# -*- coding: utf-8 -*-
"""Parser for the Business Insider website"""
from .common import strip_query_from_url, common_parse


def businessinsider_url_parse(url):
    """Parses the URL from a Business Insider website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) != 4:
        return None
    last_path = url_split[-1]
    return last_path


def businessinsider_parse(response):
    """Parses the response from a Business Insider Website"""
    link_id = businessinsider_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'div', 'meta': {'class': 'byline-publication-source'}},
        {'tag': 'section', 'meta': {'class': 'post-content-bottom '}},
        {'tag': 'section', 'meta': {'class': 'popular-video'}},
        {'tag': 'section', 'meta': {'class': 'post-content-more '}},
        {'tag': 'p', 'meta': {'class': 'piano-freemium'}},
        {'tag': 'ul', 'meta': {'class': 'read-more-links'}}
    ], [
        {'tag': 'article', 'meta': {}}
    ], author_tag=[
        {'tag': 'span', 'meta': {'class': 'byline-author-name'}},
        {'tag': 'a', 'meta': {'class': 'byline-author-name'}}
    ])
    if not article:
        return None, link_id
    return article.json(), link_id


def businessinsider_url_filter(_url):
    """Filters URLs in the Business Insider domain"""
    return True
