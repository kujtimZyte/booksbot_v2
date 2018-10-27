# -*- coding: utf-8 -*-
"""Parser for the Verge website"""
from .common import extract_item_from_element_css


def the_verge_parse(response):
    """Parses the response from a Verge website"""
    return extract_item_from_element_css(response, "div.c-entry-content")
