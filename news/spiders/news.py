# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["cnn.com"]
    start_urls = [
        #'http://www.cnn.com'
        'https://www.cnn.com/2018/10/18/health/canada-legal-pot-ticket-trnd'
    ]
    removeableParagraphs = [
        u'Paid Content',
        u'More from CNN',
        u'Read More',
        u'Recommended by',
        u'READ MORE:'
    ]
    badImgs = [
        'outbrain',
        'data:image',
        'cnnnext'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 0.5},
            )

    def parse(self, response):
        for article in response.xpath("//article"):
            for url in article.xpath("//a/@href").extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
        for li in response.css("li.ob-dynamic-rec-container"):
            for url in li.xpath("//a/@href").extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
        items = []
        for article in response.css("article"):
            item = {}
            for property in article.xpath('.//*[@itemprop]'):
                propertyContent = property.xpath("@content").extract_first()
                propertyName = property.xpath("@itemprop").extract_first()
                if propertyContent != None:
                    item[propertyName] = propertyContent
                else:
                    if propertyName == u'articleBody':
                        paragraphs = []
                        for paragraphDiv in property.css('div.zn-body__paragraph'):
                            paragraphList = []
                            for paragraph in paragraphDiv.xpath(".//text()"):
                                strippedParagraph = paragraph.extract().strip()
                                if len(strippedParagraph) > 0 and strippedParagraph not in self.removeableParagraphs:
                                    paragraphList.append({
                                        'text': strippedParagraph
                                    })
                            for link in paragraphDiv.css('a'):
                                text = link.xpath('text()').extract_first().strip()
                                href = link.xpath('@href').extract_first().strip()
                                for paragraphText in paragraphList:
                                    if paragraphText['text'] == text:
                                        paragraphText['link'] = href
                            if len(paragraphList) > 0:
                                paragraphs.append(paragraphList)
                        item[propertyName] = paragraphs
            imgs = []
            for img in article.css('img::attr(src)').extract():
                fullImg = response.urljoin(img)
                if not self.isBadImg(fullImg) and fullImg not in imgs:
                    imgs.append(fullImg)
            if item:
                item['imgs'] = imgs
                items.append(item)
        if len(items) > 0:
            yield {
                'items' : items
                #'html': response.text
            }

    def isBadImg(self, img):
        for badImg in self.badImgs:
            if badImg in img:
                return True
        return False
