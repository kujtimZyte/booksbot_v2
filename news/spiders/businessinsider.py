# -*- coding: utf-8 -*-
"""Parser for the Business Insider website"""
from .common import extract_item_from_element_css


def businessinsider_parse(response):
    """Parses the response from a Business Insider website"""
    return extract_item_from_element_css(response, "article")
