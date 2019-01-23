# -*- coding: utf-8 -*-
"""Parser for the ABC website"""
from bs4 import BeautifulSoup
import html2text
import js2py
from .common import extract_metadata, strip_query_from_url
from .article import Article, Image, Video, Author, Audio


def abc_url_parse(url):
    """Parses the URL from an ABC website"""
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if len(url_split) < 7:
        return None
    last_path = url_split[-1]
    if not last_path.isdigit():
        return None
    return last_path


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
        },
        {
            'tag': 'a',
            'meta': {
                'class': 'button'
            }
        },
        {
            'tag': 'noscript',
            'meta': {}
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'comp-share'
            }
        },
        {
            'tag': 'li',
            'meta': {
                'class': 'menu-item'
            }
        },
        {
            'tag': 'button',
            'meta': {}
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'comp-embedded-float-right'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'view-features-list'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'view-sidebar'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'rn-nav'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'id': 'comments'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'ct-social-share'
            }
        },
        {
            'tag': 'a',
            'meta': {
                'class': 'ico'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'view-brand-logo'
            }
        },
        {
            'tag': 'div',
            'meta': {
                'class': 'print-hide'
            }
        },
        {
            'tag': 'span',
            'meta': {
                'class': 'accordion-icon'
            }
        }
    ]
    for remove_item in remove_items:
        for tag in soup.findAll(remove_item['tag'], remove_item['meta']):
            tag.decompose()


def find_facebook_url(meta_tags, soup):
    """Finds the facebook URL from an article"""
    if 'article:publisher' in meta_tags:
        return meta_tags['article:publisher']
    for a_tag in soup.findAll('a'):
        for img_tag in a_tag.findAll('img'):
            if not img_tag.has_attr('title'):
                continue
            if img_tag['title'] == 'ABC News on Facebook':
                return a_tag['href']
    return None


def find_tags(meta_tags):
    """Finds the tags within an ABC article"""
    tags = []
    if 'ABC.tags' in meta_tags:
        for tag in meta_tags['ABC.tags'].split(';'):
            tags.append(tag)
    return tags


def find_published_time(meta_tags, response):
    """Finds the published time within an ABC article"""
    if 'article:published_time' in meta_tags:
        return meta_tags['article:published_time']
    elif 'DCTERMS.issued' in meta_tags:
        return meta_tags['DCTERMS.issued']
    raise ValueError('Could not find a published date: {}'.format(response.url))


def find_modified_time(meta_tags):
    """Finds the modified time within an ABC article"""
    if 'article:modified_time' in meta_tags:
        return meta_tags['article:modified_time']
    elif 'DCTERMS.modified' in meta_tags:
        return meta_tags['DCTERMS.modified']
    return None


def find_title(meta_tags, response):
    """Finds the title of the ABC article"""
    if 'DC.title' in meta_tags:
        return meta_tags['DC.title']
    elif 'DCTERMS.title' in meta_tags:
        return meta_tags['DCTERMS.title']
    else:
        raise ValueError('Could not find a title: {}'.format(response.url))


def find_location(meta_tags, article):
    """Finds the location of an ABC article"""
    if 'geo.position' in meta_tags:
        positions = meta_tags['geo.position'].split(';')
        article.location.set_latitude(positions[0])
        article.location.set_longitude(positions[1])


def find_facebook_page(meta_tags):
    """Finds the facebook page"""
    if 'fb:pages' in meta_tags:
        return meta_tags['fb:pages']
    return None


def find_twitter(meta_tags, article):
    """Finds the twitter information"""
    article.publisher.twitter.set_card(meta_tags['twitter:card'])
    if 'twitter:image' in meta_tags:
        article.publisher.twitter.set_image(meta_tags['twitter:image'])
    if 'twitter:site' in meta_tags:
        article.publisher.twitter.set_handle(meta_tags['twitter:site'])


def find_genre(meta_tags):
    """Finds the genre of an ABC article"""
    if 'ABC.editorialGenre' in meta_tags:
        return meta_tags['ABC.editorialGenre']
    return None


def find_description(meta_tags):
    """Finds the description of an ABC article"""
    if 'description' in meta_tags:
        return meta_tags['description']
    return None


def fill_article_from_meta_tags(article, response, soup):
    """Fills an article object with information from meta tags"""
    meta_tags = extract_metadata(response)
    article.publisher.facebook.set_url(find_facebook_url(meta_tags, soup))
    remove_tags(soup)
    for tag in find_tags(meta_tags):
        article.add_tag(tag)
    article.time.set_published_time(find_published_time(meta_tags, response))
    article.time.set_modified_time(find_modified_time(meta_tags))
    article.info.set_genre(find_genre(meta_tags))
    article.info.set_url(response.url)
    article.info.set_title(find_title(meta_tags, response))
    article.info.set_description(find_description(meta_tags))
    article.images.thumbnail.url = meta_tags['og:image']
    article.images.thumbnail.width = meta_tags['og:image:width']
    article.images.thumbnail.height = meta_tags['og:image:height']
    article.images.thumbnail.mime_type = meta_tags['og:image:type']
    find_location(meta_tags, article)
    article.publisher.facebook.set_page_id(find_facebook_page(meta_tags))
    find_twitter(meta_tags, article)
    if 'DC.Publisher.CorporateName' in meta_tags:
        article.publisher.set_organisation(meta_tags['DC.Publisher.CorporateName'])
    elif 'DCTERMS.publisher' in meta_tags:
        article.publisher.set_organisation(meta_tags['DCTERMS.publisher'])
    else:
        raise ValueError('Could not find an organisation: {}'.format(response.url))
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
            byline_text = div_tag.text.replace('By ', '').replace('AP: ', '')
            for name in byline_text.split(' and '):
                author = Author()
                author.name = name.strip()
                article.authors.append(author)
            break
    if len(article.authors) == 1:
        for a_tag in soup.findAll('a', {'class': 'twitter-timeline'}):
            article.authors[0].twitter_url = a_tag['href']


def find_main_content_tag(soup, response):
    """Finds the main content tag in an ABC article"""
    main_content_div = soup.find('div', {'id': 'main_content'})
    if not main_content_div:
        main_content_div = soup.find('div', {'class': 'article'})
        if main_content_div:
            if 'media-wrapper-dl' in main_content_div['class']:
                main_content_div = None
    if not main_content_div:
        main_content_div = soup.find('div', {'class': 'page'})
    if not main_content_div:
        main_content_div = soup.find('div', {'class': 'article-text'})
    if not main_content_div:
        main_content_div = soup.find('div', {'class': 'container'})
    if not main_content_div:
        raise ValueError('Could not find the main content div: {}'.format(response.url))
    return main_content_div


def find_audio(soup, article):
    """Finds the audio within an ABC article"""
    for a_tag in soup.findAll('a', {'class': 'ico-download'}):
        audio = Audio()
        audio.url = a_tag['href']
        article.audio.append(audio)
    for span_tag in soup.findAll('span', {'class': 'download'}):
        for a_tag in span_tag.findAll('a'):
            if a_tag['href'].endswith('.mp3'):
                audio = Audio()
                audio.url = a_tag['href']
                article.audio.append(audio)


def find_images(soup, article, response):
    """Finds the images with an ABC article"""
    for img_tag in soup.findAll('img'):
        image = Image()
        image.url = response.urljoin(img_tag['src'])
        if img_tag.has_attr('width'):
            image.width = int(img_tag['width'])
        if img_tag.has_attr('height'):
            image.height = int(img_tag['height'])
        if img_tag.has_attr('alt'):
            image.alt = img_tag['alt']
        if img_tag.has_attr('title'):
            image.title = img_tag['title']
        article.images.append_image(image)


def abc_parse(response):
    """Parses the response from a ABC website"""
    link_id = abc_url_parse(response.url)
    if link_id is None:
        return None, link_id
    article = Article()
    soup = BeautifulSoup(response.text, 'html.parser')
    find_audio(soup, article)
    fill_article_from_meta_tags(article, response, soup)
    main_content_div = find_main_content_tag(soup, response)
    find_images(soup, article, response)
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
    if not article.text.text.strip():
        raise ValueError('Could not find a text: {}'.format(response.url))
    return article.json(), link_id


def abc_url_filter(url):
    """Filters URLs in the ABC domain"""
    url_filters = [
        'contact/feedback',
        'news/feed/',
        'conditions.h',
        'about.',
        'contact/tip-off',
        'rural/rss',
        'alerts/email',
        '/tok-pisin',
        '/download-this-service/'
    ]
    url_endings = [
        '.pdf',
        '.xml'
    ]
    for url_filter in url_filters:
        if url_filter in url:
            return False
    for url_ending in url_endings:
        if url.endswith(url_ending):
            return False
    return True
