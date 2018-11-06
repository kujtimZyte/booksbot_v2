# -*- coding: utf-8 -*-
"""Parser for the CNBC website"""
from .common import extract_item_from_element_css


def cnbc_parse(response):
    """Parses the response from a CNBC website"""
    return extract_item_from_element_css(response, "article")
