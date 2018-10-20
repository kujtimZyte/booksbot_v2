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

| News Site                   | Last Updated      | Status |
| --------------------------- |:-----------------:| ------:|
| [CNN](https://www.cnn.com/) | 20th October 2018 | Stable |

## Dependencies :globe_with_meridians:
* [scrapy](https://scrapy.org/)
* [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash)

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

### Cloud
This repository contains [CircleCI](https://circleci.com) builds that automatically deploy on master. You can configure this with the following environment variables:
| Name              | Value                                                                                         |
| ----------------- | ---------------------------------------------------------------------------------------------:|
| SCRAPY_API_KEY    | Your API key for [Scrapy Cloud](https://scrapinghub.com/scrapy-cloud)                         |
| SCRAPY_PROJECT_ID | Your Project ID for [Scrapy Cloud](https://scrapinghub.com/scrapy-cloud)                      |
| SPLASH_URL        | The URL pointing to your [Splash Instance](https://scrapinghub.com/splash)                    |
| NEWS_HTTP_USER    | The username to use for authenticating your [Splash Instance](https://scrapinghub.com/splash) |
| NEWS_HTTP_PASS    | The password to use for authenticating your [Splash Instance](https://scrapinghub.com/splash) |

## Contributing :mailbox_with_mail:
Contributions are welcomed, have a look at the [CONTRIBUTING.md](CONTRIBUTING.md) document for more information.

## License :memo:
The project is available under the [MIT](https://opensource.org/licenses/MIT) license.
