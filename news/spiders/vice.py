# -*- coding: utf-8 -*-
"""Parser for the Vice website"""
from .common import extract_link_id, common_parse_return


def vice_url_parse(url):
    """Parses the URL from a Vice website"""
    return extract_link_id(url, lengths=[7])


def vice_parse(response):
    """Parses the response from a Vice Website"""
    link_id = vice_url_parse(response.url)
    if link_id is None:
        return None, link_id
    return common_parse_return(response, [
        {'tag': 'ul', 'meta': {'class': 'topics'}},
        {'tag': 'ul', 'meta': {'class': 'main-list'}},
        {'tag': 'div', 'meta': {'class': 'navbar-scrollable'}}
    ], [
        {'tag': 'article', 'meta': {}}
    ], link_id)


def vice_url_filter(_url):
    """Filters URLs in the Vice domain"""
    return True
