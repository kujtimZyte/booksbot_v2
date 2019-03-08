# -*- coding: utf-8 -*-
"""Parser for the CBS website"""
import hashlib
from .common import strip_query_from_url, common_parse


def cbs_url_parse(url):
    """Parses the URL from a CBS website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) != 5:
        return None
    return hashlib.sha224(url_split[-1]).hexdigest()


def cbs_parse(response):
    """Parses the response from a CBS Website"""
    link_id = cbs_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'div', 'meta': {'class': 'social'}},
        {'tag': 'div', 'meta': {'class': 'copyright'}}
    ], [
        {'tag': 'article', 'meta': {}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def cbs_url_filter(url):
    """Filters URLs in the CBS domain"""
    if '/video/' in url:
        return False
    if '/live/' in url:
        return False
    if '/pictures/' in url:
        return False
    return True
