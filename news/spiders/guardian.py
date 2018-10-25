# -*- coding: utf-8 -*-
"""Parser for the Guardian website"""
from .common import extract_metadata, extract_text_with_links


def guardian_parse(response):
    """Parses the response from a Guardian website"""
    items = []
    for article in response.css("article"):
        paragraph_list = []
        for div_element in response.css("div.content__article-body"):
            for p_element in div_element.css("p"):
                paragraph_list.extend(extract_text_with_links(p_element, []))
        if not paragraph_list:
            continue
        imgs = []
        for img in article.css('img::attr(src)').extract():
            full_img = response.urljoin(img)
            imgs.append(full_img)
        item = {'articleBody': paragraph_list, 'imgs' : imgs}
        item.update(extract_metadata(response))
        items.append(item)
    return items
