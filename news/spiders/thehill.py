# -*- coding: utf-8 -*-
"""Parser for The Hill website"""
from .common import extract_item_from_element_css


def thehill_parse(response):
    """Parses the response from The Hill website"""
    return extract_item_from_element_css(response, "div.content-wrp")
