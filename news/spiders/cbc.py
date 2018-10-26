# -*- coding: utf-8 -*-
"""Parser for the CBC website"""
from .common import extract_text_with_links, extract_item


def cbc_parse(response):
    """Parses the response from a CBC website"""
    items = []
    for div_element in response.css("div.story"):
        paragraph_list = []
        for p_element in div_element.css("p"):
            paragraph_list.extend(extract_text_with_links(p_element, []))
        item = extract_item(response, paragraph_list, div_element)
        if item:
            items.append(item)
    return items
