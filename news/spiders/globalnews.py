# -*- coding: utf-8 -*-
"""Parser for the Global News website"""
import json
from .article import Image
from .common import extract_link_id, find_common_response_data, remove_common_tags, find_main_content


def globalnews_url_parse(url):
    """Parses the URL from a Global News website"""
    return extract_link_id(url, lengths=[6])


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'form', 'meta': {'class': 'newsletter-signup__form'}},
        {'tag': 'strong', 'meta': {}},
        {'tag': 'div', 'meta': {'class': 'story-ad-read-more'}},
        {'tag': 'div', 'meta': {'class': 'carousel'}}
    ], soup)


def globalnews_parse(response):
    """Parses the response from a Global News Website"""
    link_id = globalnews_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup, _, article = find_common_response_data(response)
    remove_tags(soup)
    find_main_content(
        [{'tag': 'span', 'meta': {'class': 'gnca-article-story-txt'}}], article, response, soup)
    return article.json(), link_id


def globalnews_url_filter(_url):
    """Filters URLs in the Global News domain"""
    return True
