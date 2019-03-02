# -*- coding: utf-8 -*-
"""Common utilities for scraping"""
import hashlib
import json
import re
from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs
from bs4 import BeautifulSoup
import html2text
import js2py
from .article import Image, Audio, Author, Article


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
            final_url = response.urljoin(text_string)
            if final_url not in urls:
                urls.append(final_url)
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
    final_url = urlunparse(parsed_url)
    if final_url[-1] == '/':
        final_url = final_url[:-1]
    return final_url


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
    except (js2py.PyJsException, KeyError), _exception:
        pass
    return None


def find_images(soup, article, response):
    """Finds the images with an article"""
    for img_tag in soup.findAll('img'):
        if not img_tag.has_attr('src'):
            continue
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
    bad_line_flags = [
        'Read more:'
    ]
    for bad_line_flag in bad_line_flags:
        markdown_text = '\n'.join(
            [line for line in markdown_text.split('\n') if bad_line_flag not in line])
    article.text.set_markdown_text(markdown_text)


def author_from_json_author(json_author):
    """Finds the author from the JSON author"""
    if json_author['@type'] == 'Organization' or json_author['@type'] == 'NewsMediaOrganization':
        return None
    article_author = Author()
    article_author.name = json_author['name']
    return article_author


def handle_script_json_authors(script_json, article):
    """Handles the author parsing from the script JSON"""
    if 'author' in script_json:
        authors = script_json['author']
        if isinstance(authors, list):
            for author in authors:
                article_author = author_from_json_author(author)
                if article_author:
                    article.authors.append(article_author)
        elif isinstance(authors, dict):
            author = authors
            article_author = author_from_json_author(author)
            if article_author:
                article.authors.append(article_author)


def handle_script_image(script_json, article):
    """Handles the script image field in the JSON context"""
    if 'image' in script_json:
        image = script_json['image']
        if isinstance(image, basestring):
            article.images.thumbnail.url = image
        else:
            if 'url' in image:
                article.images.thumbnail.url = image['url']
            article.images.thumbnail.width = image['width']
            article.images.thumbnail.height = image['height']


def find_script_json(soup, article):
    """Finds the script JSON"""
    for script_tag in soup.findAll('script', {'type': 'application/ld+json'}):
        script_json = json.loads(script_tag.text.replace('\\/', '/'))
        handle_script_json_authors(script_json, article)
        if 'dateModified' in script_json:
            article.time.set_modified_time(script_json['dateModified'])
        if 'publisher' in script_json:
            publisher = script_json['publisher']
            if 'name' in publisher:
                article.publisher.organisation = publisher['name']
        if 'url' in script_json:
            article.info.url = script_json['url']
        elif 'mainEntityOfPage' in script_json:
            article.info.url = script_json['mainEntityOfPage']
        handle_script_image(script_json, article)
        if 'datePublished' in script_json:
            article.time.set_published_time(script_json['datePublished'])
        if 'headline' in script_json:
            article.info.title = script_json['headline']
        if 'description' in script_json:
            article.info.description = script_json['description']


def common_response_data(response):
    """Finds the common response data"""
    soup = BeautifulSoup(response.text, 'html5lib')
    meta_tags = extract_metadata(response)
    article = Article()
    return soup, meta_tags, article


def extract_link_id(url, lengths=None, article_index=-1, use_hash=True):
    """Extracts the link ID from a URL"""
    if lengths is None:
        lengths = [7]
    url = strip_query_from_url(url)
    url_split = url.split('/')
    if url_split[-1] == 'index.html':
        url_split = url_split[:-1]
    if len(url_split) not in lengths:
        return None
    last_path = url_split[article_index]
    if use_hash:
        return hashlib.sha224(last_path).hexdigest()
    return last_path


def parse_meta_tags_keywords(meta_tags, article):
    """Extracts the necessary meta tags keywords into the article"""
    keyword_keys = ['keywords', 'news_keywords']
    for keyword_key in keyword_keys:
        if keyword_key not in meta_tags:
            continue
        for keyword in meta_tags[keyword_key].split(','):
            article.tags.append(keyword.strip())


def parse_meta_tags_info(meta_tags, article):
    """Extracts the necessary meta tags into the article info"""
    if 'description' in meta_tags:
        article.info.description = meta_tags['description']
    if 'article:section' in meta_tags:
        article.info.genre = meta_tags['article:section']
    article.info.title = meta_tags['og:title']
    article.info.description = meta_tags['og:description']


def parse_meta_tags_time(meta_tags, article):
    """Extracts the necessary meta tags into the article time"""
    if 'dc.date.modified' in meta_tags:
        article.time.set_modified_time(meta_tags['dc.date.modified'])
    if 'article:published_time' in meta_tags:
        article.time.set_published_time(meta_tags['article:published_time'])
    if 'article:modified_time' in meta_tags:
        article.time.set_modified_time(meta_tags['article:modified_time'])


def parse_meta_tags_images(meta_tags, article):
    """Extracts the necessary meta tags into the article images"""
    if 'image' in meta_tags:
        article.images.thumbnail.url = meta_tags['image']
    article.images.thumbnail.url = meta_tags['og:image']
    if 'og:image:width' in meta_tags:
        article.images.thumbnail.width = meta_tags['og:image:width']
    if 'og:image:height' in meta_tags:
        article.images.thumbnail.height = meta_tags['og:image:height']


def parse_meta_tags(meta_tags, article):
    """Extracts the necessary meta tags into the article"""
    bad_authors = [
        'CNN',
        'CNN Library',
        'Ars Staff'
    ]
    parse_meta_tags_keywords(meta_tags, article)
    parse_meta_tags_info(meta_tags, article)
    parse_meta_tags_time(meta_tags, article)
    parse_meta_tags_images(meta_tags, article)
    if 'og:site_name' in meta_tags:
        article.publisher.organisation = meta_tags['og:site_name']
    author_keys = ['author', 'article:author']
    for author_key in author_keys:
        if author_key not in meta_tags:
            continue
        for author in meta_tags[author_key].split(','):
            author_split = author.split(' and ')
            for author_split_instance in author_split:
                author = Author()
                author.name = author_split_instance.strip()
                author.name = author.name.replace('Presented by: ', '')
                if author.name in bad_authors:
                    continue
                if author.name.startswith('http'):
                    continue
                article.authors.append(author)
    if 'fb:pages' in meta_tags:
        article.publisher.facebook.page_ids.append(meta_tags['fb:pages'])
    if 'article:publisher' in meta_tags:
        article.publisher.facebook.url = meta_tags['article:publisher']
    if 'twitter:site' in meta_tags:
        article.publisher.twitter.handle = meta_tags['twitter:site']
    article.publisher.twitter.title = meta_tags['twitter:title']
    article.publisher.twitter.description = meta_tags['twitter:description']
    if 'twitter:image' in meta_tags:
        article.publisher.twitter.image = meta_tags['twitter:image']
    if 'fb:app_id' in meta_tags:
        article.publisher.facebook.app_id = meta_tags['fb:app_id']


def find_common(soup, meta_tags, article):
    """Extracts common elements from the page"""
    parse_meta_tags(meta_tags, article)
    find_script_json(soup, article)


def find_common_response_data(response):
    """Finds the common response data and parses it"""
    soup, meta_tags, article = common_response_data(response)
    find_common(soup, meta_tags, article)
    return soup, meta_tags, article
