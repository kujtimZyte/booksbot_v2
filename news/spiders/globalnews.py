# -*- coding: utf-8 -*-
"""Parser for the Global News website"""
from .common import extract_item_from_element_css


def globalnews_parse(response):
    """Parses the response from a Global News website"""
    return extract_item_from_element_css(response, "span.gnca-article-story-txt")
