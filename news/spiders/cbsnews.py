# -*- coding: utf-8 -*-
"""Parser for the CBS News website"""
from .common import extract_item_from_element_css


def cbsnews_parse(response):
    """Parses the response from a CBS News website"""
    return extract_item_from_element_css(response, "article")
