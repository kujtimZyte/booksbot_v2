# -*- coding: utf-8 -*-
"""Parser for the BBC website"""
from .common import extract_metadata, extract_text_with_links, extract_imgs


def bbc_parse(response):
    """Parses the response from a BBC website"""
    items = []
    for div_element in response.css("div.story-body__inner"):
        paragraph_list = []
        for p_element in div_element.css("p"):
            paragraph_list.extend(extract_text_with_links(p_element, []))
        imgs = extract_imgs(response, div_element)
        item = {'articleBody': paragraph_list, 'imgs' : imgs}
        item.update(extract_metadata(response))
        items.append(item)
    return items
