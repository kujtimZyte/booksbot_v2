# -*- coding: utf-8 -*-
"""Parser for the Huffington Post website"""
from .common import extract_link_id, common_parse


def huffingtonpost_url_parse(url):
    """Parses the URL from a Huffington Post website"""
    return extract_link_id(url, lengths=[5])


def huffingtonpost_parse(response):
    """Parses the response from a Huffington Post Website"""
    link_id = huffingtonpost_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'div', 'meta': {'class': 'related-articles'}},
        {'tag': 'section', 'meta': {'class': 'app-download-interstitial'}}
    ], [
        {'tag': 'div', 'meta': {'class': 'entry__text'}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def huffingtonpost_url_filter(_url):
    """Filters URLs in the Huffington Post domain"""
    return True
