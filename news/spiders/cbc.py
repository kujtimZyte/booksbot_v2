# -*- coding: utf-8 -*-
"""Parser for the CBC website"""
from .common import extract_item_from_element_css


def cbc_parse(response):
    """Parses the response from a CBC website"""
    return extract_item_from_element_css(response, "div.story")
