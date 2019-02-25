# -*- coding: utf-8 -*-
"""Parser for the CBC website"""
from bs4 import NavigableString
from .article import Author
from .common import strip_query_from_url, remove_common_tags, find_main_content, \
find_script_json, common_response_data


def cbc_url_parse(url):
    """Parses the URL from a CBC website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) != 6:
        return None
    return url_split[-1]


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'div', 'meta': {'class': 'card-content'}},
        {'tag': 'div', 'meta': {'class': 'moreStories'}},
        {'tag': 'div', 'meta': {'class': 'vf-commenting'}},
        {'tag': 'div', 'meta': {'class': 'comments'}},
        {'tag': 'div', 'meta': {'class': 'trending'}},
        {'tag': 'div', 'meta': {'class': 'relatedlinks'}},
        {'tag': 'div', 'meta': {'class': 'contentFeedback'}},
        {'tag': 'div', 'meta': {'class': 'authorprofile'}},
        {'tag': 'strong', 'meta': {}},
        {'tag': 'div', 'meta': {'class': 'label-Opinion'}},
        {'tag': 'span', 'meta': {'class': 'similarLinkText'}},
        {'tag': 'ul', 'meta': {'class': 'similarLinks'}},
        {'tag': 'div', 'meta': {'class': 'vf-share-dropdown'}},
        {'tag': 'li', 'meta': {'class': 'vf-share-option'}}
    ], soup)


def cbc_parse(response):
    """Parses the response from a CBC Website"""
    link_id = cbc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup, meta_tags, article = common_response_data(response)
    article.publisher.organisation = meta_tags['og:site_name']
    article.publisher.facebook.page_ids.append(meta_tags['fb:pages'])
    article.publisher.twitter.card = meta_tags['twitter:card']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.info.title = meta_tags['og:title']
    article.info.description = meta_tags['og:description']
    article.info.genre = meta_tags['cXenseParse:cbc-subsection1']
    article.images.thumbnail.url = meta_tags['og:image']
    article.time.set_published_time(meta_tags['article:published_time'])
    article.time.set_modified_time(meta_tags['article:modified_time'])
    author = Author()
    author.name = soup.find('p', {'class': 'authorprofile-name'}).text
    for a_tag in soup.find('a', {'class': 'authorprofile-item'}):
        if isinstance(a_tag, NavigableString):
            continue
        a_text = a_tag.text
        if a_text:
            if a_text.startswith('@'):
                author.twitter_url = a_tag['href']
    article.authors.append(author)
    find_script_json(soup, article)
    remove_tags(soup)
    find_main_content(
        [{'tag': 'div', 'meta': {'class': 'sclt-storycontent'}}], article, response, soup)
    return article.json(), link_id


def cbc_url_filter(_url):
    """Filters URLs in the CBC domain"""
    return True
