# -*- coding: utf-8 -*-
"""Common utilities for scraping"""


def extract_urls(response):
    """Extracts URLs from a tags"""
    urls = []
    for url in response.xpath("//a/@href").extract():
        urls.append(response.urljoin(url))
    return urls


def extract_metadata(response):
    """Extracts metadata from meta tags"""
    metadata = {}
    for meta_element in response.xpath('//meta'):
        name = meta_element.xpath("@name").extract_first()
        meta_property = meta_element.xpath("@property").extract_first()
        content = meta_element.xpath("@content").extract_first()
        meta_key = name
        if not meta_key:
            meta_key = meta_property
        metadata[meta_key] = content
    return metadata


def extract_text_with_links(element, removeable_paragraphs):
    """Extracts text with the appropriate hyperlink"""
    paragraph_list = []
    for paragraph in element.xpath(".//text()"):
        stripped_paragraph = paragraph.extract().strip()
        if stripped_paragraph and stripped_paragraph not in removeable_paragraphs:
            paragraph_list.append({
                'text': stripped_paragraph
            })
    for link in element.css('a'):
        text_path = link.xpath('text()').extract_first()
        if text_path is None:
            continue
        text = text_path.strip()
        href_path = link.xpath('@href').extract_first()
        if href_path is None:
            continue
        href = href_path.strip()
        for paragraph_text in paragraph_list:
            if paragraph_text['text'] == text:
                paragraph_text['link'] = href
    return paragraph_list


def extract_imgs(response, element):
    """Extracts img sources from an element"""
    imgs = []
    for img in element.css('img::attr(src)').extract():
        full_img = response.urljoin(img)
        imgs.append(full_img)
    return imgs


def extract_item(response, paragraph_list, main_element):
    """Extracts items from a paragraph list, the main element and the response"""
    if not paragraph_list:
        return None
    item = extract_metadata(response)
    item['articleBody'] = paragraph_list
    item['imgs'] = extract_imgs(response, main_element)
    return item
