# -*- coding: utf-8 -*-
"""Parser for the Vice website"""
from .common import extract_item_from_element_css


def vice_parse(response):
    """Parses the response from a Vice website"""
    return extract_item_from_element_css(response, "article")
