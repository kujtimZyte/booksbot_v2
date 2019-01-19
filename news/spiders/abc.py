# -*- coding: utf-8 -*-
"""Parser for the ABC website"""
import datetime
from .common import extract_item_from_element_css, extract_metadata
from .article import Article, Image, Video
from bs4 import BeautifulSoup
from dateutil import parser
import html2text
import js2py


remove_items = [
    {
        'tag': 'div',
        'meta': {
            'class': 'featured-scroller'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'id': 'footer-stories'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'promo'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'newsmail-signup'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'localised-top-stories'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'promo-list'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'graphic'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'sidebar'
        }
    },
    {
        'tag': 'p',
        'meta': {
            'class': 'topics'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'statepromo'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'share-icons'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'jwplayer-video'
        }
    },
    {
        'tag': 'a',
        'meta': {
            'class': 'abcLink'
        }
    },
    {
        'tag': 'a',
        'meta': {
            'class': 'controller'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'class': 'brand'
        }
    },
    {
        'tag': 'div',
        'meta': {
            'id': 'highContrastTest'
        }
    },
    {
        'tag': 'img',
        'meta': {
            'id': 'imgCounter'
        }
    }
]


def abc_url_parse(url):
    """Parses the URL from an ABC website"""
    url_split = url.split('/')
    if len(url_split) != 7:
        return None
    return url_split[-1]


def abc_parse(response):
    """Parses the response from a ABC website"""
    link_id = abc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = Article()
    meta_tags = extract_metadata(response)
    article.tags = meta_tags['ABC.tags'].split(';')
    article.time.published_time = parser.parse(meta_tags['article:published_time'])
    article.time.modified_time = parser.parse(meta_tags['article:modified_time'])
    article.time.retrieved_time = parser.parse(meta_tags['article:modified_time'])
    article.info.genre = meta_tags['ABC.editorialGenre']
    article.info.url = response.url
    article.info.title = meta_tags['DC.title']
    article.info.description = meta_tags['description']
    article.images.thumbnail.url = meta_tags['og:image']
    article.images.thumbnail.width = meta_tags['og:image:width']
    article.images.thumbnail.height = meta_tags['og:image:height']
    article.images.thumbnail.mime_type = meta_tags['og:image:type']
    positions = meta_tags['geo.position'].split(';')
    article.location.latitude = positions[0]
    article.location.longitude = positions[1]
    article.publisher.facebook.url = meta_tags['article:publisher']
    article.publisher.facebook.page_id = meta_tags['fb:pages']
    article.publisher.twitter.card = meta_tags['twitter:card']
    article.publisher.twitter.image = meta_tags['twitter:image']
    article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.organisation = meta_tags['DC.Publisher.CorporateName']
    article.author.url = meta_tags['article:author']
    soup = BeautifulSoup(response.text, 'html.parser')
    for remove_item in remove_items:
        for tag in soup.findAll(remove_item['tag'], remove_item['meta']):
            tag.decompose()
    main_content_div = soup.find('div', {'id': 'main_content'})
    for img_tag in soup.findAll('img'):
        image = Image()
        image.url = response.urljoin(img_tag['src'])
        if 'width' in img_tag:
            image.width = int(img_tag['width'])
        if 'height' in img_tag:
            image.height = int(img_tag['height'])
        article.images.images.append(image)
    for script_tag in soup.findAll('script'):
        script_text = script_tag.text
        if not script_text:
            continue
        try:
            context = js2py.EvalJs()
            context.execute(script_text)
            if not hasattr(context, 'inlineVideoData'):
                continue
            for inline_video in context.inlineVideoData:
                for inline_video_instance in inline_video:
                    video = Video()
                    video.url = response.urljoin(inline_video_instance['url'])
                    video.mime_type = inline_video_instance['contentType']
                    video.codec = inline_video_instance['codec']
                    video.bitrate = inline_video_instance['bitrate']
                    video.width = inline_video_instance['width']
                    video.height = inline_video_instance['height']
                    video.size = inline_video_instance['filesize']
                    article.videos.videos.append(video)
        except js2py.PyJsException:
            continue
    article.text.markdown = html2text.html2text(unicode(main_content_div))
    return article.json(), link_id
