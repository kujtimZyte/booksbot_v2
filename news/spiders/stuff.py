# -*- coding: utf-8 -*-
"""Parser for the stuff website"""
from .common import extract_item_from_element_css


def stuff_parse(response):
    """Parses the response from a stuff website"""
    return extract_item_from_element_css(response, "div.sics-component__story")
