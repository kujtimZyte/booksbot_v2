# -*- coding: utf-8 -*-
"""Parser for the Huffington Post website"""
from .common import extract_item_from_element_css


def huffingtonpost_parse(response):
    """Parses the response from a Huffington Post website"""
    return extract_item_from_element_css(response, "div.entry__text")
