import unittest
from news.spiders.news import NewsSpider
import os
from scrapy.http import TextResponse, Request
 
class TestNewsSpider(unittest.TestCase):
 
    def setUp(self):
        self.scraper = NewsSpider()
        self.htmlDirectory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_html_files')

    def testCNNHomepage(self):
        newRequests, items = self.fakeHTML('cnn.com.html', 'https://www.cnn.com')
        self.assertIn('https://www.cnn.com/2018/10/18/politics/beto-orourke-impeach-trump-cnn-town-hall/index.html', newRequests)
        self.assertEqual(len(newRequests), 188)
        self.assertEqual(len(items), 0)
    
    def testCNNCanadaLegalPotTicket(self):
        newRequests, items = self.fakeHTML('cnn-canada-legal-pot-ticket-trnd.html', 'https://www.cnn.com/2018/10/18/health/canada-legal-pot-ticket-trnd')
        self.assertIn('http://www.cnn.com/2018/10/17/politics/alaska-lieutenant-governor-resigns/?iid=ob_lockedrail_topeditorial&obOrigUrl=true', newRequests)
        self.assertEqual(len(newRequests), 117)
        self.assertEqual(len(items), 1)
        rawItems = items[0]['items']
        self.assertEqual(len(rawItems), 1)
        firstItem = rawItems[0]
        expectedItem = {
            'articleBody': [
                [
                    {'text': u'The Winnipeg Police posted a photo later that day of a (redacted) traffic ticket one of its officers had to write for "consuming cannabis in a motor vehicle."'}
                ],
                [
                    {'text': u'"So... this happened early this morning," the police department wrote. "Just like alcohol, consuming cannabis is legal - and like alcohol, consuming it in your vehicle is **not**."'}
                ],
                [
                    {'text': u'Winnipeg Police Service traffic division Insp. Gord Spado'},
                    {'text': u'told CBC news', 'link': u'https://www.cbc.ca/news/canada/manitoba/cannabis-consumption-car-ticket-1.4867328'},
                    {'text': u'the ticket was issued by an officer at approximately 1 a.m., a whole hour after pot buying became legal. He told CBC the weed involved in this particular traffic stop was probably illegally purchased. (CNN has reached out to the department for details.)'}
                ],
                [
                    {'text': u'While many Canadians are stoked to toke in a legal fashion now, the Winnipeg Police reminded people in a subsequent tweet that'},
                    {'text': u'there are still laws and regulations that go along with the new provisions', 'link': u'https://lgcamb.ca/cannabis/'},
                    {'text': u'.'}
                ],
                [
                    {'text': u'"Bottom line is that you cannot consume cannabis in your vehicle,"'},
                    {'text': u'it tweeted', 'link': u'https://twitter.com/wpgpolice/status/1052665350486192128'},
                    {'text': u'.'}
                ],
                [
                    {'text': u"Here's what you need to know about recreational pot in Canada", 'link': u'https://www.cnn.com/2018/10/17/health/canada-legalizes-recreational-marijuana/index.html'}
                ]
            ],
            u'thumbnailUrl': u'https://cdn.cnn.com/cnnnext/dam/assets/181018092408-canada-pot-ticket-super-tease.jpg',
            'imgs': [],
            u'description': u"This is why we can't have nice things, random traffic offender. ",
            u'author': u'AJ Willingham, CNN',
            u'url': u'https://www.cnn.com/2018/10/18/health/canada-legal-pot-ticket-trnd/index.html',
            u'image': u'https://cdn.cnn.com/cnnnext/dam/assets/181018092408-canada-pot-ticket-super-tease.jpg',
            u'datePublished': u'2018-10-18T13:41:12Z',
            u'headline': u'Weed was legal in Canada for a whole hour before someone messed it up  - CNN',
            u'alternativeHeadline': u'Weed was legal in Canada for a whole hour before someone got a ticket for driving and toking',
            u'keywords': u'health, Weed was legal in Canada for a whole hour before someone messed it up  - CNN',
            u'isPartOf': u'health',
            u'articleSection': u'health',
            u'dateCreated': u'2018-10-18T13:41:12Z',
            u'dateModified': u'2018-10-18T16:17:50Z'
        }
        self.assertEqual(expectedItem, firstItem)
    
    def fakeHTML(self, htmlFilename , url):
        htmlFilePath = os.path.join(self.htmlDirectory, htmlFilename)
        html = open(htmlFilePath).read()
        request = Request(url=url)
        response = TextResponse(url=url,
            request=request,
            body=html)
        scrapedItems = self.scraper.parse(response)
        newRequests = []
        items = []
        for scrapedItem in scrapedItems:
            if isinstance(scrapedItem, Request):
                requestURL = scrapedItem.url
                if not self.isURLAllowed(requestURL):
                    continue
                if requestURL not in newRequests:
                    newRequests.append(requestURL)
            else:
                items.append(scrapedItem)
        return newRequests, items
    
    def isURLAllowed(self, url):
        for allowedDomain in self.scraper.allowed_domains:
            if allowedDomain in url:
                return True
        return False
 
if __name__ == '__main__':
    unittest.main()
