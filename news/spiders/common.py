# -*- coding: utf-8 -*-
"""Common utilities for scraping"""
import json
import re
from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs
import html2text
import js2py
from .article import Image, Audio, Author


def extract_string_from_javascript(response_text, start_index):
    """Extracts a string from a javascript string in text"""
    string_length = 0
    while True:
        if response_text[start_index + string_length] == '"':
            if response_text[start_index + string_length - 1] != '\\':
                break
        string_length += 1
    final_string = response_text[start_index:start_index + string_length]
    return final_string.encode('utf-8').decode('unicode-escape')


def extract_javascript_strings(response_text, start_pattern):
    """Extracts many javascript strings based on a pattern"""
    text_strings = []
    for found_pattern in re.finditer(start_pattern, response_text):
        start_index = found_pattern.start()
        begin_looking_index = start_index + len(start_pattern)
        text = extract_string_from_javascript(response_text, begin_looking_index)
        text_strings.append(text)
    return text_strings


def extract_urls(response):
    """Extracts URLs from a tags"""
    urls = []
    for url in response.xpath("//a/@href").extract():
        urls.append(response.urljoin(url))
    javascript_identifiers = [
        '{"__typename":"LinkFormat","url":"', # New York Times
        '"type":"Story","url":"' # The Star
    ]
    for javascript_identifier in javascript_identifiers:
        text_strings = extract_javascript_strings(response.text, javascript_identifier)
        for text_string in text_strings:
            urls.append(response.urljoin(text_string))
    return urls


def extract_metadata(response):
    """Extracts metadata from meta tags"""
    metadata = {}
    for meta_element in response.xpath('//meta'):
        name = meta_element.xpath("@name").extract_first()
        meta_property = meta_element.xpath("@property").extract_first()
        content = meta_element.xpath("@content").extract_first()
        meta_key = name
        if not meta_key:
            meta_key = meta_property
        if isinstance(meta_key, basestring) and isinstance(content, basestring):
            metadata[meta_key] = content
    return metadata


def extract_text_with_links(element, removeable_paragraphs):
    """Extracts text with the appropriate hyperlink"""
    paragraph_list = []
    for paragraph in element.xpath(".//text()"):
        stripped_paragraph = paragraph.extract().strip()
        if stripped_paragraph and stripped_paragraph not in removeable_paragraphs:
            paragraph_list.append({
                'text': stripped_paragraph
            })
    for link in element.css('a'):
        text_path = link.xpath('text()').extract_first()
        if text_path is None:
            continue
        text = text_path.strip()
        href_path = link.xpath('@href').extract_first()
        if href_path is None:
            continue
        href = href_path.strip()
        for paragraph_text in paragraph_list:
            if paragraph_text['text'] == text:
                paragraph_text['link'] = href
    return paragraph_list


def extract_imgs(response, element):
    """Extracts img sources from an element"""
    imgs = []
    for img in element.css('img::attr(src)').extract():
        full_img = response.urljoin(img)
        imgs.append(full_img)
    return imgs


def extract_item(response, paragraph_list, main_element):
    """Extracts items from a paragraph list, the main element and the response"""
    if not paragraph_list:
        return None
    item = extract_metadata(response)
    item['articleBody'] = paragraph_list
    item['imgs'] = extract_imgs(response, main_element)
    return item


def extract_item_from_element_css(response, css_selector):
    """Extracts items from a single css selector"""
    items = []
    for div_element in response.css(css_selector):
        paragraph_list = []
        for p_element in div_element.css("p"):
            paragraph_list.extend(extract_text_with_links(p_element, []))
        item = extract_item(response, paragraph_list, div_element)
        if item:
            items.append(item)
    return items


def strip_query_from_url(url):
    """Strips a query string from a URL"""
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query.pop('q2', None)
    parsed_url = parsed_url._replace(query=urlencode(query, True))
    return urlunparse(parsed_url)


def remove_common_tags(remove_items, soup):
    """Remove common tags"""
    remove_items.append({'tag': 'noscript', 'meta': {}})
    remove_items.append({'tag': 'button', 'meta': {}})
    remove_items.append({'tag': 'div', 'meta': {'class': 'ob-widget-section'}})
    for remove_item in remove_items:
        for tag in soup.findAll(remove_item['tag'], remove_item['meta']):
            tag.decompose()


def execute_script(script_tag):
    """Executes a script"""
    if not script_tag.text:
        return None
    try:
        context = js2py.EvalJs()
        context.execute(script_tag.text)
        return context
    except js2py.PyJsException:
        pass
    return None


def find_images(soup, article, response):
    """Finds the images with an article"""
    for img_tag in soup.findAll('img'):
        if img_tag['src'].startswith('data:'):
            continue
        image = Image()
        image.url = response.urljoin(img_tag['src'])
        if img_tag.has_attr('width'):
            image.width = img_tag['width']
        if img_tag.has_attr('height'):
            image.height = img_tag['height']
        if img_tag.has_attr('alt'):
            image.alt = img_tag['alt']
        if img_tag.has_attr('title'):
            image.title = img_tag['title']
        article.images.append_image(image)


def find_audio(soup, article):
    """Finds the audio within an article"""
    for audio_tag in soup.findAll('audio'):
        for source_tag in audio_tag.findAll('source'):
            audio = Audio()
            audio.url = source_tag['src']
            audio.mime_type = source_tag['type']
            article.audio.append(audio)


def find_main_content(main_content_divs, article, response, soup):
    """Finds the main content and fills in the article"""
    main_content_div = None
    for div in main_content_divs:
        main_content_div = soup.find(div['tag'], div['meta'])
        if main_content_div:
            break
    if not main_content_div:
        raise ValueError('Could not find the main content div: {}'.format(response.url))
    find_images(main_content_div, article, response)
    markdown_text = html2text.html2text(unicode(main_content_div))
    markdown_text = '\n'.join([line for line in markdown_text.split('\n') if 'Read more:' not in line])
    article.text.set_markdown_text(markdown_text)


def find_script_json(soup, article):
    """Finds the script JSON"""
    for script_tag in soup.findAll('script', {'type': 'application/ld+json'}):
        script_json = json.loads(script_tag.text.replace('\\/', '/'))
        for author in script_json['author']:
            if isinstance(author, unicode):
                continue
            article_author = Author()
            article_author.name = author['name']
            article.authors.append(article_author)
        article.time.set_modified_time(script_json['dateModified'])
        article.publisher.organisation = script_json['publisher']['name']
        if 'url' in script_json:
            article.info.url = script_json['url']
        else:
            article.info.url = script_json['mainEntityOfPage']
        article.images.thumbnail.url = script_json['image']['url']
        article.images.thumbnail.width = script_json['image']['width']
        article.images.thumbnail.height = script_json['image']['height']
        article.time.set_published_time(script_json['datePublished'])
        article.info.title = script_json['headline']
        if 'description' in script_json:
            article.info.description = script_json['description']
