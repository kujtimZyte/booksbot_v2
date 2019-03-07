# -*- coding: utf-8 -*-
"""Parser for the Vice website"""
from .common import extract_link_id, common_parse


def vice_url_parse(url):
    """Parses the URL from a Vice website"""
    return extract_link_id(url, lengths=[7])


def vice_parse(response):
    """Parses the response from a Vice Website"""
    link_id = vice_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'ul', 'meta': {'class': 'topics'}},
        {'tag': 'ul', 'meta': {'class': 'main-list'}},
        {'tag': 'div', 'meta': {'class': 'navbar-scrollable'}}
    ], [
        {'tag': 'article', 'meta': {}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def vice_url_filter(_url):
    """Filters URLs in the Vice domain"""
    return True
