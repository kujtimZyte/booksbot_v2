# -*- coding: utf-8 -*-
"""Common utilities for scraping"""


def extract_article_urls(response):
    """Extracts URLs from article tags"""
    urls = []
    for article in response.xpath("//article"):
        for url in article.xpath("//a/@href").extract():
            urls.append(response.urljoin(url))
    return urls
