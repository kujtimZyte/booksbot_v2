# -*- coding: utf-8 -*-
"""Structure for creating an article representation"""
import datetime
import re
from bs4 import BeautifulSoup
from dateutil import parser
from markdown import markdown
import requests


def timecode_from_datetime(datetime_obj):
    """Computes the unix timecode from a datetime object"""
    utc_naive = datetime_obj
    if datetime_obj.utcoffset() is not None:
        utc_naive = datetime_obj.replace(tzinfo=None) - datetime_obj.utcoffset()
    return (utc_naive - datetime.datetime(1970, 1, 1)).total_seconds()


def url_head_headers(url):
    """Fetches the headers for a URL HEAD request"""
    try:
        response = requests.head(url, timeout=5)
        return response.headers
    except requests.ReadTimeout:
        return {}


def markdown_to_plaintext(markdown_text):
    """Converts markdown to plaintext"""
    # https://gist.github.com/lorey/eb15a7f3338f959a78cc3661fbc255fe
    html = markdown(markdown_text)
    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)
    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))
    return text


def fix_pixel_property(pixel_property):
    """Converts the pixel property to an int"""
    if isinstance(pixel_property, int):
        return pixel_property
    if isinstance(pixel_property, float):
        return int(pixel_property)
    return int(float(pixel_property.replace('px', '')))


def parse_date(datestring):
    """Parses a date safely"""
    date = None
    try:
        date = parser.parse(datestring)
    except ValueError:
        return None
    return date


class ArticleTime(object):
    """Holds the information about the article time"""
    def __init__(self):
        self.published_time = None
        self.modified_time = None


    def set_published_time(self, published_time):
        """Sets the published time and parses the date"""
        date = parse_date(published_time)
        if date:
            self.published_time = date


    def set_modified_time(self, modified_time):
        """Sets the modified time and parses the date"""
        date = parse_date(modified_time)
        if date:
            self.modified_time = date


    def json(self):
        """Converts the class to a dictionary object compatible with JSON"""
        time_json = {}
        if self.published_time:
            time_json['published_time'] = timecode_from_datetime(self.published_time)
        if self.modified_time:
            time_json['modified_time'] = timecode_from_datetime(self.modified_time)
        return time_json


class Info(object):
    """Holds the general information about the article"""
    genre = None
    url = None
    title = None
    description = None


    def __init__(self):
        self.genre = None
        self.url = None
        self.title = None
        self.description = None


    def set_genre(self, genre):
        """Sets the genre"""
        self.genre = genre


    def set_url(self, url):
        """Sets the url"""
        self.url = url


    def set_title(self, title):
        """Sets the title"""
        self.title = title


    def set_description(self, description):
        """Sets the description"""
        self.description = description


    def json(self):
        """Converts the class to a dictionary object compatible with JSON"""
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


class RichMedia(object):
    """Holds the information about the media"""
    url = None
    mime_type = None
    last_modified = None
    size = None
    etag = None


    def __init__(self):
        self.url = None
        self.mime_type = None
        self.last_modified = None
        self.size = None
        self.etag = None


    def fill(self):
        """Fills the rich media information"""
        if not self.url:
            return
        if self.last_modified != None and \
           self.size != None and \
           self.mime_type != None and \
           self.etag != None:
            return
        headers = url_head_headers(self.url)
        if 'Last-Modified' in headers and self.last_modified != None:
            self.last_modified = timecode_from_datetime(parser.parse(headers['Last-Modified']))
        if 'Content-Length' in headers and self.size != None:
            self.size = int(headers['Content-Length'])
        if 'Content-Type' in headers and self.mime_type != None:
            self.mime_type = headers['Content-Type']
        if 'ETag' in headers and not self.etag:
            self.etag = headers['ETag']


    def json(self):
        """Converts the class to a dictionary object compatible with JSON"""
        self.fill()
        rich_media_info = {}
        if self.url:
            rich_media_info['url'] = self.url
        if self.mime_type:
            rich_media_info['mime_type'] = self.mime_type
        if self.last_modified:
            rich_media_info['last_modified'] = self.last_modified
        if self.size:
            rich_media_info['size'] = self.size
        if self.etag:
            rich_media_info['etag'] = self.etag
        return rich_media_info


class Image(RichMedia):
    """Holds the information about the image"""
    width = None
    height = None
    alt = None
    title = None


    def __init__(self):
        RichMedia.__init__(self)
        self.width = None
        self.height = None
        self.alt = None
        self.title = None


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        image_json = super(Image, self).json()
        if self.width:
            image_json['width'] = fix_pixel_property(self.width)
        if self.height:
            image_json['height'] = fix_pixel_property(self.height)
        if self.alt:
            image_json['alt'] = self.alt
        if self.title:
            image_json['title'] = self.title
        return image_json


class Images(object):
    """An object for holding images"""
    thumbnail = Image()
    images = []


    def __init__(self):
        self.thumbnail = Image()
        self.images = []


    def append_image(self, image):
        """Appends an image"""
        self.images.append(image)


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        images_json = {}
        if self.thumbnail:
            images_json['thumbnail'] = self.thumbnail.json()
        if self.images:
            images_json['images'] = [x.json() for x in self.images]
        return images_json


class Location(object):
    """An object for holding location images"""
    latitude = None
    longitude = None


    def __init__(self):
        self.latitude = None
        self.longitude = None


    def set_latitude(self, latitude):
        """Sets the latitude"""
        self.latitude = latitude


    def set_longitude(self, longitude):
        """Sets the longitude"""
        self.longitude = longitude


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        location_info = {}
        if self.latitude:
            location_info['latitude'] = float(self.latitude)
        if self.longitude:
            location_info['longitude'] = float(self.longitude)
        return location_info


class Author(object):
    """An object for holding the author"""
    def __init__(self):
        self.url = None
        self.name = None
        self.twitter_url = None
        self.email = None
        self.image = Image()


    def set_url(self, url):
        """Sets the authors URL"""
        self.url = url


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        author_info = {}
        if self.url:
            author_info['url'] = self.url
        if self.name:
            author_info['name'] = self.name
        if self.twitter_url:
            author_info['twitter_url'] = self.twitter_url
        if self.email:
            author_info['email'] = self.email
        if self.image:
            image_dict = self.image.json()
            if image_dict:
                author_info['image'] = image_dict
        return author_info


class Facebook(object):
    """An object for holding the facebook information"""
    def __init__(self):
        self.url = None
        self.page_ids = []
        self.app_id = None
        self.status = None


    def set_url(self, url):
        """Sets the Facebook URL"""
        self.url = url


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        facebook_info = {}
        if self.url:
            facebook_info['url'] = self.url
        if self.page_ids:
            facebook_info['page_id'] = self.page_ids
        if self.app_id:
            facebook_info['app_id'] = self.app_id
        if self.status:
            facebook_info['status'] = self.status
        return facebook_info


class Twitter(object):
    """An object for holding the twitter information"""
    def __init__(self):
        self.card = None
        self.image = None
        self.handle = None
        self.image_alt = None
        self.title = None
        self.description = None
        self.domain = None


    def set_card(self, card):
        """Sets the card"""
        self.card = card


    def set_image(self, image):
        """Sets the image"""
        self.image = image


    def set_handle(self, handle):
        """Sets the handle"""
        self.handle = handle


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        twitter_info = {}
        if self.card:
            twitter_info['card'] = self.card
        if self.image:
            twitter_info['image'] = self.image
        if self.handle:
            twitter_info['handle'] = self.handle
        if self.image_alt:
            twitter_info['image_alt'] = self.image_alt
        if self.title:
            twitter_info['title'] = self.title
        if self.description:
            twitter_info['description'] = self.description
        if self.domain:
            twitter_info['domain'] = self.domain
        return twitter_info


class Publisher(object):
    """An object for holding the publishers information"""
    facebook = Facebook()
    twitter = Twitter()
    organisation = None


    def __init__(self):
        self.facebook = Facebook()
        self.twitter = Twitter()
        self.organisation = None


    def set_organisation(self, organisation):
        """Sets the organisation"""
        self.organisation = organisation


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        publisher_info = {}
        if self.facebook:
            publisher_info['facebook'] = self.facebook.json()
        if self.twitter:
            publisher_info['twitter'] = self.twitter.json()
        if self.organisation:
            publisher_info['organisation'] = self.organisation
        return publisher_info


class Text(object):
    """An object for holding the text"""
    markdown_text = None
    text = None


    def __init__(self):
        self.markdown_text = None
        self.text = None


    def set_markdown_text(self, markdown_text):
        """Sets the markdown"""
        self.markdown_text = markdown_text
        self.text = markdown_to_plaintext(self.markdown_text)


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        text_info = {}
        if self.markdown_text:
            text_info['markdown'] = self.markdown_text
        if self.text:
            text_info['text'] = self.text
        return text_info


class Video(RichMedia):
    """An object for holding the video"""
    codec = None
    bitrate = None
    width = None
    height = None


    def __init__(self):
        RichMedia.__init__(self)
        self.codec = None
        self.bitrate = None
        self.width = None
        self.height = None


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        self.fill()
        video_info = super(Video, self).json()
        if self.codec:
            video_info['codec'] = self.codec
        if self.bitrate:
            video_info['bitrate'] = int(self.bitrate)
        if self.width:
            video_info['width'] = fix_pixel_property(self.width)
        if self.height:
            video_info['height'] = fix_pixel_property(self.height)
        return video_info


class Videos(object):
    """An object for holding videos"""
    videos = []


    def __init__(self):
        self.videos = []


    def append_video(self, video):
        """Appends a video"""
        self.videos.append(video)


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        videos_info = {}
        if self.videos:
            videos_info['videos'] = [x.json() for x in self.videos]
        return videos_info


class Audio(RichMedia):
    """An object for holding audio"""
    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        self.fill()
        audio_info = super(Audio, self).json()
        return audio_info


# pylint: disable=too-many-instance-attributes
class Article(object):
    """An object for holding an article"""
    def __init__(self):
        self.tags = []
        self.time = ArticleTime()
        self.info = Info()
        self.images = Images()
        self.location = Location()
        self.authors = []
        self.publisher = Publisher()
        self.text = Text()
        self.videos = Videos()
        self.audio = []


    def add_tag(self, tag):
        """Adds a tag"""
        self.tags.append(tag)


    def json(self):
        """Returns the object as a dictionary for JSON consumption"""
        author_dict = {}
        for author in self.authors:
            if not author.name and not author.url:
                continue
            if author.name in author_dict:
                continue
            author_dict[author.name] = author
        article_json = {
            'time': self.time.json(),
            'tags': filter(len, list(set(self.tags))),
            'info': self.info.json(),
            'images': self.images.json(),
            'location': self.location.json(),
            'authors': [x.json() for x in author_dict.values()],
            'publisher': self.publisher.json(),
            'text': self.text.json(),
            'videos': self.videos.json(),
            'audio': [x.json() for x in self.audio]
        }
        return article_json
# pylint: enable=too-many-instance-attributes
