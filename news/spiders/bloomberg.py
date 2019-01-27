# -*- coding: utf-8 -*-
"""Parser for the Bloomberg website"""
import hashlib
from bs4 import BeautifulSoup
from .article import Article
from .common import strip_query_from_url, \
extract_metadata, \
remove_common_tags, \
find_audio, \
find_main_content, \
find_script_json


def bloomberg_url_parse(url):
    """Parses the URL from a Bloomberg website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) != 7:
        return None
    last_path = url_split[-1]
    return hashlib.sha224(last_path).hexdigest()


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'div', 'meta': {'class': 'page-ad'}},
        {'tag': 'div', 'meta': {'class': 'rotation-item'}},
        {'tag': 'div', 'meta': {'class': 'mini-player'}},
        {'tag': 'div', 'meta': {'class': 'terminal-tout-v2'}},
        {'tag': 'div', 'meta': {'class': 'secure-tip-tout-v2'}},
        {'tag': 'aside', 'meta': {'class': 'left-column'}},
        {'tag': 'div', 'meta': {'class': 'navi-breaking-news'}},
        {'tag': 'a', 'meta': {'class': 'zipr-recirc__story'}},
        {'tag': 'div', 'meta': {'class': 'zipr-recirc'}}
    ], soup)


def bloomberg_parse(response):
    """Parses the response from a Bloomberg website"""
    link_id = bloomberg_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = Article()
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tags = extract_metadata(response)
    for tag in meta_tags['parsely-tags'].split(','):
        article.tags.append(tag)
    article.publisher.twitter.card = meta_tags['twitter:card']
    article.publisher.twitter.description = meta_tags['twitter:description']
    article.publisher.twitter.image = meta_tags['twitter:image']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.facebook.status = meta_tags['fb:status']
    find_script_json(soup, article)
    find_audio(soup, article)
    remove_tags(soup)
    find_main_content(
        [{'tag': 'article', 'meta': {'data-type': 'article'}}],
        article,
        response,
        soup)
    return article.json(), link_id


def bloomberg_url_filter(_url):
    """Filters URLs in the Bloomberg domain"""
    return True
