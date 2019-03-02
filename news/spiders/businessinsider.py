# -*- coding: utf-8 -*-
"""Parser for the Business Insider website"""
from bs4 import BeautifulSoup
from .article import Article, Author
from .common import strip_query_from_url, extract_metadata, remove_common_tags, find_main_content, \
find_script_json


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
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tags = extract_metadata(response)
    if 'og:type' in meta_tags:
        if meta_tags['og:type'] != 'article':
            return None, link_id
    article = Article()
    if 'date' in meta_tags:
        article.time.set_published_time(meta_tags['date'])
    else:
        return None, link_id
    for tag in meta_tags['news_keywords'].split(','):
        article.tags.append(tag.strip())
    article.info.description = meta_tags['sailthru.description']
    article.info.title = meta_tags['title']
    article.images.thumbnail.url = meta_tags['sailthru.image.thumb']
    article.publisher.organisation = meta_tags['article:publisher']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.twitter.description = meta_tags['twitter:description']
    article.publisher.twitter.card = meta_tags['twitter:card']
    article.publisher.twitter.image = meta_tags['twitter:image']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.facebook.page_ids.append(meta_tags['fb:pages'])
    find_script_json(soup, article)
    author = Author()
    author.name = find_byline(soup)
    article.authors.append(author)
    remove_tags(soup)
    find_main_content([{'tag': 'article', 'meta': {}}], article, response, soup)
    return article.json(), link_id


def businessinsider_url_filter(_url):
    """Filters URLs in the Business Insider domain"""
    return True
