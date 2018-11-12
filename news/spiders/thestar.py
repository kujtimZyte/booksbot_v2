# -*- coding: utf-8 -*-
"""Parser for the Star website"""
import json
from bs4 import BeautifulSoup


def thestar_parse(response):
    """Parses the response from a Star website"""
    items = []
    for script_element in response.css("script"):
        script_text = script_element.xpath('text()').extract_first()
        if script_text is None:
            continue
        preloaded_state = 'window.__PRELOADED_STATE__ = '
        if preloaded_state in script_text:
            stripped_script = script_text.replace(preloaded_state, '')
            stripped_script = stripped_script.replace('<!--//--><![CDATA[//><!--', '')
            stripped_script = stripped_script.replace('//--><!]]>', '')
            json_page = json.loads(stripped_script)
            if 'body' not in json_page:
                continue
            item = {'articleBody': []}
            for body in json_page['body']:
                if body['type'] != 'text':
                    continue
                if 'text' not in body:
                    continue
                soup = BeautifulSoup(body['text'], 'html.parser')
                for paragraph in soup.find_all('p'):
                    item['articleBody'].append({
                        'text': paragraph.get_text()
                    })
            items.append(item)
            break
    return items
