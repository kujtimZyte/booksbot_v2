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

## Contributing :mailbox_with_mail:
Contributions are welcomed, have a look at the [CONTRIBUTING.md](CONTRIBUTING.md) document for more information.

## License :memo:
The project is available under the [MIT](https://opensource.org/licenses/MIT) license.
