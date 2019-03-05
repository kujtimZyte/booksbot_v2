# -*- coding: utf-8 -*-
"""Parser for the Business Insider website"""
from bs4 import BeautifulSoup
from .article import Article, Author
from .common import strip_query_from_url, extract_metadata, remove_common_tags, find_main_content, \
find_script_json, common_parse


def businessinsider_url_parse(url):
    """Parses the URL from a Business Insider website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) != 4:
        return None
    last_path = url_split[-1]
    return last_path


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'div', 'meta': {'class': 'byline-publication-source'}},
        {'tag': 'section', 'meta': {'class': 'post-content-bottom '}},
        {'tag': 'section', 'meta': {'class': 'popular-video'}},
        {'tag': 'section', 'meta': {'class': 'post-content-more '}},
        {'tag': 'p', 'meta': {'class': 'piano-freemium'}},
        {'tag': 'ul', 'meta': {'class': 'read-more-links'}}
    ], soup)


def find_byline(soup):
    """Finds the author byline"""
    html_tag = soup.find('span', {'class': 'byline-author-name'})
    if html_tag is None:
        html_tag = soup.find('a', {'class': 'byline-author-name'})
    return html_tag.text


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
