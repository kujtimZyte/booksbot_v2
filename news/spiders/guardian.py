# -*- coding: utf-8 -*-
"""Parser for the Guardian website"""
from .common import extract_metadata, extract_text_with_links


def extract_guardian_metadata(response):
    """Extracts the metadata related to the article"""
    metadata = extract_metadata(response)
    filtered_metadata = {
        'thumbnailUrl': metadata['og:image'],
        'url': metadata['og:url'],
        'image': metadata['og:image'],
        'datePublished': metadata['article:published_time'],
        'headline': metadata['og:title'],
        'keywords': metadata['news_keywords'],
        'isPartOf': metadata['article:section'],
        'articleSection': metadata['article:section'],
        'dateCreated': metadata['article:published_time'],
        'dateModified': metadata['article:modified_time']
    }
    filtered_metadata.update(metadata)
    return metadata


def guardian_parse(response):
    """Parses the response from a Guardian website"""
    items = []
    for article in response.css("article"):
        paragraph_list = []
        for div_element in response.css("div.content__article-body"):
            for p_element in div_element.css("p"):
                paragraph_list.extend(extract_text_with_links(p_element, []))
        imgs = []
        for img in article.css('img::attr(src)').extract():
            full_img = response.urljoin(img)
            imgs.append(full_img)
        item = {'articleBody': paragraph_list, 'imgs' : imgs}
        item.update(extract_guardian_metadata(response))
        items.append(item)
    return items
