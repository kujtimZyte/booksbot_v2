# -*- coding: utf-8 -*-
"""Parser for the RadioNZ website"""
from .common import extract_item_from_element_css


def radionz_parse(response):
    """Parses the response from a RadioNZ website"""
    return extract_item_from_element_css(response, "div.article__body")
