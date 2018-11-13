# -*- coding: utf-8 -*-
"""Parser for the Bloomberg website"""
from .common import extract_item_from_element_css


def bloomberg_parse(response):
    """Parses the response from a Bloomberg website"""
    return extract_item_from_element_css(response, "div.body-copy-v2")
