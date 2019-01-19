# -*- coding: utf-8 -*-
"""Structure for creating an article representation"""
import datetime
from dateutil import parser
import requests
from .common import markdown_to_plaintext


def timecode_from_datetime(datetime_obj):
    utc_naive  = datetime_obj.replace(tzinfo=None) - datetime_obj.utcoffset()
    return (utc_naive - datetime.datetime(1970, 1, 1)).total_seconds()


def url_head_headers(url):
    r = requests.head(url, timeout=5)
    return r.headers



class ArticleTime:
    published_time = None
    modified_time = None


    def json(self):
        time_json = {}
        if self.published_time:
            time_json['published_time'] = timecode_from_datetime(self.published_time)
        if self.modified_time:
            time_json['modified_time'] = timecode_from_datetime(self.modified_time)
        return time_json


class Info:
    genre = None
    url = None
    title = None
    description = None


    def json(self):
        info_json = {}
        if self.genre:
            info_json['genre'] = self.genre
        if self.url:
            info_json['url'] = self.url
        if self.title:
            info_json['title'] = self.title
        if self.description:
            info_json['description'] = self.description
        return info_json


class Image:
    url = None
    width = None
    height = None
    mime_type = None
    last_modified = None
    size = None


    def _fill(self):
        if not self.url:
            return
        headers = url_head_headers(self.url)
        if 'Last-Modified' in headers:
            self.last_modified = timecode_from_datetime(parser.parse(headers['Last-Modified']))
        if 'Content-Length' in headers:
            self.size = int(headers['Content-Length'])
        if 'Content-Type' in headers:
            self.mime_type = headers['Content-Type']


    def json(self):
        self._fill()
        image_json = {}
        if self.url:
            image_json['url'] = self.url
        if self.width:
            image_json['width'] = int(self.width)
        if self.height:
            image_json['height'] = int(self.height)
        if self.mime_type:
            image_json['mime_type'] = self.mime_type
        if self.last_modified:
            image_json['last_modified'] = self.last_modified
        if self.size:
            image_json['size'] = self.size
        return image_json


class Images:
    thumbnail = Image()
    images = []


    def json(self):
        images_json  = {}
        if self.thumbnail:
            images_json['thumbnail'] =  self.thumbnail.json()
        if self.images:
            images_json['images'] = [x.json() for x in self.images]
        return images_json


class Location:
    latitude = None
    longitude = None


    def json(self):
        location_info = {}
        if self.latitude:
            location_info['latitude'] = float(self.latitude)
        if self.longitude:
            location_info['longitude'] = float(self.longitude)
        return location_info


class Author:
    url = None


    def json(self):
        author_info = {}
        if self.url:
            author_info['url'] = self.url
        return author_info


class Facebook:
    url = None
    page_id = None


    def json(self):
        facebook_info = {}
        if self.url:
            facebook_info['url'] = self.url
        if self.page_id:
            facebook_info['page_id'] = self.page_id
        return facebook_info


class Twitter:
    card = None
    image = None
    handle = None


    def json(self):
        twitter_info = {}
        if self.card:
            twitter_info['card'] = self.card
        if self.image:
            twitter_info['image']  = self.image
        if self.handle:
            twitter_info['handle'] = self.handle
        return twitter_info


class Publisher:
    facebook = Facebook()
    twitter = Twitter()
    organisation = None


    def json(self):
        publisher_info = {}
        if self.facebook:
            publisher_info['facebook'] = self.facebook.json()
        if self.twitter:
            publisher_info['twitter'] = self.twitter.json()
        if self.organisation:
            publisher_info['organisation'] = self.organisation
        return publisher_info


class Text:
    markdown = None


    def json(self):
        text_info = {}
        if self.markdown:
            text_info['markdown'] = self.markdown
            text_info['text'] = markdown_to_plaintext(self.markdown)
        return text_info


class Video:
    url = None
    mime_type = None
    codec = None
    bitrate = None
    width = None
    height = None
    size = None
    last_modified = None
    etag = None


    def _fill(self):
        if not self.url:
            return
        headers = url_head_headers(self.url)
        if 'Last-Modified' in headers:
            self.last_modified = timecode_from_datetime(parser.parse(headers['Last-Modified']))
        if 'Content-Length' in headers:
            self.size = int(headers['Content-Length'])
        if 'Content-Type' in headers:
            self.mime_type = headers['Content-Type']
        if 'ETag' in headers:
            self.etag = headers['ETag']


    def json(self):
        self._fill()
        video_info = {}
        if self.url:
            video_info['url'] = self.url
        if self.mime_type:
            video_info['mime_type'] = self.mime_type
        if self.codec:
            video_info['codec'] = self.codec
        if self.bitrate:
            video_info['bitrate'] = int(self.bitrate)
        if self.width:
            video_info['width'] = int(self.width)
        if self.height:
            video_info['height'] = int(self.height)
        if self.size:
            video_info['size'] = int(self.size)
        if self.etag:
            video_info['etag'] = self.etag
        return video_info


class Videos:
    videos = []


    def json(self):
        videos_info = {}
        if self.videos:
            videos_info['videos'] = [x.json() for x in self.videos]
        return videos_info


class Article:
    tags = []
    time = ArticleTime()
    info = Info()
    images = Images()
    location = Location()
    author = Author()
    publisher = Publisher()
    text = Text()
    videos = Videos()


    def json(self):
        article_json = {
            'time': self.time.json(),
            'tags': self.tags,
            'info': self.info.json(),
            'images': self.images.json(),
            'location': self.location.json(),
            'author': self.author.json(),
            'publisher': self.publisher.json(),
            'text': self.text.json(),
            'videos': self.videos.json()
        }
        return article_json
