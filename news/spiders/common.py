# -*- coding: utf-8 -*-
"""Common utilities for scraping"""
import hashlib
import json
import re
from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs
import html2text
import js2py
from bs4 import BeautifulSoup
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
            meta_key = meta_element.xpath("@itemprop").extract_first()
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
    remove_items.append({'tag': 'div', 'meta': {'class': 'ob-widget-header'}})
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
    try:
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
    except AttributeError:
        pass


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
        'Read more:',
        'Breaking News Emails',
        'Get breaking news alerts and special reports',
        'SIGN UP HERE'
    ]
    for bad_line_flag in bad_line_flags:
        markdown_text = '\n'.join(
            [line for line in markdown_text.split('\n') if bad_line_flag not in line])
    article.text.set_markdown_text(markdown_text)


def parse_authors(author_string, article):
    """Parses authors and appends them to an article"""
    bad_authors = [
        'CNN',
        'CNN Library',
        'Ars Staff'
    ]
    for author in author_string.split(','):
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


def author_from_json_author(json_author, article):
    """Finds the author from the JSON author"""
    if json_author['@type'] == 'Organization' or json_author['@type'] == 'NewsMediaOrganization':
        return None
    parse_authors(json_author['name'], article)


def handle_script_json_authors(script_json, article):
    """Handles the author parsing from the script JSON"""
    if 'author' in script_json:
        authors = script_json['author']
        if isinstance(authors, list):
            for author in authors:
                author_from_json_author(author, article)
        elif isinstance(authors, dict):
            author = authors
            author_from_json_author(author, article)


def handle_script_image_instance(image, article):
    """Handles the script image instance"""
    if 'url' in image:
        article.images.thumbnail.url = image['url']
    if 'width' in image:
        article.images.thumbnail.width = image['width']
    if 'height' in image:
        article.images.thumbnail.height = image['height']


def handle_script_image(script_json, article):
    """Handles the script image field in the JSON context"""
    if 'image' in script_json:
        image = script_json['image']
        if isinstance(image, basestring):
            article.images.thumbnail.url = image
        elif isinstance(image, list):
            for image_inst in image:
                handle_script_image_instance(image_inst, article)
        else:
            handle_script_image_instance(image, article)


def find_script_json(soup, article):
    """Finds the script JSON"""
    for script_tag in soup.findAll('script', {'type': 'application/ld+json'}):
        script_text = script_tag.text
        script_text = script_text.replace('\n', '')
        script_json = json.loads(script_text)
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


def common_response_data(response, parser='html5lib'):
    """Finds the common response data"""
    soup = BeautifulSoup(response.text, parser)
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
    keyword_keys = [
        'keywords',
        'news_keywords',
        'article:tag',
        'sailthru.tags'
    ]
    for keyword_key in keyword_keys:
        if keyword_key not in meta_tags:
            continue
        for keyword in meta_tags[keyword_key].split(','):
            article.tags.append(keyword.strip())


def parse_meta_tags_info(meta_tags, article):
    """Extracts the necessary meta tags into the article info"""
    description_keys = [
        'description',
        'og:description',
        'dcterms.abstract',
        'dc.description',
        'sailthru.description'
    ]
    for description_key in description_keys:
        if description_key not in meta_tags:
            continue
        article.info.description = meta_tags[description_key]
        break
    title_keys = [
        'og:title',
        'dc.title',
        'sailthru.title'
    ]
    for title_key in title_keys:
        if title_key not in meta_tags:
            continue
        article.info.title = meta_tags[title_key]
        break
    genre_keys = [
        'article:section',
        'cXenseParse:cbc-subsection1'
    ]
    for genre_key in genre_keys:
        if genre_key not in meta_tags:
            continue
        article.info.genre = meta_tags[genre_key]


def parse_meta_tags_time(meta_tags, article):
    """Extracts the necessary meta tags into the article time"""
    published_keys = [
        'article:published_time',
        'dc.date',
        'dcterms.created',
        'datePublished',
        'dateCreated',
        'date'
    ]
    for published_key in published_keys:
        if published_key not in meta_tags:
            continue
        article.time.set_published_time(meta_tags[published_key])
        break
    modified_keys = [
        'dc.date.modified',
        'article:modified_time',
        'dcterms.modified',
        'dateModified'
    ]
    for modified_key in modified_keys:
        if modified_key not in meta_tags:
            continue
        article.time.set_modified_time(meta_tags[modified_key])
        break


def parse_meta_tags_images(meta_tags, article):
    """Extracts the necessary meta tags into the article images"""
    image_keys = [
        'image',
        'og:image',
        'sailthru.image.thumb'
    ]
    for image_key in image_keys:
        if image_key not in meta_tags:
            continue
        article.images.thumbnail.url = meta_tags[image_key]
        break
    if 'og:image:width' in meta_tags:
        article.images.thumbnail.width = meta_tags['og:image:width']
    if 'og:image:height' in meta_tags:
        article.images.thumbnail.height = meta_tags['og:image:height']


def parse_meta_tags_publisher(meta_tags, article):
    """Extracts the necessary meta tags into the article publisher"""
    organisation_keys = [
        'og:site_name',
        'dc.publisher'
    ]
    for organisation_key in organisation_keys:
        if organisation_key not in meta_tags:
            continue
        article.publisher.organisation = meta_tags[organisation_key]
    if 'fb:pages' in meta_tags:
        article.publisher.facebook.page_ids.append(meta_tags['fb:pages'])
    if 'article:publisher' in meta_tags:
        article.publisher.facebook.url = meta_tags['article:publisher']
    if 'twitter:site' in meta_tags:
        article.publisher.twitter.handle = meta_tags['twitter:site']
    if 'twitter:title' in meta_tags:
        article.publisher.twitter.title = meta_tags['twitter:title']
    if 'twitter:description' in meta_tags:
        article.publisher.twitter.description = meta_tags['twitter:description']
    if 'twitter:image' in meta_tags:
        article.publisher.twitter.image = meta_tags['twitter:image']
    if 'twitter:card' in meta_tags:
        article.publisher.twitter.card = meta_tags['twitter:card']
    if 'fb:app_id' in meta_tags:
        article.publisher.facebook.app_id = meta_tags['fb:app_id']


def parse_meta_tags(meta_tags, article):
    """Extracts the necessary meta tags into the article"""
    parse_meta_tags_keywords(meta_tags, article)
    parse_meta_tags_info(meta_tags, article)
    parse_meta_tags_time(meta_tags, article)
    parse_meta_tags_images(meta_tags, article)
    parse_meta_tags_publisher(meta_tags, article)
    author_keys = [
        'author',
        'article:author',
        'dc.creator']
    for author_key in author_keys:
        if author_key not in meta_tags:
            continue
        parse_authors(meta_tags[author_key], article)


def find_common(soup, meta_tags, article):
    """Extracts common elements from the page"""
    parse_meta_tags(meta_tags, article)
    find_script_json(soup, article)


def find_common_response_data(response, parser='html5lib'):
    """Finds the common response data and parses it"""
    soup, meta_tags, article = common_response_data(response, parser=parser)
    find_common(soup, meta_tags, article)
    return soup, meta_tags, article


def find_author_content(author_content_divs, article, response, soup):
    """Finds the author content and fills in the article"""
    author_content_div = None
    for div in author_content_divs:
        author_content_div = soup.find(div['tag'], div['meta'])
        if author_content_div:
            break
    if not author_content_div:
        raise ValueError('Could not find the author content div: {}'.format(response.url))
    parse_authors(author_content_div.text, article)


def common_parse(response, remove_tags, main_tags, require_article=True, author_tag=None):
    """Perform common parsing on the response"""
    soup, meta_tags, article = find_common_response_data(response)
    if require_article:
        if 'og:type' not in meta_tags:
            return None
        if meta_tags['og:type'] != 'article':
            return None
    if author_tag is not None:
        find_author_content(author_tag, article, response, soup)
    remove_common_tags(remove_tags, soup)
    find_main_content(main_tags, article, response, soup)
    return article
