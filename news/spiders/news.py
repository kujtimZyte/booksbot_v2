# -*- coding: utf-8 -*-
"""The main scraper for news sites"""
import os
import json
import hashlib
import urlparse
import scrapy
from scrapy_splash import SplashRequest
from google.cloud import storage
from langdetect import detect
from langdetect import DetectorFactory
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


def is_item_english(items):
    """Detects whether an item is in English"""
    for item in items:
        for paragraph in item['articleBody']:
            text = paragraph['text']
            words = text.split()
            # Short sentences can be confused easily
            if len(words) > 10:
                if detect(text) != 'en':
                    return False
    return True

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
        "washingtonpost.com",
        "globalnews.ca",
        "businessinsider.com",
        "nzherald.co.nz",
        "huffingtonpost.com",
        "smh.com.au",
        "cnbc.com",
        "vice.com",
        "nbcnews.com",
        "apnews.com",
        "thestar.com",
        "newsweek.com",
        "bloomberg.com",
        "arstechnica.com"
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
        'https://www.washingtonpost.com/',
        'https://globalnews.ca/',
        'https://www.businessinsider.com/',
        'https://www.nzherald.co.nz/',
        'https://www.huffingtonpost.com/',
        'https://www.smh.com.au/',
        'https://www.cnbc.com',
        'https://www.vice.com/en_us',
        'https://motherboard.vice.com/en_us',
        'https://www.nbcnews.com/',
        'https://www.apnews.com/',
        'https://www.thestar.com',
        'https://www.newsweek.com/',
        'https://www.bloomberg.com/',
        'https://arstechnica.com/'
    ]
    http_user = NEWS_HTTP_AUTH_USER
    http_pass = ''
    storage = None
    bucket = None
    # pylint: disable=line-too-long
    parsers = {
        "cnn.com": {
            "parser": cnn_parse,
            "splash": True
        },
        "reuters.com": {
            "parser": reuters_parse,
            "splash": True
        },
        "theguardian.com": {
            "parser": guardian_parse,
            "splash": True
        },
        "bbc.com": {
            "parser": bbc_parse,
            "splash": True
        },
        "cbc.ca": {
            "parser": cbc_parse,
            "splash": True
        },
        "independent.co.uk": {
            "parser": independent_parse,
            "splash": True
        },
        "theverge.com": {
            "parser": the_verge_parse,
            "splash": True
        },
        "nytimes.com": {
            "parser": nytimes_parse,
            "splash": True
        },
        "abc.net.au": {
            "parser": abc_parse,
            "splash": True
        },
        "stuff.co.nz": {
            "parser": stuff_parse,
            "splash": True
        },
        "thehill.com": {
            "parser": thehill_parse,
            "splash": True
        },
        "washingtonpost.com": {
            "parser": washingtonpost_parse,
            "splash": True
        },
        "globalnews.ca": {
            "parser": globalnews_parse,
            "splash": True
        },
        "businessinsider.com": {
            "parser": businessinsider_parse,
            "splash": False
        },
        "nzherald.co.nz": {
            "parser": nzherald_parse,
            "splash": True
        },
        "huffingtonpost.com": {
            "parser": huffingtonpost_parse,
            "splash": True
        },
        "smh.com.au": {
            "parser": smh_parse,
            "splash": True
        },
        "cnbc.com": {
            "parser": cnbc_parse,
            "splash": False
        },
        "vice.com": {
            "parser": vice_parse,
            "splash": False
        },
        "nbcnews.com": {
            "parser": nbc_parse,
            "splash": True
        },
        "apnews.com": {
            "parser": apnews_parse,
            "splash": True
        },
        "thestar.com": {
            "parser": thestar_parse,
            "splash": True
        },
        "newsweek.com": {
            "parser": newsweek_parse,
            "splash": True
        },
        "bloomberg.com": {
            "parser": bloomberg_parse,
            "splash": True,
            "cookie": "__pat=-18000000; _px2=eyJ1IjoiZmM5ZDA1NzAtZTZkZC0xMWU4LTkxMDgtYzVkZDRlYTMwZDFkIiwidiI6IjEwMWFhZjYwLWQ1N2UtMTFlOC05ZGRkLTE1MTBiYWUyY2ViYSIsInQiOjE1NDIwNzA0Nzg5OTQsImgiOiI1ZGY3NmUwOWFjZWFhYzM2M2U2OGZhNWQ2MGE4ZmI0NWVhYTM0MTZjNTRjZjc2MzMxZjRmNTU3NzgxMTY0ZTNlIn0=; _litra_ses.2a03=*;"
        },
        "arstechnica.com": {
            "parser": arstechnica_parse,
            "splash": True
        }
    }
    # pylint: enable=line-too-long


    def start_requests(self):
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
                    items = self.parsers[domain]["parser"](response)
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
        if not is_item_english(items):
            return False
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
