# -*- coding: utf-8 -*-
"""The main scraper for news sites"""
import os
import json
import hashlib
import random
import time
import urlparse
import scrapy
from scrapy_splash import SplashRequest
from google.cloud import storage
from langdetect import detect
from langdetect import DetectorFactory
from .common import extract_urls
from .custom_settings import \
NEWS_HTTP_AUTH_USER, \
GCS_BUCKET_NAME, \
GCP_PROJECT, \
GCP_PRIVATE_KEY_ID, \
GCP_PRIVATE_KEY, \
GCP_CLIENT_EMAIL, \
GCP_CLIENT_ID, \
GCP_CLIENT_X509_CERT_URL
from .abc import abc_parse, abc_url_parse, abc_url_filter
from .apnews import apnews_parse, apnews_url_parse, apnews_url_filter
from .arstechnica import arstechnica_parse, arstechnica_url_parse, arstechnica_url_filter
from .bbc import bbc_parse, bbc_url_parse, bbc_url_filter
from .bloomberg import bloomberg_parse, bloomberg_url_parse, bloomberg_url_filter
from .businessinsider import businessinsider_parse, \
businessinsider_url_parse, businessinsider_url_filter
from .cbc import cbc_parse, cbc_url_parse, cbc_url_filter
from .cbsnews import cbs_parse, cbs_url_parse, cbs_url_filter
from .cnbc import cnbc_parse, cnbc_url_parse, cnbc_url_filter
from .cnn import cnn_parse, cnn_url_parse, cnn_url_filter
from .ctvnews import ctvnews_parse, ctvnews_url_parse, ctvnews_url_filter
from .fox import fox_parse, fox_url_parse, fox_url_filter
from .globalnews import globalnews_parse, globalnews_url_parse, globalnews_url_filter
from .guardian import guardian_parse, guardian_url_parse, guardian_url_filter
from .huffingtonpost import huffingtonpost_parse, huffingtonpost_url_parse, \
huffingtonpost_url_filter
from .independent import independent_parse, independent_url_parse, independent_url_filter


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
        if not isinstance(item, basestring) \
            and not isinstance(item, int) \
            and not isinstance(item, float):
            raise ValueError('Found a non string object when parsing: {}'.format(response_url))


def get_user_agent(googlebot):
    """Gets the user agent to spoof (some news require a valid one)"""
    user_agent_parts = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0)',
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/69.0.3497.100',
        'Safari/537.36'
    ]
    if googlebot:
        user_agent_parts = [
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
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
        "abc.net.au",
        "apnews.com",
        "arstechnica.com",
        "bbc.com",
        "bloomberg.com",
        "businessinsider.com",
        "cbc.ca",
        "cbsnews.com",
        "cnbc.com",
        "cnn.com",
        "ctvnews.ca",
        "foxnews.com",
        "globalnews.ca",
        "theguardian.com",
        "huffpost.com",
        "independent.co.uk"
    ]
    start_urls = [
        'https://www.abc.net.au/news/',
        'https://www.apnews.com/',
        'https://arstechnica.com/',
        'http://www.bbc.com',
        'https://www.bloomberg.com/',
        'https://www.businessinsider.com/',
        'https://www.cbc.ca/',
        'https://www.cbsnews.com/',
        'https://www.cnbc.com/',
        'https://www.cnn.com/',
        'https://www.ctvnews.ca/',
        'https://www.foxnews.com/',
        'https://globalnews.ca/',
        'https://www.theguardian.com/international',
        'https://www.huffpost.com/?country=US',
        'https://www.independent.co.uk/us'
    ]
    http_user = NEWS_HTTP_AUTH_USER
    http_pass = ''
    storage = None
    bucket = None
    parsers = {
        "abc.net.au": {
            "parser": abc_parse,
            "splash": False,
            "url_parse": abc_url_parse,
            "url_filter": abc_url_filter
        },
        "apnews.com": {
            "parser": apnews_parse,
            "splash": False,
            "url_parse": apnews_url_parse,
            "url_filter": apnews_url_filter
        },
        "arstechnica.com": {
            "parser": arstechnica_parse,
            "splash": False,
            "url_parse": arstechnica_url_parse,
            "url_filter": arstechnica_url_filter
        },
        "bbc.com": {
            "parser": bbc_parse,
            "splash": False,
            "url_parse": bbc_url_parse,
            "url_filter": bbc_url_filter
        },
        "bloomberg.com": {
            "parser": bloomberg_parse,
            "splash": False,
            "url_parse": bloomberg_url_parse,
            "url_filter": bloomberg_url_filter
        },
        "businessinsider.com": {
            "parser": businessinsider_parse,
            "splash": False,
            "url_parse": businessinsider_url_parse,
            "url_filter": businessinsider_url_filter
        },
        "cbc.ca": {
            "parser": cbc_parse,
            "splash": False,
            "url_parse": cbc_url_parse,
            "url_filter": cbc_url_filter
        },
        "cbsnews.com": {
            "parser": cbs_parse,
            "splash": False,
            "url_parse": cbs_url_parse,
            "url_filter": cbs_url_filter
        },
        "cnbc.com": {
            "parser": cnbc_parse,
            "splash": False,
            "url_parse": cnbc_url_parse,
            "url_filter": cnbc_url_filter
        },
        "cnn.com": {
            "parser": cnn_parse,
            "splash": False,
            "url_parse": cnn_url_parse,
            "url_filter": cnn_url_filter
        },
        "ctvnews.ca": {
            "parser": ctvnews_parse,
            "splash": False,
            "url_parse": ctvnews_url_parse,
            "url_filter": ctvnews_url_filter
        },
        "foxnews.com": {
            "parser": fox_parse,
            "splash": False,
            "url_parse": fox_url_parse,
            "url_filter": fox_url_filter
        },
        "globalnews.ca": {
            "parser": globalnews_parse,
            "splash": False,
            "url_parse": globalnews_url_parse,
            "url_filter": globalnews_url_filter
        },
        "guardian.com": {
            "parser": guardian_parse,
            "splash": False,
            "url_parse": guardian_url_parse,
            "url_filter": guardian_url_filter
        },
        "huffpost.com": {
            "parser": huffingtonpost_parse,
            "splash": False,
            "url_parse": huffingtonpost_url_parse,
            "url_filter": huffingtonpost_url_filter
        },
        "independent.co.uk": {
            "parser": independent_parse,
            "splash": False,
            "url_parse": independent_url_parse,
            "url_filter": independent_url_filter
        }
    }


    def start_requests(self):
        random.shuffle(self.start_urls)
        requests = self.requests_for_urls([self.start_urls[0]])
        for request in requests:
            yield request


    def parse(self, response):
        if isinstance(response, (scrapy.http.HtmlResponse, scrapy.http.TextResponse)):
            host_name = urlparse.urlsplit(response.url).hostname
            urls = extract_urls(response)
            requests = self.requests_for_urls(urls)
            for request in requests:
                yield request
            for domain in self.parsers:
                if host_name.endswith(domain):
                    article, link_id = self.parsers[domain]["parser"](response)
                    if link_id and article:
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
        folder = time.strftime('%Y%m%d', time.localtime(article['time']['published_time']))
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
                'User-Agent': get_user_agent(False)
            }
        }
        requests = []
        for url in urls:
            if 'mobile.' in url:
                url = url.replace('mobile.', '')
            host_name = urlparse.urlsplit(url).hostname
            if host_name is None:
                continue
            for domain in self.parsers:
                if host_name.endswith(domain):
                    if not self.parsers[domain]["url_filter"](url):
                        break
                    if self.parsers[domain]["splash"]:
                        requests.append(
                            SplashRequest(
                                url,
                                self.parse,
                                endpoint='render.html',
                                args=splash_args))
                    else:
                        headers = {
                            'User-Agent': get_user_agent(False),
                            'upgrade-insecure-requests': '1'
                        }
                        if 'cookie' in self.parsers[domain]:
                            headers['cookie'] = self.parsers[domain]['cookie']
                        requests.append(scrapy.Request(url, callback=self.parse, headers=headers))
        return requests
