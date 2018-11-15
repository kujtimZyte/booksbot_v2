# -*- coding: utf-8 -*-
"""Parser for the CTV News website"""
from .common import extract_item_from_element_css


def ctvnews_parse(response):
    """Parses the response from a CTV News website"""
    return extract_item_from_element_css(response, "div.articleBody")
