# -*- coding: utf-8 -*-
"""Parser for the CNN website"""
from .article import Author
from .common import find_main_content, remove_common_tags, execute_script,\
common_response_data, extract_link_id, find_common


def cnn_url_parse(url):
    """Parses the URL from a CNN website"""
    return extract_link_id(url, length=8)


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'article', 'meta': {'class': 'cd'}},
        {'tag': 'div', 'meta': {'class': 'column'}},
        {'tag': 'div', 'meta': {'class': 'zn-body__read-more'}},
        {'tag': 'div', 'meta': {'class': 'video__end-slate__top-wrapper'}},
        {'tag': 'h4', 'meta': {'class': 'video__end-slate__tertiary-title'}},
        {'tag': 'div', 'meta': {'class': 'cn-carousel-medium-strip'}},
        {'tag': 'div', 'meta': {'class': 'gigya-sharebar-element'}},
        {'tag': 'div', 'meta': {'class': 'el__gallery-showhide'}},
        {'tag': 'span', 'meta': {'class': 'el__storyelement__gray'}},
        {'tag': 'span', 'meta': {'class': 'el__storyelement__header'}}
    ], soup)


def cnn_parse(response):
    """Parses the response from a CNN Website"""
    link_id = cnn_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup, meta_tags, article = common_response_data(response)
    find_common(soup, meta_tags, article)
    for script_tag in soup.findAll('script'):
        context = execute_script(script_tag)
        if not hasattr(context, 'CNN'):
            continue
        if hasattr(context.CNN, 'contentModel'):
            content_model = context.CNN['contentModel']
            analytics = content_model['analytics']
            author = Author()
            author.name = analytics['author'].replace('By ', '').replace(', CNN', '')
            if author.name == "CNN Library":
                continue
            article.authors.append(author)
    remove_tags(soup)
    find_main_content(
        [{'tag': 'article', 'meta': {}}], article, response, soup)
    return article.json(), link_id


def cnn_url_filter(_url):
    """Filters URLs in the CNN domain"""
    return True
