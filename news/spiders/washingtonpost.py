# -*- coding: utf-8 -*-
"""Parser for the Washington Post website"""
from .common import extract_item_from_element_css


def washingtonpost_parse(response):
    """Parses the response from a Washington Post website"""
    return extract_item_from_element_css(response, "article")
