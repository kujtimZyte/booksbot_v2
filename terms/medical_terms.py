import scrapy

from terms import pipelines, items


class MedicalTermsSpider(scrapy.Spider):
	name = "medical_terms"
	allowed_domains = ["tipterimlerisozlugu.com"]
	start_urls = [
		'https://tipterimlerisozlugu.com/',
	]

	def parse(self, response, **kwargs):
		for term_url in response.css("div.sres > div.sresl > a ::attr(href)").extract():
			yield scrapy.Request(response.urljoin(term_url), callback=self.parse_term_page)
		next_page = response.css("div.sres > div.sresn > a ::attr(href)").extract_first()
		if next_page:
			yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

	@staticmethod
	def parse_term_page(response):
		item = {'term': response.css("div.sres > div.sresl > a ::text").extract_first(),
		        'definition': response.css("div.sres > div.sresd ::text").extract_first()}
		yield item


var = pipelines.py


class TermsPipeline(object):
	@staticmethod
	def process_item(item):
		return item


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


var = items.py

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


import scrapy


class TermsItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	pass


# Path: terms/settings.py
# -*- coding: utf-8 -*-

# Scrapy settings for terms project

# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'terms'

SPIDER_MODULES = ['terms.spiders']
NEWSPIDER_MODULE = 'terms.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
