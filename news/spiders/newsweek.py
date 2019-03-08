# -*- coding: utf-8 -*-
"""Parser for the News Week website"""
from .common import extract_link_id, common_parse_return


def newsweek_url_parse(url):
    """Parses the URL from a News Week website"""
    return extract_link_id(url, lengths=[4])


def newsweek_parse(response):
    """Parses the response from a News Week Website"""
    link_id = newsweek_url_parse(response.url)
    if link_id is None:
        return None, link_id
    return common_parse_return(response, [], [
        {'tag': 'div', 'meta': {'class': 'article-body'}}
    ], link_id, author_tag=[
        {'tag': 'span', 'meta': {'class': 'author'}}
    ])


def newsweek_url_filter(_url):
    """Filters URLs in the News Week domain"""
    return True
