# -*- coding: utf-8 -*-
"""Parser for the Global News website"""
from .common import extract_link_id, common_parse


def globalnews_url_parse(url):
    """Parses the URL from a Global News website"""
    return extract_link_id(url, lengths=[6])


def globalnews_parse(response):
    """Parses the response from a Global News Website"""
    link_id = globalnews_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'form', 'meta': {'class': 'newsletter-signup__form'}},
        {'tag': 'strong', 'meta': {}},
        {'tag': 'div', 'meta': {'class': 'story-ad-read-more'}},
        {'tag': 'div', 'meta': {'class': 'carousel'}}
    ], [
        {'tag': 'span', 'meta': {'class': 'gnca-article-story-txt'}}
    ])
    return article.json(), link_id


def globalnews_url_filter(_url):
    """Filters URLs in the Global News domain"""
    return True
