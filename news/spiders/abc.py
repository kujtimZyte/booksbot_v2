# -*- coding: utf-8 -*-
"""Parser for the ABC website"""
from bs4 import BeautifulSoup
import html2text
import js2py
from .common import extract_metadata
from .article import Article, Image, Video, Author


def abc_url_parse(url):
    """Parses the URL from an ABC website"""
    url_split = url.split('/')
    if len(url_split) != 7:
        return None
    return url_split[-1]


def remove_tags(soup):
    """Removes the useless tags from the HTML"""
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
        },
        {
            'tag': 'a',
            'meta': {
                'class': 'home'
            }
        },
        {
            'tag': 'a',
            'meta': {
                'class': 'search'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'bylinepromo'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'attached-content'
            }
        }
    ]
    for remove_item in remove_items:
        for tag in soup.findAll(remove_item['tag'], remove_item['meta']):
            tag.decompose()


def fill_article_from_meta_tags(article, response, soup):
    """Fills an article object with information from meta tags"""
    meta_tags = extract_metadata(response)
    for tag in meta_tags['ABC.tags'].split(';'):
        article.add_tag(tag)
    article.time.set_published_time(meta_tags['article:published_time'])
    article.time.set_modified_time(meta_tags['article:modified_time'])
    article.info.set_genre(meta_tags['ABC.editorialGenre'])
    article.info.set_url(response.url)
    article.info.set_title(meta_tags['DC.title'])
    article.info.set_description(meta_tags['description'])
    article.images.thumbnail.url = meta_tags['og:image']
    article.images.thumbnail.width = meta_tags['og:image:width']
    article.images.thumbnail.height = meta_tags['og:image:height']
    article.images.thumbnail.mime_type = meta_tags['og:image:type']
    positions = meta_tags['geo.position'].split(';')
    article.location.set_latitude(positions[0])
    article.location.set_longitude(positions[1])
    article.publisher.facebook.set_url(meta_tags['article:publisher'])
    article.publisher.facebook.set_page_id(meta_tags['fb:pages'])
    article.publisher.twitter.set_card(meta_tags['twitter:card'])
    article.publisher.twitter.set_image(meta_tags['twitter:image'])
    article.publisher.twitter.set_handle(meta_tags['twitter:site'])
    article.publisher.set_organisation(meta_tags['DC.Publisher.CorporateName'])
    if 'article:author' in meta_tags:
        author = Author()
        author.set_url(meta_tags['article:author'])
        for a_tag in soup.findAll('a'):
            if response.urljoin(a_tag['href']) == author.url:
                author.name = a_tag.text
                break
        article.authors.append(author)
    else:
        for div_tag in soup.findAll('div', {'class': 'byline'}):
            byline_text = div_tag.text.replace('By ', '')
            for name in byline_text.split(' and '):
                author = Author()
                author.name = name.strip()
                article.authors.append(author)
            break


def abc_parse(response):
    """Parses the response from a ABC website"""
    link_id = abc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = Article()
    soup = BeautifulSoup(response.text, 'html.parser')
    remove_tags(soup)
    fill_article_from_meta_tags(article, response, soup)
    main_content_div = soup.find('div', {'id': 'main_content'})
    for img_tag in soup.findAll('img'):
        image = Image()
        image.url = response.urljoin(img_tag['src'])
        if 'width' in img_tag:
            image.width = int(img_tag['width'])
        if 'height' in img_tag:
            image.height = int(img_tag['height'])
        article.images.append_image(image)
    for script_tag in soup.findAll('script'):
        if not script_tag.text:
            continue
        try:
            context = js2py.EvalJs()
            context.execute(script_tag.text)
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
                    article.videos.append_video(video)
        except js2py.PyJsException:
            continue
    article.text.set_markdown(html2text.html2text(unicode(main_content_div)))
    return article.json(), link_id


def abc_url_filter(url):
    """Filters URLs in the ABC domain"""
    if 'contact/feedback' in url:
        return False
    if 'contact/tipoff' in url:
        return False
    if 'news/feed/' in url:
        return False
    return True
