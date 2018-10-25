# -*- coding: utf-8 -*-
"""Parser for the BBC website"""
from .common import extract_text_with_links, extract_item


def bbc_parse(response):
    """Parses the response from a BBC website"""
    items = []
    for div_element in response.css("div.story-body__inner"):
        paragraph_list = []
        for p_element in div_element.css("p"):
            paragraph_list.extend(extract_text_with_links(p_element, []))
        item = extract_item(response, paragraph_list, div_element)
        if item:
            items.append(item)
    return items
