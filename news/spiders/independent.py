# -*- coding: utf-8 -*-
"""Parser for the Independent website"""
from .common import extract_link_id, common_parse


def independent_url_parse(url):
    """Parses the URL from a Independent website"""
    return extract_link_id(url, lengths=[7])


def independent_parse(response):
    """Parses the response from a Independent Website"""
    link_id = independent_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'div', 'meta': {'class': 'pagination-wrapper'}},
        {'tag': 'aside', 'meta': {'class': 'related-video'}}
    ], [
        {'tag': 'div', 'meta': {'class': 'body-content'}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def independent_url_filter(_url):
    """Filters URLs in the Independent domain"""
    return True
