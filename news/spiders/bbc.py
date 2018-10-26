# -*- coding: utf-8 -*-
"""Parser for the BBC website"""
from .common import extract_item_from_element_css


def bbc_parse(response):
    """Parses the response from a BBC website"""
    return extract_item_from_element_css(response, "div.story-body__inner")
