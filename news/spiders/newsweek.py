# -*- coding: utf-8 -*-
"""Parser for the News Week website"""
from .common import extract_item_from_element_css


def newsweek_parse(response):
    """Parses the response from a News Week website"""
    return extract_item_from_element_css(response, "div.article-body")
