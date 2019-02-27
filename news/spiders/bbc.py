# -*- coding: utf-8 -*-
"""Parser for the BBC website"""
from bs4 import BeautifulSoup
from .article import Article
from .common import strip_query_from_url, extract_metadata, remove_common_tags, find_main_content, \
find_script_json


def bbc_url_parse(url):
    """Parses the URL from a BBC website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) != 5:
        return None
    last_path = url_split[-1]
    last_digit = last_path.split('-')[-1]
    if not last_digit.isdigit():
        return None
    return last_digit


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'span', 'meta': {'class': 'off-screen'}},
        {'tag': 'div', 'meta': {'class': 'player-with-placeholder__caption'}},
        {'tag': 'div', 'meta': {'class': 'teads-ui-components-adchoices'}},
        {'tag': 'div', 'meta': {'class': 'teads-ui-components-label'}},
        {'tag': 'div', 'meta': {'class': 'teads-player'}},
        {'tag': 'div', 'meta': {'class': 'teads-ui-components-credits'}},
        {'tag': 'div', 'meta': {'class': 'share-tools--event-tag'}},
        {'tag': 'div', 'meta': {'class': 'features-and-analysis'}}
    ], soup)


def bbc_parse(response):
    """Parses the response from a BBC Website"""
    link_id = bbc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = Article()
    soup = BeautifulSoup(response.text, 'html.parser')
    for li_tag in soup.findAll('li', {'class': 'tags-list__tags'}):
        article.tags.append(str(li_tag.text))
    find_script_json(soup, article)
    meta_tags = extract_metadata(response)
    if 'twitter:title' not in meta_tags:
        return None, link_id
    article.info.description = meta_tags['og:description']
    article.info.genre = meta_tags['article:section']
    article.images.thumbnail.alt = meta_tags['og:image:alt']
    for page_id in meta_tags['fb:pages'].split(','):
        article.publisher.facebook.page_ids.append(page_id)
    article.publisher.twitter.card = meta_tags['twitter:card']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.twitter.description = meta_tags['twitter:description']
    article.publisher.twitter.image = meta_tags['twitter:image:src']
    article.publisher.twitter.image_alt = meta_tags['twitter:image:alt']
    article.publisher.twitter.domain = meta_tags['twitter:domain']
    remove_tags(soup)
    find_main_content([{'tag': 'div', 'meta': {'class': 'story-body'}}], article, response, soup)
    return article.json(), link_id


def bbc_url_filter(url):
    """Filters URLs in the BBC domain"""
    if '/vietnamese/' in url:
        return False
    if '/uzbek/' in url:
        return False
    return True
