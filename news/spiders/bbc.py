# -*- coding: utf-8 -*-
"""Parser for the BBC website"""
from ast import literal_eval
import hashlib
import json
from bs4 import BeautifulSoup
import html2text
from .article import Article
from .common import strip_query_from_url, extract_metadata, remove_common_tags, find_images


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
    for script_tag in soup.findAll('script', {'type': 'application/ld+json'}):
        script_json = json.loads(script_tag.text.replace('\\/', '/'))
        article.time.set_modified_time(script_json['dateModified'])
        article.publisher.organisation = script_json['publisher']['name']
        article.info.url = script_json['url']
        article.images.thumbnail.url = script_json['image']['url']
        article.images.thumbnail.width = script_json['image']['width']
        article.images.thumbnail.height = script_json['image']['height']
        article.time.set_published_time(script_json['datePublished'])
        article.info.title = script_json['headline']
    meta_tags = extract_metadata(response)
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
    main_content_div = soup.find('div', {'class': 'story-body'})
    if not main_content_div:
        raise ValueError('Could not find the main content div: {}'.format(response.url))
    find_images(soup, article, response)
    article.text.set_markdown_text(html2text.html2text(unicode(main_content_div)))
    #print article.text.markdown_text
    return article.json(), link_id


def bbc_url_filter(_url):
    """Filters URLs in the BBC domain"""
    return True
