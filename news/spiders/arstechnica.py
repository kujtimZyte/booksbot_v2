# -*- coding: utf-8 -*-
"""Parser for the Ars Technica website"""
from .common import extract_link_id, common_parse_return


def arstechnica_url_parse(url):
    """Parses the URL from an Ars Technica website"""
    return extract_link_id(url)


def arstechnica_parse(response):
    """Parses the response from an Ars Technica Website"""
    link_id = arstechnica_url_parse(response.url)
    return common_parse_return(response, [
        {'tag': 'div', 'meta': {'class': 'sponsored-tile'}},
        {'tag': 'div', 'meta': {'id': 'article-footer-wrap'}},
        {'tag': 'div', 'meta': {'class': 'author-bio'}},
        {'tag': 'div', 'meta': {'class': 'share-links'}},
        {'tag': 'div', 'meta': {'id': 'social-footer'}},
        {'tag': 'aside', 'meta': {'id': 'social-left'}}
    ], [
        {'tag': 'article', 'meta': {}}
    ], link_id)


def arstechnica_url_filter(url):
    """Filters URLs in the Ars Technica domain"""
    if '/author/' in url:
        return False
    return True
