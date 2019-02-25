# -*- coding: utf-8 -*-
"""Parser for the CBS website"""
import hashlib
from .common import strip_query_from_url, remove_common_tags, find_main_content, \
find_script_json, common_response_data


def cbs_url_parse(url):
    """Parses the URL from a CBS website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) != 5:
        return None
    return hashlib.sha224(url_split[-1]).hexdigest()


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'div', 'meta': {'class': 'social'}},
        {'tag': 'div', 'meta': {'class': 'copyright'}}
    ], soup)


def cbs_parse(response):
    """Parses the response from a CBS Website"""
    link_id = cbs_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup, meta_tags, article = common_response_data(response)
    for keyword in meta_tags['keywords'].split(','):
        article.tags.append(keyword.strip())
    article.info.title = meta_tags['og:title']
    article.images.thumbnail.url = meta_tags['og:image']
    article.images.thumbnail.width = meta_tags['og:image:width']
    article.images.thumbnail.height = meta_tags['og:image:height']
    article.publisher.facebook.page_ids.append(meta_tags['fb:pages'])
    article.publisher.facebook.url = meta_tags['article:publisher']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.twitter.description = meta_tags['twitter:description']
    article.publisher.twitter.image = meta_tags['twitter:image']
    find_script_json(soup, article)
    remove_tags(soup)
    find_main_content(
        [{'tag': 'article', 'meta': {}}], article, response, soup)
    return article.json(), link_id


def cbs_url_filter(_url):
    """Filters URLs in the CBS domain"""
    return True
