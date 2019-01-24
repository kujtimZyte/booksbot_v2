import unittest
from news.spiders.news import NewsSpider
import os
from scrapy.http import TextResponse, Request
import json
import mock

 
def mocked_requests_head(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, headers):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = headers


        def json(self):
            return self.json_data


    return MockResponse(None, 200, {
        'Content-Type': 'image/jpeg',
        'Last-Modified': 'Fri, 19 Oct 2018 00:40:21 GMT',
        'ETag': '"6209cb-5788a25f37d1b"',
        'Content-Length': '6425035'
    })


class TestNewsSpider(unittest.TestCase):
 
    def setUp(self):
        self.scraper = NewsSpider()
        self.htmlDirectory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_html_files')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_homepage(self, mock_head):
        self.check_fake_html_scrape(
            'abc.net.au.html',
            'https://www.abc.net.au/news/',
            'abc.net.au.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_soaking_up_australias_drought_natural_sequence_farming(self, mock_head):
        self.check_fake_html_scrape(
            'abc-soaking-up-australias-drought-natural-sequence-farming.html',
            'https://www.abc.net.au/news/2018-10-29/soaking-up-australias-drought-natural-sequence-farming/10312844',
            'abc-soaking-up-australias-drought-natural-sequence-farming.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_cctv_footage_shows_police_officer_assaulting_man(self, mock_head):
        self.check_fake_html_scrape(
            'abc-cctv-footage-shows-police-officer-assaulting-man.html',
            'https://www.abc.net.au/news/2019-01-21/cctv-footage-shows-police-officer-assaulting-man/10729284',
            'abc-cctv-footage-shows-police-officer-assaulting-man.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_greg_inglis_remorseful_for_very_poor_decision(self, mock_head):
        self.check_fake_html_scrape(
            'abc-greg-inglis-remorseful-for-very-poor-decision.html',
            'https://www.abc.net.au/news/2019-01-14/greg-inglis-remorseful-for-very-poor-decision/10714166',
            'abc-greg-inglis-remorseful-for-very-poor-decision.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_the_drum_monday_january_21(self, mock_head):
        self.check_fake_html_scrape(
            'abc-the-drum-monday-january-21.html',
            'https://www.abc.net.au/news/2019-01-21/the-drum-monday-january-21/10733656',
            'abc-the-drum-monday-january-21.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_why_the_results_in_wentworth_narrowed(self, mock_head):
        self.check_fake_html_scrape(
            'abc-why-the-results-in-wentworth-narrowed.html',
            'https://www.abc.net.au/news/2018-11-05/why-the-results-in-wentworth-narrowed/10446090',
            'abc-why-the-results-in-wentworth-narrowed.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_hockeyroo_kathryn_slattery_from_olympic_hockey_to_harvest(self, mock_head):
        self.check_fake_html_scrape(
            'abc-hockeyroo-kathryn-slattery-from-olympic-hockey-to-harvest.html',
            'https://www.abc.net.au/news/rural/2019-01-10/hockeyroo-kathryn-slattery-from-olympic-hockey-to-harvest/10700428',
            'abc-hockeyroo-kathryn-slattery-from-olympic-hockey-to-harvest.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_fast_food_and_your_brain(self, mock_head):
        self.check_fake_html_scrape(
            'abc-fast-food-and-your-brain.html',
            'https://www.abc.net.au/radionational/programs/greatmomentsinscience/fast-food-and-your-brain/10550528',
            'abc-fast-food-and-your-brain.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_nancy_pelosi_arrives_at_capitol_building_after_meeting_withh_don(self, mock_head):
        self.check_fake_html_scrape(
            'abc-nancy-pelosi-arrives-at-capitol-building-after-meeting-with-don.html',
            'https://www.abc.net.au/news/2019-01-19/nancy-pelosi-arrives-at-capitol-building-after-meeting-with-don/10728922',
            'abc-nancy-pelosi-arrives-at-capitol-building-after-meeting-with-don.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_abu_barak_bashir_must_never_be_able_to_incite_terrorism_again(self, mock_head):
        self.check_fake_html_scrape(
            'abc-abu-barak-bashir-must-never-be-able-to-incite-terrorism-again.html',
            'https://www.abc.net.au/radio/programs/am/abu-barak-bashir-must-never-be-able-to-incite-terrorism-again:fm/10738760',
            'abc-abu-barak-bashir-must-never-be-able-to-incite-terrorism-again.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_apnews_homepage(self, mock_head):
        self.check_fake_html_scrape(
            'apnews.com.html',
            'https://www.apnews.com',
            'apnews.com.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_apnews_5133931a9d734dfcb38d44feec1ec9b6(self, mock_head):
        self.check_fake_html_scrape(
            'apnews-5133931a9d734dfcb38d44feec1ec9b6.html',
            'https://www.apnews.com/5133931a9d734dfcb38d44feec1ec9b6',
            'apnews-5133931a9d734dfcb38d44feec1ec9b6.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_apnews_417eda5edd98430f948fd736f8260ae0(self, mock_head):
        self.check_fake_html_scrape(
            'apnews-417eda5edd98430f948fd736f8260ae0.html',
            'https://www.apnews.com/417eda5edd98430f948fd736f8260ae0',
            'apnews-417eda5edd98430f948fd736f8260ae0.json')


    @mock.patch('requests.head', side_effect=mocked_requests_head)
    def test_abc_the_big_dry_see_us_hear_us_help_us(self, mock_head):
        self.check_fake_html_scrape(
            'abc-the-big-dry-see-us-hear-us-help-us.html',
            'https://www.abc.net.au/news/rural/2018-07-29/the-big-dry-see-us-hear-us-help-us/10030010',
            'abc-the-big-dry-see-us-hear-us-help-us.json')


    def check_fake_html_scrape(self, html_filename, url, json_filename):
        output_json = self.fake_html(html_filename, url)
        open('output.json', 'w').write(output_json)
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
        new_requests = []
        items = []
        scrapedItems = self.scraper.parse(response)
        for scrapedItem in scrapedItems:
            if isinstance(scrapedItem, Request):
                request_url = scrapedItem.url
                if not self.is_url_allowed(request_url):
                    continue
                if request_url not in new_requests:
                    new_requests.append(request_url)
            else:
                items.append(scrapedItem)
        return json.dumps({'requests': new_requests, 'items': items}, sort_keys=True, indent=4, separators=(',', ': '))


    def is_url_allowed(self, url):
        for allowedDomain in self.scraper.allowed_domains:
            if allowedDomain in url:
                return True
        return False
 

if __name__ == '__main__':
    unittest.main()
