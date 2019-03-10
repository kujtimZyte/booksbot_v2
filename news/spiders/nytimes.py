# -*- coding: utf-8 -*-
"""Parser for the NY Timees website"""
from .article import Image, Author
from .common import extract_link_id, find_common_response_data, \
execute_script, find_common


def nytimes_url_parse(url):
    """Parses the URL from a NY Times website"""
    return extract_link_id(url, lengths=[8])


def parse_image_block(image_block, initial_state):
    """Parses a NYT image block"""
    image = Image()
    alt = ''
    if 'legacyHtmlCaption' in image_block:
        alt += image_block['legacyHtmlCaption']
    alt += ' '
    if 'credit' in image_block:
        alt += image_block['credit']
    image.alt = alt.strip()
    for key in image_block:
        if key.startswith('crops('):
            for image_subblock in image_block[key]:
                image_crop = initial_state[image_subblock['id']]
                top_area = 0
                for image_rendition_ref in image_crop['renditions']:
                    image_rendition = initial_state[image_rendition_ref['id']]
                    area = image_rendition['width'] * image_rendition['height']
                    if area > top_area:
                        top_area = area
                        image.url = image_rendition['url'].encode('utf-8')
                        image.width = image_rendition['width']
                        image.height = image_rendition['height']
    return image


def parse_author_block(person_block):
    """Parses a person block from NYT"""
    author = Author()
    author.name = person_block['displayName']
    author.url = person_block['bioUrl'].encode('utf-8')
    return author


def parse_textinline_block(textinline_block, initial_state):
    """Parses a text in line block"""
    link_url = ''
    for text_format in textinline_block['formats']:
        if text_format['typename'] == 'LinkFormat':
            link_url = initial_state[text_format['id']]['url'].encode('utf-8')
    text = ''
    if link_url:
        text = '['
    for key in textinline_block:
        if key.startswith('text'):
            text += textinline_block[key]
    if link_url:
        text += '](' + link_url + ')'
    return text


def parse_byline_block(byline_block, final_article, initial_state):
    """Parses the byline block"""
    if 'creators' in byline_block:
        for person_block in byline_block['creators']:
            author = parse_author_block(initial_state[person_block['id']])
            final_article.authors.append(author)


def parse_content_block(content_block, final_article, initial_state, markdown):
    """Parses the content block"""
    typename = content_block['__typename']
    process_children = True
    if typename == 'Heading1Block':
        markdown += "\n# "
    elif typename == 'TextInline':
        markdown += parse_textinline_block(content_block, initial_state)
        process_children = False
    elif typename == 'Image':
        image = parse_image_block(content_block, initial_state)
        markdown += "\n![" + image.alt + "](" + image.url + ")"
        final_article.images.append_image(image)
        process_children = False
    elif typename == 'Byline':
        parse_byline_block(content_block, final_article, initial_state)
        process_children = False
    elif typename == 'ParagraphBlock':
        markdown += '\n'
    if process_children:
        for key in content_block:
            content_value = content_block[key]
            if isinstance(content_value, dict):
                if 'id' in content_value:
                    markdown = parse_content_block(
                        initial_state[content_value['id']],
                        final_article,
                        initial_state,
                        markdown)
            elif isinstance(content_value, list):
                for content_inner_value in content_value:
                    if 'id' in content_inner_value:
                        markdown = parse_content_block(
                            initial_state[content_inner_value['id']],
                            final_article,
                            initial_state,
                            markdown)
    return markdown


def parse_document_block(document_block, final_article, initial_state):
    """Parses the document block"""
    markdown = ''
    for key in document_block:
        document_value = document_block[key]
        if isinstance(document_value, list):
            item_ids = [x['id'] for x in document_value]
            for item_id in item_ids:
                markdown = parse_content_block(
                    initial_state[item_id],
                    final_article,
                    initial_state,
                    markdown)
    final_article.text.set_markdown_text(markdown)


def fetch_documents_tags(article):
    """Parses the documents and tags"""
    documents = []
    timetags = []
    for key in article:
        article_value = article[key]
        if article_value is None:
            continue
        if isinstance(article_value, dict):
            if 'typename' in article_value:
                if article_value['typename'] == 'DocumentBlock':
                    documents.append(article_value['id'])
        elif isinstance(article_value, list):
            if key.startswith('timesTags'):
                for timetag in article_value:
                    timetags.append(timetag['id'])
    return documents, timetags


def parse_initial_state(initial_state, final_article):
    """Parses the initial state JSON from the NY Times"""
    articles = []
    for key in initial_state:
        root_element = initial_state[key]
        if '__typename' in root_element:
            if root_element['__typename'] == 'Article':
                articles.append(root_element)
    for article in articles:
        if 'firstPublished' not in article:
            continue
        if 'lastModified' not in article:
            continue
        final_article.time.set_published_time(article['firstPublished'])
        final_article.time.set_modified_time(article['lastModified'])
        final_article.info.title = article['promotionalHeadline']
        final_article.info.description = article['promotionalSummary']
        documents, timetags = fetch_documents_tags(article)
        for document in documents:
            parse_document_block(initial_state[document], final_article, initial_state)
        for timetag in timetags:
            timetag_block = initial_state[timetag]
            final_article.tags.append(timetag_block['vernacular'])


def nytimes_parse(response):
    """Parses the response from a NY Times Website"""
    link_id = nytimes_url_parse(response.url)
    if link_id is None:
        return None, link_id
    soup, meta_tags, article = find_common_response_data(response)
    find_common(soup, meta_tags, article)
    for script_tag in soup.findAll('script'):
        context = execute_script(script_tag)
        if not hasattr(context, 'window'):
            continue
        if hasattr(context.window, '__preloadedData'):
            state = context.window['__preloadedData']
            if state is not None:
                initial_state = state['initialState']
                if initial_state is not None:
                    parse_initial_state(initial_state.to_dict(), article)
    return article.json(), link_id


def nytimes_url_filter(_url):
    """Filters URLs in the NY Times domain"""
    return True
