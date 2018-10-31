# -*- coding: utf-8 -*-
"""The main scraper for news sites"""
import os
import json
import hashlib
import urlparse
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
from .cnn import cnn_parse
from .reuters import reuters_parse
from .guardian import guardian_parse
from .bbc import bbc_parse
from .common import extract_urls
from .cbc import cbc_parse
from .independent import independent_parse
from .theverge import the_verge_parse
from .nytimes import nytimes_parse
from .abc import abc_parse
from .stuff import stuff_parse
from .thehill import thehill_parse
from .washingtonpost import washingtonpost_parse


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


def check_valid_item(response_url, item):
    """
    Checks whether an item to post to the scraping hub is valid
    E.g. it must be either, dictionaries, lists or strings
    """
    if isinstance(item, dict):
        for key in item:
            check_valid_item(response_url, key)
            sub_item = item[key]
            check_valid_item(response_url, sub_item)
    elif isinstance(item, list):
        for list_item in item:
            check_valid_item(response_url, list_item)
    else:
        if not isinstance(item, basestring):
            raise ValueError('Found a non string object when parsing: {}'.format(response_url))


def get_user_agent():
    """Gets the user agent to spoof (some news require a valid one)"""
    user_agent_parts = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0)',
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/69.0.3497.100',
        'Safari/537.36'
    ]
    return ' '.join(user_agent_parts)


class NewsSpider(scrapy.Spider):
    """Responsible for parsing news sites"""
    name = "news"
    allowed_domains = [
        "cnn.com",
        "reuters.com",
        "theguardian.com",
        "bbc.com",
        "cbc.ca",
        "independent.co.uk",
        "theverge.com",
        "nytimes.com",
        "abc.net.au",
        "stuff.co.nz",
        "thehill.com",
        "washingtonpost.com"
    ]
    start_urls = [
        'http://www.cnn.com',
        'https://www.reuters.com/',
        'https://www.theguardian.com/international?INTCMP=CE_INT',
        'http://www.bbc.com',
        'https://www.cbc.ca/',
        'https://www.independent.co.uk/us',
        'https://www.theverge.com/',
        'https://www.nytimes.com/',
        'https://www.abc.net.au/news/',
        'https://www.stuff.co.nz/',
        'https://thehill.com/',
        'https://www.washingtonpost.com/'
    ]
    http_user = NEWS_HTTP_AUTH_USER
    http_pass = ''
    storage = None
    bucket = None
    parsers = {
        "cnn.com": cnn_parse,
        "reuters.com": reuters_parse,
        "theguardian.com": guardian_parse,
        "bbc.com": bbc_parse,
        "cbc.ca": cbc_parse,
        "independent.co.uk": independent_parse,
        "theverge.com": the_verge_parse,
        "nytimes.com": nytimes_parse,
        "abc.net.au": abc_parse,
        "stuff.co.nz": stuff_parse,
        "thehill.com": thehill_parse,
        "washingtonpost.com": washingtonpost_parse
    }


    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={
                'wait': 0.5,
                'headers': {
                    'User-Agent': get_user_agent()
                }
            })


    def parse(self, response):
        #open('output.html', 'w').write(response.text.encode('utf-8'))
        if isinstance(response, (scrapy.http.HtmlResponse, scrapy.http.TextResponse)):
            host_name = urlparse.urlsplit(response.url).hostname
            urls = extract_urls(response)
            for url in urls:
                if self.is_url_allowed(url):
                    yield scrapy.Request(response.urljoin(url), callback=self.parse)
            for domain in self.parsers:
                if host_name.endswith(domain):
                    items = self.parsers[domain](response)
                    if items:
                        check_valid_item(response.url, items)
                        if self.write_items_to_gcs(items):
                            yield {
                                'items': items,
                                'url': response.url
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
            return True
        self.setup_gcs()
        item_json = json.dumps(items)
        sha256_hash = hashlib.sha224(item_json).hexdigest()
        blob_name = sha256_hash + '.json'
        blob = self.bucket.blob(blob_name)
        if blob.exists():
            return False
        blob.upload_from_string(item_json)
        return True

    def is_url_allowed(self, url):
        """Checks whether the URL is in a defined hostname"""
        host_name = urlparse.urlsplit(url).hostname
        if host_name is None:
            return False
        for allowed_domain in self.allowed_domains:
            if host_name.endswith(allowed_domain):
                return True
        return False
