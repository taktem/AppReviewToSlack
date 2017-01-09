# coding:utf-8

import requests
import xml.etree.ElementTree as etree
from datetime import datetime, timedelta
import dateUtil
import postSlack
import reviewEntity

APPLE_URL = 'https://itunes.apple.com/jp/rss/customerreviews/id='

def postToSlack(slack_url, app_id):

    # アプリ評価xml取得
    apple_url = APPLE_URL + app_id + '/xml'

    response = requests.get(url=apple_url).text.encode('utf-8')
    root = etree.fromstring(response)

    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

    # 評価取得基準日
    scope_date = dateUtil.scope_start_date(range = 1)

    # 評価毎に処理開始
    attachments = []
    for entry in entries[1:]:
        entity = reviewEntity.ReviewEntity(entry)
        if entity.update_date < scope_date:
            print 'Out of date'
            continue

        attachment = entity.toSlackAttachment()
        attachments.append(attachment)

    slack = postSlack.PostSlack(slack_url = slack_url)
    slack.post(attachments)
