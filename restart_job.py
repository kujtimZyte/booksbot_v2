# -*- coding: utf-8 -*-
import requests
import os
import scrapinghub
import time


project_id = os.environ['SCRAPY_PROJECT_ID']
api_key = os.environ['SCRAPY_API_KEY']
spider_name = 'news'

print('Connecting to scrapinghub')
client = scrapinghub.ScrapinghubClient(api_key)
print('Connecting to project')
project = client.get_project(project_id)
print('Cancelling running jobs')
for job in project.jobs.iter(state='running'):
    client.get_job(job['key']).cancel()
while project.jobs.count(state='running') > 0:
    print('Waiting for job to cancel...')
    time.sleep(1)
print('Running new job')
project.jobs.run(spider=spider_name)
while project.jobs.count(state='running') == 0:
    print('Waiting for job to run...')
    time.sleep(1)
print('Successfully running new job')
