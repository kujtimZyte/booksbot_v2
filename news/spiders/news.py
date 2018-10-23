# -*- coding: utf-8 -*-
"""The main scraper for news sites"""
import os
import json
import hashlib
import scrapy
import urlparse
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
    allowed_domains = [
        "cnn.com",
        "reuters.com"
    ]
    start_urls = [
        'http://www.cnn.com',
        'https://www.reuters.com/'
    ]
    http_user = NEWS_HTTP_AUTH_USER
    http_pass = ''
    storage = None
    bucket = None
    parsers = {
        "cnn.com": cnn_parse
    }

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait': 0.5})

    def parse(self, response):
        host_name = urlparse.urlsplit(response.url).hostname
        for domain in self.parsers:
            if host_name.endswith(domain):
                urls, items = self.parsers[domain](response)
                for url in urls:
                    yield scrapy.Request(response.urljoin(url), callback=self.parse)
                if items:
                    self.write_items_to_gcs(items)
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
            return
        self.setup_gcs()
        item_json = json.dumps(items)
        sha256_hash = hashlib.sha224(item_json).hexdigest()
        blob_name = sha256_hash + '.json'
        blob = self.bucket.blob(blob_name)
        if blob.exists():
            return
        blob.upload_from_string(item_json)
