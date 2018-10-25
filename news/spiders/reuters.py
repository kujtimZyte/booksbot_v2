# -*- coding: utf-8 -*-
"""Parser for the Reuters website"""
from .common import extract_metadata, extract_imgs


def extract_reuters_metadata(response):
    """Extracts metadata from meta tags"""
    metadata = extract_metadata(response)
    filtered_metadata = {
        'thumbnailUrl': metadata['og:image'],
        'description': metadata['description'],
        'author': metadata['Author'],
        'url': metadata['og:url'],
        'image': metadata['og:image'],
        'datePublished': metadata['og:article:published_time'],
        'headline': metadata['og:title'],
        'alternativeHeadline': metadata['analyticsAttributes.contentTitle'],
        'keywords': metadata['keywords'],
        'isPartOf': metadata['og:article:section'],
        'articleSection': metadata['og:article:section'],
        'dateCreated': metadata['og:article:published_time'],
        'dateModified': metadata['og:article:modified_time']
    }
    filtered_metadata.update(metadata)
    return filtered_metadata


def reuters_parse(response):
    """Parses the response from a Reuters website"""
    items = []
    for div_element in response.css("div.ArticlePage_container"):
        paragraph_list = []
        for p_element in div_element.css("p"):
            paragraph_list.append({
                'text':  p_element.xpath(".//text()").extract_first().strip()
            })
        imgs = extract_imgs(response, div_element)
        item = {'articleBody': paragraph_list, 'imgs' : imgs}
        item.update(extract_reuters_metadata(response))
        items.append(item)
    return items
