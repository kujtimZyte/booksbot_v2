# -*- coding: utf-8 -*-
"""The main scraper for news sites"""
import scrapy
from scrapy_splash import SplashRequest
from .custom_settings import NEWS_HTTP_AUTH_USER


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
        paragraph_list = []
        for paragraph in paragraph_div.xpath(".//text()"):
            stripped_paragraph = paragraph.extract().strip()
            if stripped_paragraph and \
                stripped_paragraph not in removeable_paragraphs:
                paragraph_list.append({
                    'text': stripped_paragraph
                })
        for link in paragraph_div.css('a'):
            text = link.xpath(
                'text()').extract_first().strip()
            href = link.xpath(
                '@href').extract_first().strip()
            for paragraph_text in paragraph_list:
                if paragraph_text['text'] == text:
                    paragraph_text['link'] = href
        if paragraph_list:
            paragraphs.append(paragraph_list)
    return paragraphs


class NewsSpider(scrapy.Spider):
    """Responsible for parsing news sites"""
    name = "news"
    allowed_domains = ["cnn.com"]
    start_urls = [
        'http://www.cnn.com'
    ]
    http_user = NEWS_HTTP_AUTH_USER
    http_pass = ''

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait': 0.5})

    def parse(self, response):
        for article in response.xpath("//article"):
            for url in article.xpath("//a/@href").extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
        for li_element in response.css("li.ob-dynamic-rec-container"):
            for url in li_element.xpath("//a/@href").extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
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
                        item[property_name] = extract_paragraphs(itemprop)
            imgs = []
            for img in article.css('img::attr(src)').extract():
                full_img = response.urljoin(img)
                if not is_bad_img(full_img) and full_img not in imgs:
                    imgs.append(full_img)
            if item:
                item['imgs'] = imgs
                items.append(item)
        if items:
            yield {
                'items': items
            }
