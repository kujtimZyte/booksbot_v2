# -*- coding: utf-8 -*-
"""Parser for the Guardian website"""


def extract_main_urls(response):
    urls = []
    for li_element in response.css("li.pillars__item"):
        for url in li_element.xpath("a/@href").extract():
            urls.append(response.urljoin(url))
    return urls


def extract_story_urls(response):
    urls = []
    for div_element in response.css("div.fc-item"):
        for a_element in div_element.css("a"):
            url = a_element.xpath("@href").extract_first()
            urls.append(response.urljoin(url))
    return urls


def guardian_parse(response):
    """Parses the response from a Guardian website"""
    urls = extract_main_urls(response)
    urls.extend(extract_story_urls(response))
    items = []
    return urls, items
