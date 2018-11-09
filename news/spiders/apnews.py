# -*- coding: utf-8 -*-
"""Parser for the Associated Press News website"""
from .common import extract_item_from_element_css


def apnews_parse(response):
    """Parses the response from a Associated Press News website"""
    return extract_item_from_element_css(response, "div.Article")
