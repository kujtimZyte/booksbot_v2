# -*- coding: utf-8 -*-
"""Parser for the CNBC website"""
import hashlib
from .common import strip_query_from_url, remove_common_tags, find_main_content, \
find_script_json, common_response_data, extract_link_id


def cnbc_url_parse(url):
    """Parses the URL from a CNBC website"""
    return extract_link_id(url)


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([], soup)


def cnbc_parse(response):
    """Parses the response from a CNBC Website"""
    link_id = cnbc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup, meta_tags, article = common_response_data(response)
    for keyword in meta_tags['keywords'].split(','):
        article.tags.append(keyword.strip())
    article.info.title = meta_tags['og:title']
    article.info.description = meta_tags['og:description']
    article.images.thumbnail.url = meta_tags['og:image']
    if 'og:image:width' in meta_tags:
        article.images.thumbnail.width = meta_tags['og:image:width']
    if 'og:image:height' in meta_tags:
        article.images.thumbnail.height = meta_tags['og:image:height']
    if 'fb:pages' in meta_tags:
        article.publisher.facebook.page_ids.append(meta_tags['fb:pages'])
    article.publisher.facebook.url = meta_tags['article:publisher']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.twitter.description = meta_tags['twitter:description']
    article.publisher.twitter.image = meta_tags['twitter:image']
    if 'fb:app_id' in meta_tags:
        article.publisher.facebook.app_id = meta_tags['fb:app_id']
    find_script_json(soup, article)
    remove_tags(soup)
    find_main_content(
        [{'tag': 'article', 'meta': {}}], article, response, soup)
    return article.json(), link_id


def cnbc_url_filter(_url):
    """Filters URLs in the CNBC domain"""
    return True
