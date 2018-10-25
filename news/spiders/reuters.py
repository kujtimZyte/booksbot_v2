# -*- coding: utf-8 -*-
"""Parser for the Reuters website"""
from .common import extract_item


def reuters_parse(response):
    """Parses the response from a Reuters website"""
    items = []
    for div_element in response.css("div.ArticlePage_container"):
        paragraph_list = []
        for p_element in div_element.css("p"):
            paragraph_list.append({
                'text':  p_element.xpath(".//text()").extract_first().strip()
            })
        item = extract_item(response, paragraph_list, div_element)
        if item:
            items.append(item)
    return items
