# -*- coding: utf-8 -*-
"""Parser for the Ars Technica website"""
from .common import extract_item_from_element_css


def arstechnica_parse(response):
    """Parses the response from a Ars Technica website"""
    return extract_item_from_element_css(response, "div.article-content")
