# -*- coding: utf-8 -*-
"""Parser for the Sydney Morning Herald website"""
from .common import extract_item_from_element_css


def smh_parse(response):
    """Parses the response from a Sydney Morning Herald website"""
    return extract_item_from_element_css(response, "article")
