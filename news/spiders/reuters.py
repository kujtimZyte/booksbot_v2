# -*- coding: utf-8 -*-
"""Parser for the Reuters website"""
from .common import common_parse_return, extract_link_id


def reuters_url_parse(url):
    """Parses the URL from a Reuters website"""
    return extract_link_id(url, lengths=[6])


def reuters_parse(response):
    """Parses the response from a Reuters Website"""
    link_id = reuters_url_parse(response.url)
    if link_id is None:
        return None, link_id
    return common_parse_return(response, [
        {'tag': 'div', 'meta': {'class': 'DPSlot_container'}},
        {'tag': 'div', 'meta': {'class': 'StandardArticleBody_trustBadgeContainer'}},
        {'tag': 'div', 'meta': {'class': 'SocialTool_container'}},
        {'tag': 'div', 'meta': {'class': 'ArticleHeader_channel'}}
    ], [
        {'tag': 'div', 'meta': {'class': 'ArticlePage_container'}}
    ], link_id)


def reuters_url_filter(_url):
    """Filters URLs in the Reuters domain"""
    return True
