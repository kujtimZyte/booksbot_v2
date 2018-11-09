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

    def test_bbc_homepage(self):
        self.check_fake_html_scrape(
            'bbc.com.html',
            'http://www.bbc.com',
            'bbc.com.json')

    def test_bbc_45973436(self):
        self.check_fake_html_scrape(
            'bbc-45973436.html',
            'https://www.bbc.com/news/world-us-canada-45973436',
            'bbc-45973436.json')

    def test_guardian_next_generation_2018_20_of_the_best_talents_at_premier_league_clubs(self):
        self.check_fake_html_scrape(
            'guardian-next-generation-2018-20-of-the-best-talents-at-premier-league-clubs.html',
            'https://www.theguardian.com/football/ng-interactive/2018/oct/10/next-generation-2018-20-of-the-best-talents-at-premier-league-clubs',
            'guardian-next-generation-2018-20-of-the-best-talents-at-premier-league-clubs.json')

    def test_cbc_homepage(self):
        self.check_fake_html_scrape(
            'cbc.ca.html',
            'https://www.cbc.ca/',
            'cbc.ca.json')

    def test_cbc_trump_pipe_bomb(self):
        self.check_fake_html_scrape(
            'cbc-trump-pipe-bomb.html',
            'https://www.cbc.ca/news/opinion/trump-pipe-bomb-1.4878980',
            'cbc-trump-pipe-bomb.json')

    def test_independent_homepage(self):
        self.check_fake_html_scrape(
            'independent.co.uk.html',
            'https://www.independent.co.uk/us',
            'independent.co.uk.json')

    def test_independent_bomb_arrest_live_cesar_sayoc_florida_update_nyc_bomber_cnn_trump_latest(self):
        self.check_fake_html_scrape(
            'independent-bomb-arrest-live-cesar-sayoc-florida-update-nyc-bomber-cnn-trump-latest.html',
            'https://www.independent.co.uk/news/world/americas/bomb-arrest-live-cesar-sayoc-florida-update-nyc-bomber-cnn-trump-latest-a8603651.html',
            'independent-bomb-arrest-live-cesar-sayoc-florida-update-nyc-bomber-cnn-trump-latest.json')

    def test_the_verge_homepage(self):
        self.check_fake_html_scrape(
            'theverge.com.html',
            'https://www.theverge.com/',
            'theverge.com.json')

    def test_the_verge_channel_zero_dream_door_syfy_horror_show(self):
        self.check_fake_html_scrape(
            'theverge-channel-zero-dream-door-syfy-horror-show.html',
            'https://www.theverge.com/2018/10/26/18022758/channel-zero-dream-door-syfy-horror-show',
            'theverge-channel-zero-dream-door-syfy-horror-show.json')

    def test_nytimes_homepage(self):
        self.check_fake_html_scrape(
            'nytimes.com.html',
            'https://www.nytimes.com/',
            'nytimes.com.json')

    def test_nytimes_cnn_cory_booker_pipe_bombs_sent(self):
        self.check_fake_html_scrape(
            'nytimes-cnn-cory-booker-pipe-bombs-sent.html',
            'https://www.nytimes.com/2018/10/26/nyregion/cnn-cory-booker-pipe-bombs-sent.html?action=click&module=Top%20Stories&pgtype=Homepage',
            'nytimes-cnn-cory-booker-pipe-bombs-sent.json')

    def test_abc_homepage(self):
        self.check_fake_html_scrape(
            'abc.net.au.html',
            'https://www.abc.net.au/news/',
            'abc.net.au.json')

    def test_abc_soaking_up_australias_drought_natural_sequence_farming(self):
        self.check_fake_html_scrape(
            'abc-soaking-up-australias-drought-natural-sequence-farming.html',
            'https://www.abc.net.au/news/2018-10-29/soaking-up-australias-drought-natural-sequence-farming/10312844',
            'abc-soaking-up-australias-drought-natural-sequence-farming.json')

    def test_stuff_homepage(self):
        self.check_fake_html_scrape(
            'stuff.co.nz.html',
            'https://www.stuff.co.nz/',
            'stuff.co.nz.json')

    def test_stuff_lion_air_jet_requested_return_to_airport_before_crash(self):
        self.check_fake_html_scrape(
            'stuff-lion-air-jet-requested-return-to-airport-before-crash.html',
            'https://www.stuff.co.nz/world/asia/108204710/lion-air-jet-requested-return-to-airport-before-crash',
            'stuff-lion-air-jet-requested-return-to-airport-before-crash.json')

    def test_thehill_homepage(self):
        self.check_fake_html_scrape(
            'thehill.com.html',
            'https://thehill.com',
            'thehill.com.json')

    def test_thehill_trump_says_he_will_sign_executive_order_banning_birthright(self):
        self.check_fake_html_scrape(
            'thehill-trump-says-he-will-sign-executive-order-banning-birthright.html',
            'https://thehill.com/homenews/administration/413770-trump-says-he-will-sign-executive-order-banning-birthright',
            'thehill-trump-says-he-will-sign-executive-order-banning-birthright.json')

    def test_washingtonpost_homepage(self):
        self.check_fake_html_scrape(
            'washingtonpost.com.html',
            'https://www.washingtonpost.com/',
            'washingtonpost.com.json')

    def test_washingtonpost_congressional_leaders_decline_to_join_trump_in_visit_to_pittsburgh_after_massacre(self):
        self.check_fake_html_scrape(
            'washingtonpost-congressional-leaders-decline-to-join-trump-in-visit-to-pittsburgh-after-massacre.html',
            'https://www.washingtonpost.com/politics/congressional-leaders-decline-to-join-trump-in-visit-to-pittsburgh-after-massacre/2018/10/30/34709010-dc4e-11e8-aa33-53bad9a881e8_story.html?utm_term=.d38742ee056c',
            'washingtonpost-congressional-leaders-decline-to-join-trump-in-visit-to-pittsburgh-after-massacre.json')

    def test_globalnews_homepage(self):
        self.check_fake_html_scrape(
            'globalnews.ca.html',
            'https://globalnews.ca/',
            'globalnews.ca.json')

    def test_globalnews_cleaning_up_albertas_oilpatch_could_cost_260_billion_regulatory_documents_warn(self):
        self.check_fake_html_scrape(
            'globalnews-cleaning-up-albertas-oilpatch-could-cost-260-billion-regulatory-documents-warn.html',
            'https://globalnews.ca/news/4617664/cleaning-up-albertas-oilpatch-could-cost-260-billion-regulatory-documents-warn/',
            'globalnews-cleaning-up-albertas-oilpatch-could-cost-260-billion-regulatory-documents-warn.json')

    def test_businessinsider_homepage(self):
        self.check_fake_html_scrape(
            'businessinsider.com.html',
            'https://www.businessinsider.com',
            'businessinsider.com.json')

    def test_businessinsider_central_american_migrants_have_a_message_for_trump(self):
        self.check_fake_html_scrape(
            'business-insider-central-american-migrants-have-a-message-for-trump.html',
            'https://www.businessinsider.com/central-american-migrants-have-a-message-for-trump-2018-11',
            'business-insider-central-american-migrants-have-a-message-for-trump.json')

    def test_nzherald_homepage(self):
        self.check_fake_html_scrape(
            'nzherald.co.nz.html',
            'https://www.nzherald.co.nz/',
            'nzherald.co.nz.json')

    def test_nzherald_12154083(self):
        self.check_fake_html_scrape(
            'nzherald-12154083.html',
            'https://www.nzherald.co.nz/sport/news/article.cfm?c_id=4&objectid=12154083',
            'nzherald-12154083.json')

    def test_huffingtonpost_homepage(self):
        self.check_fake_html_scrape(
            'huffingtonpost.com.html',
            'https://www.huffingtonpost.com/',
            'huffingtonpost.com.json')

    def test_huffingtonpost_sonny_perdue_cotton_pickin_important_ron_desantis_andrew_gillum(self):
        self.check_fake_html_scrape(
            'huffingtonpost-sonny-perdue-cotton-pickin-important-ron-desantis-andrew-gillum.html',
            'https://www.huffingtonpost.com/entry/sonny-perdue-cotton-pickin-important-ron-desantis-andrew-gillum_us_5bde4f84e4b09d43e31f83e3',
            'huffingtonpost-sonny-perdue-cotton-pickin-important-ron-desantis-andrew-gillum.json')

    def test_smh_homepage(self):
        self.check_fake_html_scrape(
            'smh.com.au.html',
            'https://www.smh.com.au',
            'smh.com.au.json')

    def test_smh_ghost_bus_the_scomo_express_hits_the_runway_rather_than_the_road(self):
        self.check_fake_html_scrape(
            'smh-ghost-bus-the-scomo-express-hits-the-runway-rather-than-the-road.html',
            'https://www.smh.com.au/politics/federal/ghost-bus-the-scomo-express-hits-the-runway-rather-than-the-road-20181105-p50e2g.html',
            'smh-ghost-bus-the-scomo-express-hits-the-runway-rather-than-the-road.json')

    def test_cnbc_homepage(self):
        self.check_fake_html_scrape(
            'cnbc.com.html',
            'https://www.cnbc.com/',
            'cnbc.com.json')

    def test_cnbc_heres_what_every_major_wall_street_firm_expects_from_the_election_and_how_to_play_it(self):
        self.check_fake_html_scrape(
            'cnbc-heres-what-every-major-wall-street-firm-expects-from-the-election-and-how-to-play-it.html',
            'https://www.cnbc.com/2018/11/06/heres-what-every-major-wall-street-firm-expects-from-the-election-and-how-to-play-it.html',
            'cnbc-heres-what-every-major-wall-street-firm-expects-from-the-election-and-how-to-play-it.json')

    def test_vice_homepage(self):
        self.check_fake_html_scrape(
            'vice.com.html',
            'https://www.vice.com/en_us',
            'vice.com.json')

    def test_vice_inside_an_underground_womens_mud_wrestling_ring_in_chicago(self):
        self.check_fake_html_scrape(
            'vice-inside-an-underground-womens-mud-wrestling-ring-in-chicago.html',
            'https://www.vice.com/en_us/article/9k49vz/inside-an-underground-womens-mud-wrestling-ring-in-chicago',
            'vice-inside-an-underground-womens-mud-wrestling-ring-in-chicago.json')

    def test_motherboard_homepage(self):
        self.check_fake_html_scrape(
            'motherboard.vice.com.html',
            'https://motherboard.vice.com/en_us',
            'motherboard.vice.com.json')

    def test_motherboard_my_gamer_brain_is_addicted_to_the_peloton_exercise_bike(self):
        self.check_fake_html_scrape(
            'motherboard-my-gamer-brain-is-addicted-to-the-peloton-exercise-bike.html',
            'https://motherboard.vice.com/en_us/article/vba4dx/my-gamer-brain-is-addicted-to-the-peloton-exercise-bike',
            'motherboard-my-gamer-brain-is-addicted-to-the-peloton-exercise-bike.json')

    def test_nbcnews_homepage(self):
        self.check_fake_html_scrape(
            'nbcnews.com.html',
            'https://www.nbcnews.com/',
            'nbcnews.com.json')

    def test_nbcnews_shooting_reported_borderline_bar_grill_thousand_oaks_california(self):
        self.check_fake_html_scrape(
            'nbcnews-shooting-reported-borderline-bar-grill-thousand-oaks-california.html',
            'https://www.nbcnews.com/news/us-news/shooting-reported-borderline-bar-grill-thousand-oaks-california-n933831',
            'nbcnews-shooting-reported-borderline-bar-grill-thousand-oaks-california.json')

    def test_apnews_homepage(self):
        self.check_fake_html_scrape(
            'apnews.com.html',
            'https://www.apnews.com',
            'apnews.com.json')

    def test_apnews_5133931a9d734dfcb38d44feec1ec9b6(self):
        self.check_fake_html_scrape(
            'apnews-5133931a9d734dfcb38d44feec1ec9b6.html',
            'https://www.apnews.com/5133931a9d734dfcb38d44feec1ec9b6',
            'apnews-5133931a9d734dfcb38d44feec1ec9b6.json')

    def check_fake_html_scrape(self, html_filename, url, json_filename):
        output_json = self.fake_html(html_filename, url)
        #open('output.json', 'w').write(output_json)
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
        return json.dumps({'requests': new_requests, 'items': items}, sort_keys=True, indent=4, separators=(',', ': '))
    
    def is_url_allowed(self, url):
        for allowedDomain in self.scraper.allowed_domains:
            if allowedDomain in url:
                return True
        return False
 
if __name__ == '__main__':
    unittest.main()
