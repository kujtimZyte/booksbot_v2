# -*- coding: utf-8 -*-
"""Parser for the Guardian website"""
from .common import extract_link_id, common_parse


def guardian_url_parse(url):
    """Parses the URL from a Guardian website"""
    return extract_link_id(url, lengths=[8, 9])


def guardian_parse(response):
    """Parses the response from a Guardian Website"""
    link_id = guardian_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'div', 'meta': {'class': 'submeta__syndication'}},
        {'tag': 'div', 'meta': {'class': 'submeta__share'}},
        {'tag': 'div', 'meta': {'class': 'after-article'}},
        {'tag': 'div', 'meta': {'class': 'submeta__section-labels'}},
        {'tag': 'ul', 'meta': {'class': 'submeta__links'}},
        {'tag': 'span', 'meta': {'class': 'submeta__label'}},
        {'tag': 'div', 'meta': {'class': 'rich-link__read-more'}}
    ], [
        {'tag': 'div', 'meta': {'class': 'content__article-body'}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def guardian_url_filter(_url):
    """Filters URLs in the Guardian domain"""
    return True
