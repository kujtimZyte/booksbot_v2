# -*- coding: utf-8 -*-
"""Parser for the Fox website"""
from .common import extract_item_from_element_css


def fox_parse(response):
    """Parses the response from a Fox website"""
    return extract_item_from_element_css(response, "div.article-body")
