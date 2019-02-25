# -*- coding: utf-8 -*-
"""Parser for the Ars Technica website"""
import json
from urlparse import urlparse
from bs4 import BeautifulSoup
from .article import Article, Author
from .common import extract_metadata, \
remove_common_tags, \
find_main_content, \
extract_link_id


def arstechnica_url_parse(url):
    """Parses the URL from an Ars Technica website"""
    return extract_link_id(url)


def retrieve_encoded_json(encoded_json):
    """Retrieves encoded JSON from a meta tag"""
    soup = BeautifulSoup(encoded_json, features="html.parser")
    return unicode(soup.encode(formatter=None), "utf-8")


def parse_metadata(meta_tags, article, soup):
    """Parses the meta tags from the article"""
    parsley_page = json.loads(retrieve_encoded_json(meta_tags['parsely-page']))
    article.info.title = parsley_page['title']
    article.info.url = parsley_page['link']
    article.info.description = meta_tags['og:description']
    author = Author()
    author.name = parsley_page['author']
    if 'twitter:creator' in meta_tags:
        author.twitter_url = meta_tags['twitter:creator']
    for author_social_div in soup.findAll('div', {'class': 'author-bio'}):
        for a_tag in author_social_div.findAll('a'):
            if a_tag['href'].startswith('mailto:'):
                author.email = a_tag.text
            elif a_tag['href'].startswith('/author/'):
                parsed_uri = urlparse(article.info.url)
                author.url = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri) + a_tag['href']
    article.authors.append(author)
    article.time.set_published_time(parsley_page['pub_date'])
    article.info.genre = parsley_page['section']
    for tag in parsley_page['tags']:
        article.tags.append(tag)
    article.images.thumbnail.url = parsley_page['image_url']
    if 'fb:pages' in meta_tags:
        article.publisher.facebook.page_ids = meta_tags['fb:pages'].split(',')
    article.publisher.twitter.card = meta_tags['twitter:card']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.twitter.description = meta_tags['twitter:description']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.twitter.image = meta_tags['twitter:image:src']
    article.publisher.organisation = meta_tags['og:site_name']


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'div', 'meta': {'class': 'sponsored-tile'}},
        {'tag': 'div', 'meta': {'id': 'article-footer-wrap'}},
        {'tag': 'div', 'meta': {'class': 'author-bio'}},
        {'tag': 'div', 'meta': {'class': 'share-links'}},
        {'tag': 'div', 'meta': {'id': 'social-footer'}},
        {'tag': 'aside', 'meta': {'id': 'social-left'}}
    ], soup)


def arstechnica_parse(response):
    """Parses the response from an Ars Technica Website"""
    link_id = arstechnica_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = Article()
    meta_tags = extract_metadata(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    parse_metadata(meta_tags, article, soup)
    remove_tags(soup)
    find_main_content([{'tag': 'article', 'meta': {}}], article, response, soup)
    return article.json(), link_id


def arstechnica_url_filter(url):
    """Filters URLs in the Ars Technica domain"""
    if '/author/' in url:
        return False
    return True
