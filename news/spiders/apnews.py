# -*- coding: utf-8 -*-
"""Parser for the Associated Press News website"""
import os
import html2text
from bs4 import BeautifulSoup
from .article import Article, Image, Video, Author
from .common import strip_query_from_url, extract_metadata, execute_script


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


def article_from_contents_value(contents_value, meta_tags):
    """Parses the article from the contents value"""
    article = Article()
    for tag_obj in contents_value['tagObjs']:
        article.tags.append(tag_obj['name'])
    modified_time = contents_value['updated']
    article.time.set_modified_time(modified_time)
    published_time = contents_value['published']
    if not published_time:
        published_time = modified_time
    article.time.set_published_time(published_time)
    article.info.url = contents_value['localLinkUrl']
    article.info.title = contents_value['title']
    article.info.description = contents_value['headline']
    for media in contents_value['media']:
        image = Image()
        max_value = max(media['imageRenderedSizes'])
        image.url = os.path.join(
            media['gcsBaseUrl'],
            str(max_value) + media['imageFileExtension'])
        image.mime_type = media['imageMimeType']
        image.alt = media['altText']
        image.title = media['flattenedCaption']
        article.images.images.append(image)
        if 'type' in media:
            if media['type'] == 'YouTube':
                video = Video()
                video.url = 'https://www.youtube.com/watch?v=' + media['externalId']
                video.mime_type = media['videoMimeType']
                article.videos.videos.append(video)
    if contents_value['bylines']:
        for name in contents_value['bylines'].replace('By ', '').split(' and '):
            author = Author()
            author.name = name
            article.authors.append(author)
    article.publisher.twitter.card = meta_tags['twitter:card']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.twitter.image = meta_tags['twitter:image']
    if 'twitter:image:alt' in meta_tags:
        article.publisher.twitter.image_alt = meta_tags['twitter:image:alt']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.twitter.description = meta_tags['twitter:description']
    article.publisher.facebook.app_id = meta_tags['fb:app_id']
    article.text.set_markdown_text(html2text.html2text(contents_value['storyHTML']))
    return article


def apnews_parse(response):
    """Parses the response from a Associated Press News website"""
    link_id = apnews_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tags = extract_metadata(response)
    for script_tag in soup.findAll('script'):
        context = execute_script(script_tag)
        if not hasattr(context, 'window'):
            continue
        if hasattr(context.window, 'titanium-state'):
            state = context.window['titanium-state']
            content = state['content']
            contents = content['contents']
            for contents_key in contents:
                contents_value = contents[contents_key]
                article = article_from_contents_value(contents_value, meta_tags)
                return article.json(), link_id
    return None, link_id


def apnews_url_filter(_url):
    """Filters URLs in the AP News domain"""
    return True
