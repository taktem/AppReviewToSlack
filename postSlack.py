# coding:utf-8

import requests
import json

class PostSlack:
    def __init__(self, slack_url, name = u'APP Store', emoji = u':apple:'):
        # print slackURL
        self.slack_url = slack_url
        self.name = name
        self.emoji = emoji

    def post(self, attachments):
        if attachments.count == 0:
            print 'post data is empty'
            return

        payload = {
            'attachments': attachments,
            'username': self.name,
            'icon_emoji': self.emoji,
            'link_names': 1
        }
        requests.post(self.slack_url, data = json.dumps(payload))
