# -*- coding: utf-8 -*-
"""Parser for the Daily Beast website"""
from .common import extract_item_from_element_css


def dailybeast_parse(response):
    """Parses the response from a Daily Beast website"""
    if response.url == 'https://www.thedailybeast.com/':
        return None
    return extract_item_from_element_css(response, "div.Body__content")
