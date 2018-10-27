# -*- coding: utf-8 -*-
"""Parser for the Independent website"""
from .common import extract_item_from_element_css


def independent_parse(response):
    """Parses the response from a Independent website"""
    return extract_item_from_element_css(response, "div.body-content")
