# -*- coding: utf-8 -*-
"""Parser for the Huffington Post website"""
from .common import extract_link_id, common_parse_return


def huffingtonpost_url_parse(url):
    """Parses the URL from a Huffington Post website"""
    return extract_link_id(url, lengths=[5])


def huffingtonpost_parse(response):
    """Parses the response from a Huffington Post Website"""
    link_id = huffingtonpost_url_parse(response.url)
    if link_id is None:
        return None, link_id
    return common_parse_return(response, [
        {'tag': 'div', 'meta': {'class': 'related-articles'}},
        {'tag': 'section', 'meta': {'class': 'app-download-interstitial'}},
        {'tag': 'section', 'meta': {'class': 'entry__tags'}},
        {'tag': 'div', 'meta': {'class': 'social-buttons'}}
    ], [
        {'tag': 'div', 'meta': {'class': 'entry__text'}},
        {'tag': 'article', 'meta': {'class': 'entry__content'}}
    ], link_id)


def huffingtonpost_url_filter(_url):
    """Filters URLs in the Huffington Post domain"""
    return True
