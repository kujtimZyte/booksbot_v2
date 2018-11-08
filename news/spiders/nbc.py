# -*- coding: utf-8 -*-
"""Parser for the NBC website"""
from .common import extract_item_from_element_css


def nbc_parse(response):
    """Parses the response from a NBC website"""
    return extract_item_from_element_css(response, "article.articleBody")
