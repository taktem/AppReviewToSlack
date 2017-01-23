# -*- coding: utf-8 -*-

import sys
import requests
import xml.etree.ElementTree as etree
from datetime import datetime, timedelta
import dateUtil
import postSlack
import reviewEntity

APPLE_URL = 'https://itunes.apple.com/jp/rss/customerreviews/id='

def postToSlack(slack_url, app_id, date_scope_range):

    # Create App review URL
    apple_url = APPLE_URL + app_id + '/xml'

    response = requests.get(url=apple_url).text.encode('utf-8')
    root = etree.fromstring(response)

    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

    # Create reference range
    scope_date = dateUtil.scope_start_date(range = date_scope_range)

    # Post all reviews
    attachments = []
    for entry in entries[1:]:
        entity = reviewEntity.ReviewEntity(entry)
        if entity.update_date < scope_date:
            print 'Out of date'
            continue

        attachment = entity.convertToSlackAttachment()
        attachments.append(attachment)

    if attachments.count == 0:
        print 'post data is empty'
        return

    slack = postSlack.PostSlack(slack_url = slack_url)
    slack.post(attachments)

def main():
    argvs = sys.argv
    argc = len(argvs)

    if argc < 4:
        return

    print argvs
    postToSlack(slack_url = argvs[1], app_id = argvs[2], date_scope_range = int(argvs[3]))

if __name__ == '__main__':
  main()
