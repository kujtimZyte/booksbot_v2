# -*- coding: utf-8 -*-
"""Parser for the New York Times website"""
from .common import extract_metadata, extract_javascript_strings


def nytimes_parse(response):
    """Parses the response from the New York Times website"""
    full_text = response.text
    find_pattern = '{"__typename":"TextInline","text":"'
    paragraph_list = extract_javascript_strings(full_text, find_pattern)
    items = []
    if paragraph_list:
        item = extract_metadata(response)
        item['articleBody'] = []
        for paragraph in paragraph_list:
            item['articleBody'].append({
                'text': paragraph
            })
        item['imgs'] = []
        items.append(item)
    return items
