# -*- coding: utf-8 -*-
"""Parser for the CNBC website"""
from .common import extract_link_id, common_parse


def cnbc_url_parse(url):
    """Parses the URL from a CNBC website"""
    return extract_link_id(url, lengths=[7, 8])


def cnbc_parse(response):
    """Parses the response from a CNBC Website"""
    link_id = cnbc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'div', 'meta': {'class': 'embed-container'}}
    ], [
        {'tag': 'article', 'meta': {}},
        {'tag': 'div', 'meta': {'class': 'ArticleBody-articleBody'}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def cnbc_url_filter(url):
    """Filters URLs in the CNBC domain"""
    if '/video/' in url:
        return False
    return True
