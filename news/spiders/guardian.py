# -*- coding: utf-8 -*-
"""Parser for the Guardian website"""
from .common import extract_metadata, extract_text_with_links


def extract_main_urls(response):
    """Extracts the main URLs from the header"""
    urls = []
    for li_element in response.css("li.pillars__item"):
        for url in li_element.xpath("a/@href").extract():
            urls.append(response.urljoin(url))
    return urls


def extract_story_urls(response):
    """Extracts other story URLs"""
    urls = []
    for div_element in response.css("div.fc-item"):
        for a_element in div_element.css("a"):
            url = a_element.xpath("@href").extract_first()
            urls.append(response.urljoin(url))
    for li_element in response.css("li.right-most-popular-item"):
        for a_element in li_element.css("a"):
            url = a_element.xpath("@href").extract_first()
            urls.append(response.urljoin(url))
    return urls


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
    urls = extract_main_urls(response)
    urls.extend(extract_story_urls(response))
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
    return urls, items
