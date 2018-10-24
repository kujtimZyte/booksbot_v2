# -*- coding: utf-8 -*-
import requests
import os


# Get our settings
project_id = os.environ['SCRAPY_PROJECT_ID']
api_key = os.environ['SCRAPY_API_KEY']
main_url = 'https://app.scrapinghub.com/api/jobs/'
spider = 'news'

# List the current jobs
print('Listing the current jobs...')
jobs_url = main_url + 'list.json'
list_result = requests.get(jobs_url, auth=(api_key, ''), params={
    'project': project_id,
    'spider': spider,
    'state': 'running',
    'count': '1'
}).json()

# Stop the jobs
for job_id in list_result['jobs']:
    print('Stopping job {}'.format(job_id))
    stop_url = main_url + 'stop.json'
    stop_result = requests.post(stop_url, auth=(api_key, ''), data={
        'project': project_id,
        'job': job_id
    })

# Run a new job
run_url = main_url + 'run.json'
requests.post(run_url, auth=(api_key, ''), data={
    'project': project_id,
    'spider': spider
})
