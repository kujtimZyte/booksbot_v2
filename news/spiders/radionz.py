# -*- coding: utf-8 -*-
"""Parser for the RadioNZ website"""
from .common import common_parse_return, extract_link_id


def radionz_url_parse(url):
    """Parses the URL from a Radio NZ website"""
    return extract_link_id(url, lengths=[9])


def radionz_parse(response):
    """Parses the response from a Radio NZ Website"""
    link_id = radionz_url_parse(response.url)
    if link_id is None:
        return None, link_id
    return common_parse_return(response, [
        {'tag': 'div', 'meta': {'class': 'c-play-controller'}}
    ], [
        {'tag': 'div', 'meta': {'class': 'article__body'}}
    ], link_id, author_tag=[
        {'tag': 'span', 'meta': {'class': 'author-name'}}
    ])


def radionz_url_filter(_url):
    """Filters URLs in the Radio NZ domain"""
    return True
