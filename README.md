# scraper

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

| News Site                                                           | Last Updated      | Status |
| ------------------------------------------------------------------- |:-----------------:| ------:|
| [CNN](https://www.cnn.com/)                                         | 20th October 2018 | Stable |
| [Reuters](https://www.reuters.com/)                                 | 22nd October 2018 | Stable |
| [Guardian](https://www.theguardian.com/international?INTCMP=CE_INT) | 23rd October 2018 | Stable |
| [BBC](http://www.bbc.com)                                           | 24th October 2018 | Stable |
| [CBC](https://www.cbc.ca/)                                          | 26th October 2018 | Stable |
| [The Independent](https://www.independent.co.uk)                    | 27th October 2018 | Stable |
| [The Verge](https://www.theverge.com/)                              | 27th October 2018 | Stable |
| [The New York Times](https://www.nytimes.com/)                      | 27th October 2018 | Stable |
| [Australian Broadcasting Corporation](https://www.abc.net.au/news/) | 28th October 2018 | Stable |
| [stuff](https://www.stuff.co.nz/)                                   | 29th October 2018 | Stable |
| [The Hill](https://thehill.com)                                     | 30th October 2018 | Stable |
| [The Washington Post](https://www.washingtonpost.com)               | 31st October 2018 | Stable |
| [Global News](https://globalnews.ca/)                               | 1st November 2018 | Stable |
| [Business Insider](https://www.businessinsider.com)                 | 3rd November 2018 | Stable |
| [The New Zealand Herald](https://www.nzherald.co.nz/)               | 3rd November 2018 | Stable |
| [The Huffington Post](https://www.huffingtonpost.com)               | 4th November 2018 | Stable |
| [The Sydney Morning Herald](https://www.smh.com.au)                 | 5th November 2018 | Stable |
| [CNBC](https://www.cnbc.com)                                        | 6th November 2018 | Stable |
| [Vice](https://www.vice.com/en_us)                                  | 7th November 2018 | Stable |
| [Motherboard](https://motherboard.vice.com/en_us)                   | 7th November 2018 | Stable |
| [NBC News](https://www.nbcnews.com/)                                | 8th November 2018 | Stable |

## Dependencies :globe_with_meridians:
* [scrapy](https://scrapy.org/)
* [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash)
* [google-cloud-storage](https://cloud.google.com/storage/docs/reference/libraries)

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
    "items":[
        {
            "url":"https://www.theguardian.com/world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas",
            "items":[
                {
                    "articleBody":[
                        {
                            "text":"Donald Trump has said that the Saudi operation to kill"
                        },
                        {
                            "text":"Jamal Khashoggi",
                            "link":"https://www.theguardian.com/world/jamal-khashoggi"
                        },
                        {
                            "text":"in Riyadh\u2019s consulate in Istanbul led to \u201cone of the worst cover-ups\u201d in history, as the US said it would sanction officials who were implicated in the writer\u2019s death."
                        },
                        {
                            "text":"Twenty-one Saudis will have their US visas revoked or be made ineligible for US visas over the journalist\u2019s killing, a state department spokeswoman, Heather Nauert, said on Tuesday."
                        }
                    ],
                    "twitter:app:url:ipad":"gnmguardian://world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas?contenttype=Article&source=twitter",
                    "og:image:height":"720",
                    "application-name":"The Guardian",
                    "twitter:app:name:googleplay":"The Guardian",
                    "twitter:image":"https://i.guim.co.uk/img/media/6e532981cf34af9609e41032d5c5d9102c6ff0d6/0_233_3500_2101/master/3500.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&s=990d00212b56936bfe2a680740695c6e",
                    "HandheldFriendly":"True",
                    "fb:app_id":"180444840287",
                    "twitter:app:url:googleplay":"guardian://www.theguardian.com/world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas",
                    "twitter:site":"@guardian",
                    "article:publisher":"https://www.facebook.com/theguardian",
                    "twitter:dnt":"on",
                    "al:ios:url":"gnmguardian://world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas?contenttype=Article&source=applinks",
                    "og:url":"http://www.theguardian.com/world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas",
                    "twitter:app:url:iphone":"gnmguardian://world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas?contenttype=Article&source=twitter",
                    "og:image":"https://i.guim.co.uk/img/media/6e532981cf34af9609e41032d5c5d9102c6ff0d6/0_233_3500_2101/master/3500.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&s=990d00212b56936bfe2a680740695c6e",
                    "msapplication-TileColor":"#e7edef",
                    "al:ios:app_store_id":"409128287",
                    "author":"Bethan McKernan",
                    "description":"US curbs 21 Saudi officials\u2019 visas and mulls more sanctions, with Pompeo adding: \u2018These penalties will not be the last word\u2019",
                    "og:type":"article",
                    "apple-itunes-app":"app-id=409128287, app-argument=https://www.theguardian.com/world/2018/oct/23/jamal-khashoggi-trump-cover-up-sanctions-visas, affiliate-data=ct=newsmartappbanner&pt=304191",
                    "theme-color":"#e7edef",
                    "article:modified_time":"2018-10-23T22:43:42.000Z",
                    "og:title":"Jamal Khashoggi: Trump says Saudi cover-up was 'one of worst' in history",
                    "twitter:app:id:ipad":"409128287",
                    "article:tag":"Jamal Khashoggi,US foreign policy,Saudi Arabia,World news,US news,Middle East and North Africa,Mike Pompeo,Donald Trump,Turkey,Recep Tayyip Erdo\u011fan",
                    "thumbnail":"https://i.guim.co.uk/img/media/6e532981cf34af9609e41032d5c5d9102c6ff0d6/0_233_3500_2101/master/3500.jpg?width=620&quality=85&auto=format&fit=max&s=904b3aef5c9263fc950eb0ee29c7743f",
                    "fb:pages":"516977308337360",
                    "article:section":"World news",
                    "news_keywords":"Jamal Khashoggi,US foreign policy,Saudi Arabia,World news,US news,Middle East and North Africa,Mike Pompeo,Donald Trump,Turkey,Recep Tayyip Erdo\u011fan",
                    "twitter:app:name:iphone":"The Guardian",
                    "article:author":"https://www.theguardian.com/profile/bethan-mckernan",
                    "twitter:app:name:ipad":"The Guardian",
                    "msapplication-TileImage":"https://assets.guim.co.uk/images/favicons/77beb32f01ee0157ec193e09e4e18c4e/windows_tile_144_b.png",
                    "al:ios:app_name":"The Guardian",
                    "imgs":[
                        "https://i.guim.co.uk/img/media/efd4b0da768248d47fc1c3da23dfc922bc61db26/100_66_1135_681/master/1135.png?width=300&quality=85&auto=format&fit=max&s=d6dc6e97579cb5e178c28c02012a9c31",
                        "https://i.guim.co.uk/img/media/1cb1179ad6b0ff0d187a4c94e7f7484a91b81839/22_176_4072_2443/master/4072.jpg?width=300&quality=85&auto=format&fit=max&s=53cb811e25f6635912958aeec4923f58"
                    ],
                    "twitter:app:id:googleplay":"com.guardian",
                    "og:image:width":"1200",
                    "article:published_time":"2018-10-23T22:04:24.000Z",
                    "twitter:app:id:iphone":"409128287",
                    "viewport":"width=device-width,minimum-scale=1,initial-scale=1",
                    "og:site_name":"the Guardian",
                    "twitter:card":"summary_large_image",
                    "apple-mobile-web-app-title":"Guardian",
                    "og:description":"US curbs 21 Saudi officials\u2019 visas and mulls more sanctions, with Pompeo adding: \u2018These penalties will not be the last word\u2019",
                    "null":"2018-10-23T18:43:42-0400",
                    "keywords":"Jamal Khashoggi,US foreign policy,Saudi Arabia,World news,US news,Middle East and North Africa,Mike Pompeo,Donald Trump,Turkey,Recep Tayyip Erdo\u011fan",
                    "format-detection":"telephone=no"
                }
            ]
        }
    ],
    "requests":[
        "https://www.theguardian.com/football/live/2018/oct/23/manchester-united-v-juventus-champions-league-live",
        "https://www.theguardian.com/film/2018/oct/23/bohemian-rhapsody-review-freddie-mercury-biopic-bites-the-dust"
    ]
}
```
The seemingly random metadata tags come from the `meta` tags keys and values.

## License :memo:
The project is available under the [MIT](https://opensource.org/licenses/MIT) license.
