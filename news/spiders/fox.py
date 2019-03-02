# -*- coding: utf-8 -*-
"""Parser for the Fox website"""
import json
from .article import Image
from .common import extract_link_id, find_common_response_data


def fox_url_parse(url):
    """Parses the URL from a Fox website"""
    return extract_link_id(url, lengths=[5])


def fox_parse(response):
    """Parses the response from a Fox Website"""
    link_id = fox_url_parse(response.url)
    if link_id is None:
        return None, link_id
    _, _, article = find_common_response_data(response)
    nuxt_tag = 'window.__NUXT__='
    json_text = response.text[response.text.find(nuxt_tag)+len(nuxt_tag):]
    json_text = json_text[0:json_text.find("</script>") - 1]
    nuxt = json.loads(json_text)
    full_articles = nuxt['state']['Articles']['fullArticles']
    markdown_text = ''
    for full_article_key in full_articles:
        full_article = full_articles[full_article_key]
        for component in full_article['components']:
            if component['is'] == 'paragraph':
                markdown_text += component['props']['text'] + '\n\n'
            if component['is'] == 'article-image':
                props = component['props']
                image = Image()
                markdown_text += '!['
                if 'imageAlt' in props:
                    image.alt = props['imageAlt']
                    markdown_text += image.alt
                markdown_text += ']'
                markdown_text += '('
                image.url = props['url']
                markdown_text += image.url
                markdown_text += ')\n\n'
                article.images.append_image(image)
    article.text.set_markdown_text(markdown_text)
    return article.json(), link_id


def fox_url_filter(_url):
    """Filters URLs in the Fox domain"""
    return True
