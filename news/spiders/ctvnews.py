# -*- coding: utf-8 -*-
"""Parser for the CTVNews website"""
from .common import extract_link_id, common_parse


def ctvnews_url_parse(url):
    """Parses the URL from a CTVNews website"""
    return extract_link_id(url, lengths=[5])


def ctvnews_parse(response):
    """Parses the response from a CTVNews Website"""
    link_id = ctvnews_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = common_parse(response, [
        {'tag': 'div', 'meta': {'class': 'boxAd'}},
        {'tag': 'div', 'meta': {'class': 'connect'}},
        {'tag': 'div', 'meta': {'class': 'twoColumns'}},
        {'tag': 'div', 'meta': {'class': 'teaser'}},
        {'tag': 'div', 'meta': {'class': 'videoPromoList'}},
        {'tag': 'div', 'meta': {'class': 'form-submit'}},
        {'tag': 'div', 'meta': {'class': 'StoryShareBottom'}},
        {'tag': 'article', 'meta': {'class': 'superTeaser'}},
        {'tag': 'div', 'meta': {'class': 'right-c'}},
        {'tag': 'div', 'meta': {'class': 'related'}},
        {'tag': 'div', 'meta': {'class': 'gig-bar-container'}}
    ], [
        {'tag': 'div', 'meta': {'class': 'article'}}
    ])
    if article is None:
        return None, link_id
    return article.json(), link_id


def ctvnews_url_filter(url):
    """Filters URLs in the CTVNews domain"""
    if '/newsletters/' in url:
        return False
    return True
