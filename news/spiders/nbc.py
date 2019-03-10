# -*- coding: utf-8 -*-
"""Parser for the NBC website"""
from .common import extract_link_id, common_parse


def nbc_url_parse(url):
    """Parses the URL from a NBC website"""
    return extract_link_id(url, lengths=[6])


def nbc_parse(response):
    """Parses the response from a NBC Website"""
    link_id = nbc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [], [
        {'tag': 'article', 'meta': {'class': 'articleBody'}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def nbc_url_filter(url):
    """Filters URLs in the NBC domain"""
    if '/video/' in url:
        return False
    return True
