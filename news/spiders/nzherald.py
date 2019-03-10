# -*- coding: utf-8 -*-
"""Parser for the NZ Herald website"""
import urlparse
from .common import common_parse_return


def nzherald_url_parse(url):
    """Parses the URL from a NZ Herald website"""
    parsed = urlparse.urlparse(url)
    params = urlparse.parse_qs(parsed.query)
    if 'objectid' in params and 'c_id' in params:
        return params['c_id'] + params['objectid']
    return None


def nzherald_parse(response):
    """Parses the response from a NZ Herald Website"""
    link_id = nzherald_url_parse(response.url)
    if link_id is None:
        return None, link_id
    return common_parse_return(response, [
        {'tag': 'div', 'meta': {'class': 'pb-f-utilities-sharebar'}},
        {'tag': 'div', 'meta': {'class': 'pb-f-global-blank-html'}},
        {'tag': 'div', 'meta': {'class': 'timeline-container'}},
        {'tag': 'div', 'meta': {'class': 'score-line'}},
        {'tag': 'div', 'meta': {'class': 'opta-matchstats'}},
        {'tag': 'div', 'meta': {'class': 'timeline-graph'}},
        {'tag': 'div', 'meta': {'class': 'clock'}},
        {'tag': 'div', 'meta': {'class': 'opta-timeline'}},
        {'tag': 'div', 'meta': {'class': 'pb-f-article-related-articles'}},
        {'tag': 'div', 'meta': {'class': 'ad-container'}},
        {'tag': 'div', 'meta': {'class': 'byline-shares'}},
        {'tag': 'div', 'meta': {'class': 'pb-f-article-slimline-byline'}},
        {'tag': 'article', 'meta': {'class': 'story-preview-wrapper'}},
        {'tag': 'div', 'meta': {'class': 'story-category'}},
        {'tag': 'div', 'meta': {'class': 'header-label'}}
    ], [
        {'tag': 'article', 'meta': {'class': 'article-main'}}
    ], link_id, author_tag=[
        {'tag': 'span', 'meta': {'class': 'author-title'}}
    ])


def nzherald_url_filter(_url):
    """Filters URLs in the NZ Herald domain"""
    return True
