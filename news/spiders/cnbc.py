# -*- coding: utf-8 -*-
"""Parser for the CNBC website"""
from .common import find_main_content, remove_common_tags,\
find_script_json, common_response_data, extract_link_id, parse_meta_tags


def cnbc_url_parse(url):
    """Parses the URL from a CNBC website"""
    return extract_link_id(url, lengths=[7,8])


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_common_tags([
        {'tag': 'div', 'meta': {'class': 'embed-container'}}
    ], soup)


def cnbc_parse(response):
    """Parses the response from a CNBC Website"""
    link_id = cnbc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup, meta_tags, article = common_response_data(response)
    parse_meta_tags(meta_tags, article)
    find_script_json(soup, article)
    remove_tags(soup)
    find_main_content(
        [{'tag': 'article', 'meta': {}}], article, response, soup)
    return article.json(), link_id


def cnbc_url_filter(_url):
    """Filters URLs in the CNBC domain"""
    return True
