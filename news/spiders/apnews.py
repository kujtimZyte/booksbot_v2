# -*- coding: utf-8 -*-
"""Parser for the Associated Press News website"""
import os
from bs4 import BeautifulSoup
import html2text
import js2py
from .article import Article, Image, Video, Author
from .common import strip_query_from_url, extract_metadata


def apnews_url_parse(url):
    """Parses the URL from an AP News website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) == 2:
        return None
    last_path = url_split[-1]
    if len(last_path) != 32:
        return None
    return last_path


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
    remove_items = [
        {
            'tag': 'div',
            'meta': {
                'class': 'SocialShare'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'RelatedTopics'
            }
        }
    ]
    for remove_item in remove_items:
        for tag in soup.findAll(remove_item['tag'], remove_item['meta']):
            tag.decompose()


def apnews_parse(response):
    """Parses the response from a Associated Press News website"""
    link_id = apnews_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tags = extract_metadata(response)
    for script_tag in soup.findAll('script'):
        if not script_tag.text:
            continue
        try:
            context = js2py.EvalJs()
            context.execute(script_tag.text)
            if not hasattr(context, 'window'):
                continue
            if hasattr(context.window, 'titanium-state'):
                state = context.window['titanium-state']
                content = state['content']
                contents = content['contents']
                for contents_key in contents:
                    contents_value = contents[contents_key]
                    article = Article()
                    for tagObj in contents_value['tagObjs']:
                        article.tags.append(tagObj['name'])
                    article.time.set_published_time(contents_value['published'])
                    article.time.set_modified_time(contents_value['updated'])
                    article.info.url = contents_value['localLinkUrl']
                    article.info.title = contents_value['title']
                    article.info.description = contents_value['headline']
                    for media in contents_value['media']:
                        image = Image()
                        max_value = max(media['imageRenderedSizes'])
                        image.url = os.path.join(media['gcsBaseUrl'], str(max_value) + media['imageFileExtension'])
                        image.mime_type = media['imageMimeType']
                        image.alt = media['altText']
                        image.title = media['flattenedCaption']
                        article.images.images.append(image)
                        if media['type'] == 'YouTube':
                            video = Video()
                            video.url = 'https://www.youtube.com/watch?v=' + media['externalId']
                            video.mime_type = media['videoMimeType']
                            article.videos.videos.append(video)
                    for name in contents_value['bylines'].replace('By ', '').split(' and '):
                        author = Author()
                        author.name = name
                        article.authors.append(author)
                    article.publisher.twitter.card = meta_tags['twitter:card']
                    article.publisher.twitter.handle = meta_tags['twitter:site']
                    article.publisher.twitter.image = meta_tags['twitter:image']
                    article.publisher.twitter.image_alt = meta_tags['twitter:image:alt']
                    article.publisher.twitter.title = meta_tags['twitter:title']
                    article.publisher.twitter.description = meta_tags['twitter:description']
                    article.publisher.facebook.app_id = meta_tags['fb:app_id']
                    article.text.set_markdown(html2text.html2text(contents_value['storyHTML']))
                    return article.json(), link_id
        except js2py.PyJsException:
            continue
    return None, link_id


def apnews_url_filter(url):
    """Filters URLs in the AP News domain"""
    return True
