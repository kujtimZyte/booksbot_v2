<img alt="scraper" src="scraper.png" width="100%" max-width="888">

[![CircleCI](https://circleci.com/gh/dust10141/scraper/tree/master.svg?style=svg)](https://circleci.com/gh/dust10141/scraper/tree/master)

A spider for crawling news sites.

## Raison D'être :thought_balloon:
This program was made to solve the problem of crawling an array of popular news sites, extracting the relevant information and dumping it to a GCS bucket.

## Architecture :triangular_ruler:
`scraper` aims to have thorough testing for all the sites it supports. It contains various layers that are responsible for choosing the correct parser for the content.
The layer design is as follows:
- **The Main Parser**, which takes a response, and forwards it to the appropriate domain parser.
- **The Domain Parser**, which takes a response for a particular, and forwards it to the appropriate version parser.
- **The Version Parser**, parses a response for a particular version of a domain.

The support table looks like so:

| News Site                                                           | Last Updated       | Status |
| ------------------------------------------------------------------- |:------------------:| ------:|
| [Australian Broadcasting Corporation](https://www.abc.net.au/news/) | 19th January 2019  | Stable |
| [Associated Press News](https://www.apnews.com)                     | 22nd January 2019  | Stable |
| [Ars Technica](https://arstechnica.com)                             | 23rd January 2019  | Stable |
| [BBC](http://www.bbc.com)                                           | 25th January 2019  | Stable |
| [Bloomberg](https://www.bloomberg.com/)                             | 27th January 2019  | Stable |
| [Business Insider](https://www.businessinsider.com/)                | 24th February 2019 | Stable |
| [CBC](https://www.cbc.ca/news/)                                     | 24th February 2019 | Stable |
| [CBS News](https://www.cbsnews.com/)                                | 25th February 2019 | Stable |
| [CNBC](https://www.cnbc.com/)                                       | 26th February 2019 | Stable |
| [CNN](https://www.cnn.com/)                                         | 27th February 2019 | Stable |
| [CTVNews](https://www.ctvnews.ca/)                                  | 28th February 2019 | Stable |
| [Fox News](https://www.foxnews.com/)                                | 2nd March 2019     | Stable |
| [Global News](https://globalnews.ca/)                               | 2nd March 2019     | Stable |
| [Guardian](https://www.theguardian.com/international?INTCMP=CE_INT) | 3rd March 2019     | Stable |
| [The Huffington Post](https://www.huffingtonpost.com)               | 4th March 2019     | Stable |
| [The Independent](https://www.independent.co.uk)                    | 5th March 2019     | Stable |
| [NBC News](https://www.nbcnews.com/)                                | 6th March 2019     | Stable |
| [Vice](https://www.vice.com/en_us)                                  | 7th March 2019     | Stable |
| [Motherboard](https://motherboard.vice.com/en_us)                   | 7th March 2019     | Stable |
| [Newsweek](https://www.newsweek.com/)                               | 8th March 2019     | Stable |

## Dependencies :globe_with_meridians:
* [scrapy](https://scrapy.org/)
* [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash)
* [google-cloud-storage](https://cloud.google.com/storage/docs/reference/libraries)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [python-dateutil](http://labix.org/python-dateutil)
* [html2text](http://www.aaronsw.com/2002/html2text/)
* [markdown](https://python-markdown.github.io/)
* [requests](http://docs.python-requests.org/en/master/)
* [js2py](https://github.com/PiotrDabkowski/Js2Py)
* [mock](https://docs.python.org/3/library/unittest.mock.html)
* [html5lib](https://pypi.org/project/html5lib/)

## Installation :inbox_tray:
The chief requirements of any installation are based off scrapy and splash, see below for local and cloud based options.

### Locally
1. Install [docker](https://www.docker.com/)
2. Pull the splash docker image:
```bash
docker pull scrapinghub/splash
```
3. Run the splash docker image:
```bash
docker run -p 8050:8050 -p 5023:5023 scrapinghub/splash
```
4. Install the requirements:
```bash
pip install -r requirements.txt
```
5. Run the crawler:
```bash
scrapy crawl news
```
6. Run the tests:
```bash
python -m unittest discover -v
```

### Cloud
This repository contains [CircleCI](https://circleci.com) builds that automatically deploy on master. You can configure this with the following environment variables:

| Name                     | Value                                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------- |
| SCRAPY_API_KEY           | Your API key for [Scrapy Cloud](https://scrapinghub.com/scrapy-cloud)                         |
| SCRAPY_PROJECT_ID        | Your Project ID for [Scrapy Cloud](https://scrapinghub.com/scrapy-cloud)                      |
| NEWS_HTTP_AUTH_USER      | The username for [Splash Cloud](https://scrapinghub.com/splash)                               |
| GCS_BUCKET_NAME          | The Google Cloud Storage Bucket to post to                                                    |
| GCP_PROJECT              | The Google Cloud Project to post the items to                                                 |
| GCP_PRIVATE_KEY_ID       | The private key ID for the google cloud service account                                       |
| GCP_PRIVATE_KEY          | The private key for the google cloud service account                                          |
| GCP_CLIENT_EMAIL         | The client email for the google cloud service account                                         |
| GCP_CLIENT_ID            | The client ID for the google cloud service account                                            |
| GCP_CLIENT_X509_CERT_URL | The X509 Certificate URL for the google cloud service account                                 |

Once these are filled in, you can run the `deploy_files.sh` script to create the necessary settings before deployment. If you wish to automatically run the job on [Scraping Hub](https://scrapinghub.com) you can also run `restart_job.py`.

## Usage example :eyes:
Once this system is running it will post JSON files to the GCS bucket defined. The standard format will look like so:
```json
{
    "items": [
        {
            "article": {
                "author": {
                    "url": "https://www.abc.net.au/news/winsome-denyer/7991864"
                },
                "images": {
                    "images": [
                        {
                            "last_modified": 1540753477.0,
                            "mime_type": "image/jpeg",
                            "size": 78902,
                            "url": "https://www.abc.net.au/news/image/10370730-3x2-940x627.jpg"
                        }
                    ],
                    "thumbnail": {
                        "height": 394,
                        "last_modified": 1540753487.0,
                        "mime_type": "image/jpeg",
                        "size": 71935,
                        "url": "https://www.abc.net.au/news/image/10370752-16x9-700x394.jpg",
                        "width": 700
                    }
                },
                "info": {
                    "description": "Is natural sequence farming the secret to restoring our water-starved continent? For more than a decade, two farmers have shown that parched landscapes can be revived. And finally Canberra's listening.",
                    "genre": "News & Current Affairs",
                    "title": "'We can fix all this': Could this be the solution to Australia's drought crisis?",
                    "url": "https://www.abc.net.au/news/2018-10-29/soaking-up-australias-drought-natural-sequence-farming/10312844"
                },
                "location": {
                    "latitude": -35.2587,
                    "longitude": 149.4382
                },
                "publisher": {
                    "facebook": {
                        "page_id": "72924719987",
                        "url": "https://www.facebook.com/abcnews.au"
                    },
                    "organisation": "Australian Broadcasting Corporation",
                    "twitter": {
                        "card": "summary",
                        "handle": "@ABCNews",
                        "image": "https://www.abc.net.au/news/image/10370752-16x9-700x394.jpg"
                    }
                },
                "tags": [
                    "drought",
                    "rural",
                    "sustainable-and-alternative-farming",
                    "beef-cattle",
                    "livestock"
                ],
                "text": {
                    "markdown": "# Soaking up Australia's drought\n\nIs Natural Sequence Farming the secret to restoring our water-starved\ncontinent? For more than a decade, two farmers have shown that parched\nlandscapes can be revived. And finally Canberra's listening.\n\n[Australian Story](/austory/)",
                    "text": "Soaking up Australia's drought\nIs Natural Sequence Farming the secret to restoring our water-starved\ncontinent? For more than a decade, two farmers have shown that parched\nlandscapes can be revived. And finally Canberra's listening."
                },
                "time": {
                    "modified_time": 1540768541.0,
                    "published_time": 1540753388.0
                },
                "videos": {
                    "videos": [
                        {
                            "bitrate": 469,
                            "codec": "AVC",
                            "etag": "\"6209cb-5788a25f37d1b\"",
                            "height": 288,
                            "mime_type": "video/mp4",
                            "size": 6425035,
                            "url": "https://abcmedia.akamaized.net/news/austory/video/201810/ASTb_HopeSprings_1910_512k.mp4",
                            "width": 512
                        }
                    ]
                }
            },
            "url": "https://www.abc.net.au/news/2018-10-29/soaking-up-australias-drought-natural-sequence-farming/10312844"
        }
    ],
    "requests": [
        "https://www.abc.net.au/news/2018-10-29/soaking-up-australias-drought-natural-sequence-farming/10312844#main_content"
    ]
}
```
The seemingly random metadata tags come from the `meta` tags keys and values.

## License :memo:
The project is available under the [GPL 3.0](https://opensource.org/licenses/GPL-3.0) license.

## Acknowledgements

- Icon in README banner is [scraper](https://thenounproject.com/search/?q=scraper&i=474203) by Philipp Lehmann from the Noun Project.
