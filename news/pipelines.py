# -*- coding: utf-8 -*-
"""The pipeline for our news"""


class NewsPipeline(object):
    """The pipeline for a news site"""
    def process_item(self, item, spider):
        return item
