# -*- coding: utf-8 -*-
"""The main scraper for news sites"""
import os
import json
import hashlib
import scrapy
from scrapy_splash import SplashRequest
from google.cloud import storage
from .custom_settings import \
NEWS_HTTP_AUTH_USER, \
GCS_BUCKET_NAME, \
GCP_PROJECT, \
GCP_PRIVATE_KEY_ID, \
GCP_PRIVATE_KEY, \
GCP_CLIENT_EMAIL, \
GCP_CLIENT_ID, \
GCP_CLIENT_X509_CERT_URL


def is_bad_img(img):
    """
    Checks whether an image is worthy of inclusion
    """
    bad_imgs = [
        'outbrain',
        'data:image',
        'cnnnext'
    ]
    for bad_img in bad_imgs:
        if bad_img in img:
            return True
    return False


def extract_paragraphs(itemprop_element):
    """
    Extract the paragraphs from an article element
    """
    removeable_paragraphs = [
        u'Paid Content',
        u'More from CNN',
        u'Read More',
        u'Recommended by',
        u'READ MORE:'
    ]
    paragraphs = []
    for paragraph_div in itemprop_element.css(
            'div.zn-body__paragraph'):
        paragraph_list = []
        for paragraph in paragraph_div.xpath(".//text()"):
            stripped_paragraph = paragraph.extract().strip()
            if stripped_paragraph and \
                stripped_paragraph not in removeable_paragraphs:
                paragraph_list.append({
                    'text': stripped_paragraph
                })
        for link in paragraph_div.css('a'):
            text = link.xpath(
                'text()').extract_first().strip()
            href = link.xpath(
                '@href').extract_first().strip()
            for paragraph_text in paragraph_list:
                if paragraph_text['text'] == text:
                    paragraph_text['link'] = href
        if paragraph_list:
            paragraphs.append(paragraph_list)
    return paragraphs


def write_gcp_credentials():
    """
    Writes the appropriate GCP credentials to a file
    """
    gcs_env_key = 'GOOGLE_APPLICATION_CREDENTIALS'
    if gcs_env_key in os.environ:
        return
    current_script_directory = os.path.dirname(os.path.realpath(__file__))
    credentials_filepath = os.path.join(current_script_directory, 'gcp-credentials.json')
    if os.path.exists(credentials_filepath):
        return
    credentials = {
        "type": "service_account",
        "project_id": GCP_PROJECT,
        "private_key_id": GCP_PRIVATE_KEY_ID,
        "private_key": GCP_PRIVATE_KEY,
        "client_email": GCP_CLIENT_EMAIL,
        "client_id": GCP_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": GCP_CLIENT_X509_CERT_URL
    }
    json_credentials = json.dumps(credentials)
    open(credentials_filepath, 'w').write(json_credentials)
    os.environ[gcs_env_key] = credentials_filepath


class NewsSpider(scrapy.Spider):
    """Responsible for parsing news sites"""
    name = "news"
    allowed_domains = ["cnn.com"]
    start_urls = [
        'http://www.cnn.com'
    ]
    http_user = NEWS_HTTP_AUTH_USER
    http_pass = ''
    storage = None
    bucket = None

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait': 0.5})

    def parse(self, response):
        for article in response.xpath("//article"):
            for url in article.xpath("//a/@href").extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
        for li_element in response.css("li.ob-dynamic-rec-container"):
            for url in li_element.xpath("//a/@href").extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
        items = []
        for article in response.css("article"):
            item = {}
            for itemprop in article.xpath('.//*[@itemprop]'):
                property_content = itemprop.xpath("@content").extract_first()
                property_name = itemprop.xpath("@itemprop").extract_first()
                if property_content is not None:
                    item[property_name] = property_content
                else:
                    if property_name == u'articleBody':
                        item[property_name] = extract_paragraphs(itemprop)
            imgs = []
            for img in article.css('img::attr(src)').extract():
                full_img = response.urljoin(img)
                if not is_bad_img(full_img) and full_img not in imgs:
                    imgs.append(full_img)
            if item:
                item['imgs'] = imgs
                items.append(item)
        if items:
            self.write_items_to_gcs(items)
            yield {
                'items': items
            }


    def setup_gcs(self):
        """Sets up the GCS storage client"""
        write_gcp_credentials()
        if not self.storage:
            self.storage = storage.Client()
        if not self.bucket:
            self.bucket = self.storage.get_bucket(GCS_BUCKET_NAME)


    def write_items_to_gcs(self, items):
        """Writes items to GCS"""
        if not GCS_BUCKET_NAME:
            return
        self.setup_gcs()
        item_json = json.dumps(items)
        sha256_hash = hashlib.sha224(item_json).hexdigest()
        blob_name = sha256_hash + '.json'
        blob = self.bucket.blob(blob_name)
        if blob.exists():
            return
        blob.upload_from_string(item_json)
