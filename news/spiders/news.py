# -*- coding: utf-8 -*-
"""The main scraper for news sites"""
import os
import json
import hashlib
import random
import re
import time
import urlparse
import scrapy
from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest
from google.cloud import storage
from langdetect import detect
from langdetect import DetectorFactory
from markdown import markdown
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
from .abc import abc_parse, abc_url_parse
from .stuff import stuff_parse
from .thehill import thehill_parse
from .washingtonpost import washingtonpost_parse
from .globalnews import globalnews_parse
from .businessinsider import businessinsider_parse
from .nzherald import nzherald_parse
from .huffingtonpost import huffingtonpost_parse
from .smh import smh_parse
from .cnbc import cnbc_parse
from .vice import vice_parse
from .nbc import nbc_parse
from .apnews import apnews_parse
from .thestar import thestar_parse
from .newsweek import newsweek_parse
from .bloomberg import bloomberg_parse
from .arstechnica import arstechnica_parse
from .cbsnews import cbsnews_parse
from .ctvnews import ctvnews_parse
from .radionz import radionz_parse
from .fox import fox_parse
from .thedailybeast import dailybeast_parse


DetectorFactory.seed = 0


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
        if not isinstance(item, basestring) and not isinstance(item, int) and not isinstance(item, float):
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


def is_item_english(article):
    """Detects whether an item is in English"""
    text = article['text']['text']
    words = text.split()
    if len(words) > 20:
        if detect(text) != 'en':
            return False
    return True


class NewsSpider(scrapy.Spider):
    """Responsible for parsing news sites"""
    name = "news"
    allowed_domains = [
        "abc.net.au"
    ]
    start_urls = [
        'https://www.abc.net.au/news/'
    ]
    http_user = NEWS_HTTP_AUTH_USER
    http_pass = ''
    storage = None
    bucket = None
    # pylint: disable=line-too-long
    parsers = {
        "abc.net.au": {
            "parser": abc_parse,
            "splash": True,
            "url_parse": abc_url_parse
        }
    }
    # pylint: enable=line-too-long


    def start_requests(self):
        random.shuffle(self.start_urls)
        requests = self.requests_for_urls(self.start_urls)
        for request in requests:
            yield request


    def parse(self, response):
        #open('output.html', 'w').write(response.text.encode('utf-8'))
        if isinstance(response, (scrapy.http.HtmlResponse, scrapy.http.TextResponse)):
            host_name = urlparse.urlsplit(response.url).hostname
            urls = extract_urls(response)
            requests = self.requests_for_urls(urls)
            for request in requests:
                yield request
            for domain in self.parsers:
                if host_name.endswith(domain):
                    article, link_id = self.parsers[domain]["parser"](response)
                    if link_id:
                        check_valid_item(response.url, article)
                        if self.write_items_to_gcs(article, link_id, domain):
                            yield {
                                'article': article,
                                'url': response.url
                            }


    def setup_gcs(self):
        """Sets up the GCS storage client"""
        write_gcp_credentials()
        if not self.storage:
            self.storage = storage.Client()
        if not self.bucket:
            self.bucket = self.storage.get_bucket(GCS_BUCKET_NAME)


    def write_items_to_gcs(self, article, link_id, host_name):
        """Writes items to GCS"""
        if not is_item_english(article):
            return False
        if not GCS_BUCKET_NAME:
            return True
        self.setup_gcs()
        article_json = json.dumps(article)
        sha256_hash = hashlib.sha224(article_json).hexdigest()
        folder = time.strftime('%Y%m%d', time.localtime(int(article.time.published_time)))
        blob_name = os.path.join(folder, host_name, link_id, sha256_hash + '.json')
        blob = self.bucket.blob(blob_name)
        if blob.exists():
            return False
        blob.upload_from_string(article_json)
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


    def requests_for_urls(self, urls):
        """Generates request objects from urls"""
        splash_args = {
            'wait': 0.5,
            'headers': {
                'User-Agent': get_user_agent()
            }
        }
        requests = []
        for url in urls:
            host_name = urlparse.urlsplit(url).hostname
            if host_name is None:
                continue
            for domain in self.parsers:
                if host_name.endswith(domain):
                    if self.parsers[domain]["splash"]:
                        new_splash_args = splash_args
                        if "cookie" in self.parsers[domain]:
                            new_splash_args["headers"]["cookie"] = self.parsers[domain]["cookie"]
                        requests.append(
                            SplashRequest(
                                url,
                                self.parse,
                                endpoint='render.html',
                                args=splash_args))
                    else:
                        requests.append(scrapy.Request(url, callback=self.parse))
        return requests
