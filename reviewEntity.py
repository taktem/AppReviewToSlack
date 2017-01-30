# -*- coding: utf-8 -*-

import xmltodict
import dateUtil

class ReviewEntity:
    def __init__(self, entry):
        update_date_string = entry.find('.//{http://www.w3.org/2005/Atom}updated').text.encode('utf-8')
        self.update_date = dateUtil.stringToLocalDateTimeWithISO8601(update_date_string)
        self.author_name = entry.find('.//{http://www.w3.org/2005/Atom}author').find('.//{http://www.w3.org/2005/Atom}name').text.encode('utf-8')
        self.version = entry.find('.//{http://itunes.apple.com/rss}version').text.encode('utf-8')
        self.title = entry.find('.//{http://www.w3.org/2005/Atom}title').text.encode('utf-8')
        self.content = entry.find('.//{http://www.w3.org/2005/Atom}content').text.encode('utf-8')
        self.rating = int(entry.find('.//{http://itunes.apple.com/rss}rating').text)

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
