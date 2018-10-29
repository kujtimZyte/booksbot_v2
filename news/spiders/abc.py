# -*- coding: utf-8 -*-
"""Parser for the ABC website"""
from .common import extract_item_from_element_css


def abc_parse(response):
    """Parses the response from a ABC website"""
    return extract_item_from_element_css(response, "div.article")
