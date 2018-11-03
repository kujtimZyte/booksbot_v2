# -*- coding: utf-8 -*-
"""Parser for the CNN website"""
from .common import extract_text_with_links


def is_bad_img(img):
    """
    Checks whether an image is worthy of inclusion
    """
    bad_imgs = [
        'outbrain',
        'data:image',
        'cnnnext'
    ]
    for bad_img in bad_imgs:
        if bad_img in img:
            return True
    return False


def extract_paragraphs(itemprop_element):
    """
    Extract the paragraphs from an article element
    """
    removeable_paragraphs = [
        u'Paid Content',
        u'More from CNN',
        u'Read More',
        u'Recommended by',
        u'READ MORE:'
    ]
    paragraphs = []
    for paragraph_div in itemprop_element.css(
            'div.zn-body__paragraph'):
        paragraph_list = extract_text_with_links(paragraph_div, removeable_paragraphs)
        if paragraph_list:
            paragraphs.extend(paragraph_list)
    return paragraphs


def cnn_parse(response):
    """
    Parses the CNN website from a scrapy response
    """
    items = []
    for article in response.css("article"):
        item = {}
        for itemprop in article.xpath('.//*[@itemprop]'):
            property_content = itemprop.xpath("@content").extract_first()
            property_name = itemprop.xpath("@itemprop").extract_first()
            if property_content is not None:
                item[property_name] = property_content
            else:
                if property_name == u'articleBody':
                    if property_name not in item:
                        item[property_name] = []
                    item[property_name].extend(extract_paragraphs(itemprop))
        imgs = []
        for img in article.css('img::attr(src)').extract():
            full_img = response.urljoin(img)
            if not is_bad_img(full_img) and full_img not in imgs:
                imgs.append(full_img)
        if item:
            item['imgs'] = imgs
            items.append(item)
    return items
