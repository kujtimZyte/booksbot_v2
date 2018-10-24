import unittest
from news.spiders.news import NewsSpider
import os
from scrapy.http import TextResponse, Request
import json
 
class TestNewsSpider(unittest.TestCase):
 
    def setUp(self):
        self.scraper = NewsSpider()
        self.htmlDirectory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_html_files')

    def test_cnn_homepage(self):
        self.check_fake_html_scrape(
            'cnn.com.html',
            'https://www.cnn.com',
            'cnn.com.json')
    
    def test_cnn_canada_legal_pot_ticket(self):
        self.check_fake_html_scrape(
            'cnn-canada-legal-pot-ticket-trnd.html',
            'https://www.cnn.com/2018/10/18/health/canada-legal-pot-ticket-trnd',
            'cnn-canada-legal-pot-ticket-trnd.json')

    def test_cnn_aretha_franklin_fast_facts(self):
        self.check_fake_html_scrape(
            'cnn-aretha-franklin-fast-facts.html',
            'https://edition.cnn.com/2013/06/27/us/aretha-franklin-fast-facts/index.html',
            'cnn-aretha-franklin-fast-facts.json')

    def test_reuters_homepage(self):
        self.check_fake_html_scrape(
            'reuters.com.html',
            'https://www.reuters.com/',
            'reuters.com.json')

    def test_reuters_how_the_man_behind_khashoggi_murder_ran_the_killing_via_skype(self):
        self.check_fake_html_scrape(
            'reuters-how-the-man-behind-khashoggi-murder-ran-the-killing-via-skype.html',
            'https://www.reuters.com/article/us-saudi-khashoggi-adviser-insight/how-the-man-behind-khashoggi-murder-ran-the-killing-via-skype-idUSKCN1MW2HA',
            'reuters-how-the-man-behind-khashoggi-murder-ran-the-killing-via-skype.json')

    def test_guardian_homepage(self):
        self.check_fake_html_scrape(
            'guardian.com.html',
            'https://www.theguardian.com/international?INTCMP=CE_INT',
            'guardian.com.json')

    def test_guardian_jamal_khashoggi_trump_cover_up_sanctions_visas(self):
        self.check_fake_html_scrape(
            'guardian-jamal-khashoggi-trump-cover-up-sanctions-visas.html',
            'https://www.theguardian.com/world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas',
            'guardian-jamal-khashoggi-trump-cover-up-sanctions-visas.json')

    def check_fake_html_scrape(self, html_filename, url, json_filename):
        output_json = self.fake_html(html_filename, url)
        #print(output_json)
        json_filepath = os.path.join(self.htmlDirectory, json_filename)
        with open(json_filepath) as json_filehandle:
            expected_output = json.load(json_filehandle)
            produced_output = json.loads(output_json)
            self.assertEqual(produced_output['requests'], expected_output['requests'])
            self.assertEqual(produced_output['items'], expected_output['items'])

    def fake_html(self, htmlFilename , url):
        htmlFilePath = os.path.join(self.htmlDirectory, htmlFilename)
        html = open(htmlFilePath).read()
        request = Request(url=url)
        response = TextResponse(url=url,
            request=request,
            body=html)
        scrapedItems = self.scraper.parse(response)
        new_requests = []
        items = []
        for scrapedItem in scrapedItems:
            if isinstance(scrapedItem, Request):
                request_url = scrapedItem.url
                if not self.is_url_allowed(request_url):
                    continue
                if request_url not in new_requests:
                    new_requests.append(request_url)
            else:
                items.append(scrapedItem)
        return json.dumps({'requests': new_requests, 'items': items})
    
    def is_url_allowed(self, url):
        for allowedDomain in self.scraper.allowed_domains:
            if allowedDomain in url:
                return True
        return False
 
if __name__ == '__main__':
    unittest.main()
