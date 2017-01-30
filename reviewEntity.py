# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

import xmltodict
import dateUtil

class ReviewEntity:
    def __init__(self, entry):
        update_date_string = entry[u'updated']
        self.update_date = dateUtil.stringToLocalDateTimeWithISO8601(update_date_string)
        self.author_name = entry[u'author'][u'name']
        self.version = entry[u'im:version']
        self.title = entry[u'title']
        self.content = entry[u'content']
        self.rating = int(entry[u'im:rating'])

    def convertToSlackAttachment(self):
        star = ''
        for index in range(self.rating):
            star = star + ':star:'

        attachment = {
            'color': '#E84985',
            'author_name': self.author_name,
            'title': self.title,
            'text': self.content,
            'fields': [
                {
                    'title': 'Post date',
                    'value': self.update_date.strftime('%Y/%m/%d %H:%M')
                },
                {
                    'title': 'Rating',
                    'value': star
                },
                {
                    'title': 'Version',
                    'value': self.version
                }
            ]
        }

        return attachment
