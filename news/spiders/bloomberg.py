# -*- coding: utf-8 -*-
"""Parser for the Bloomberg website"""
import hashlib
import json
from bs4 import BeautifulSoup
import html2text
from .article import Article, Author
from .common import strip_query_from_url, extract_metadata, find_images, remove_common_tags, find_audio


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
    for script_tag in soup.findAll('script', {'type': 'application/ld+json'}):
        script_json = json.loads(script_tag.text.replace('\\/', '/'))
        for author in script_json['author']:
            article_author = Author()
            article_author.name = author['name']
            article.authors.append(article_author)
        article.time.set_modified_time(script_json['dateModified'])
        article.publisher.organisation = script_json['publisher']['name']
        article.info.url = script_json['mainEntityOfPage']
        article.images.thumbnail.url = script_json['image']['url']
        article.images.thumbnail.width = script_json['image']['width']
        article.images.thumbnail.height = script_json['image']['height']
        article.time.set_published_time(script_json['datePublished'])
        article.info.title = script_json['headline']
        article.info.description = script_json['description']
    find_audio(soup, article)
    remove_tags(soup)
    main_content_div = soup.find('article', {'data-type': 'article'})
    if not main_content_div:
        raise ValueError('Could not find the main content div: {}'.format(response.url))
    find_images(main_content_div, article, response)
    article.text.set_markdown_text(html2text.html2text(unicode(main_content_div)))
    return article.json(), link_id


def bloomberg_url_filter(_url):
    """Filters URLs in the Bloomberg domain"""
    return True
