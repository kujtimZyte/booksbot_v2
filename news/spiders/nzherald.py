# -*- coding: utf-8 -*-
"""Parser for the New Zealand Herald website"""
from .common import extract_item_from_element_css


def nzherald_parse(response):
    """Parses the response from a New Zealand Herald website"""
    return extract_item_from_element_css(response, "article")
