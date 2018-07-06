# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib'))

import boto3
import json
import requests
import xml.etree.ElementTree as etree
from datetime import datetime, timedelta, timezone
import dateutil.parser

s3Resource = boto3.resource('s3')
s3Client = boto3.client('s3')

APPLE_URL = 'https://itunes.apple.com/jp/rss/customerreviews/id='
bucket_name = 'BUCKET_NAME'

def scope_start_date(range):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today - timedelta(days=range)

def putToS3(key='', body=''):
    if not os.environ.get(bucket_name):
        print('S3 Bucket name is not set')
        return

    bucket = s3Resource.Bucket(os.environ[bucket_name])

    if None in [key, body]:
        ValueError('Missing required parameter')

    obj = bucket.Object(key)

    response = obj.put(
        Body=body.encode('utf-8'),
        ContentEncoding='utf-8',
        ContentType='text/tab-separated-values'
    )

    print('Put success: ' + key)

    expire = 60 * 60 * 24 * 30
    result = s3Client.generate_presigned_url(
        ClientMethod = 'put_object',
        Params = {'Bucket' : os.environ[bucket_name], 'Key' : key},
        ExpiresIn = expire,
        HttpMethod = 'GET')

    return result

class PostSlack:
    def __init__(self, slack_url, name = u'APP Store', emoji = u':apple:', channel_name = ''):
        # print slackURL
        self.slack_url = slack_url
        self.name = name
        self.emoji = emoji
        self.channel_name = channel_name

    def post(self, attachments):
        if attachments.count == 0:
            print('post data is empty')
            return

        payload = {
            'attachments': attachments,
            'username': self.name,
            'icon_emoji': self.emoji,
            'link_names': 1,
            'channel': self.channel_name
        }
        requests.post(self.slack_url, data = json.dumps(payload))

class ReviewEntity:
    def __init__(self, entry):
        update_date_string = entry.find('.//{http://www.w3.org/2005/Atom}updated').text.encode('utf-8')
        self.update_date = dateutil.parser.parse(update_date_string)
        self.author_name = entry.find('.//{http://www.w3.org/2005/Atom}author').find('.//{http://www.w3.org/2005/Atom}name').text.encode('utf-8')
        self.version = entry.find('.//{http://itunes.apple.com/rss}version').text.encode('utf-8')
        self.title = entry.find('.//{http://www.w3.org/2005/Atom}title').text.encode('utf-8')
        self.content = entry.find('.//{http://www.w3.org/2005/Atom}content').text.encode('utf-8')
        self.rating = int(entry.find('.//{http://itunes.apple.com/rss}rating').text)

    def convertToTSVRow(self):
        return ('\t').join([
            datetime.strftime(self.update_date, '%Y-%m-%dT%H:%M:%S'),
            self.author_name.decode('utf-8'),
            self.version.decode('utf-8'),
            self.title.decode('utf-8'),
            self.content.decode('utf-8').replace('\n', ''),
            str(self.rating)
        ])

    def convertToSlackAttachment(self):
        star = ''
        for index in range(self.rating):
            star = star + ':star:'

        dif = int(self.update_date.strftime("%Z %z")) / 100
        jstDateString = self.update_date + timedelta(hours=dif)
        attachment = {
            'color': '#E84985',
            'author_name': self.author_name.decode('utf-8'),
            'title': self.title.decode('utf-8'),
            'text': self.content.decode('utf-8'),
            'fields': [
                {
                    'title': 'Post date',
                    'value': jstDateString.strftime('%Y/%m/%d %H:%M')
                },
                {
                    'title': 'Rating',
                    'value': star
                },
                {
                    'title': 'Version',
                    'value': self.version.decode('utf-8')
                }
            ]
        }

        return attachment

def lambda_handler(event, context):
    def getDictValue(dict, key):
        if dict.get(key) != None:
            return dict.get(key)
        elif dict.get(key.lower()) != None:
            return dict.get(key.lower())

    # QueryStringParameters
    if not isinstance(event.get('queryStringParameters'), dict):
        raise ValueError('Missing required queries')

    slackUrl = getDictValue(dict = event['queryStringParameters'], key = 'slack_url')
    appId = getDictValue(dict = event['queryStringParameters'], key = 'app_id')
    dateScopeRange = getDictValue(dict = event['queryStringParameters'], key = 'date_scope_range')
    channelName = getDictValue(dict = event['queryStringParameters'], key = 'channel_name')

    print('Request resource {\n    slack_url: ' + slackUrl + '\n    app_id: ' + appId + '\n    date_scope_range: ' + str(dateScopeRange) + '\n    channel_name: ' + channelName + '\n}')
    apple_url = APPLE_URL + appId + '/sortBy=mostRecent/xml'

    response = requests.get(url=apple_url)
    response.encoding = 'utf-8'

    xml_string = response.text.encode('utf-8')
    root = etree.fromstring(xml_string)

    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

    if len(entries) == 0:
        print('Review is empty')
        return

    # Create reference range
    scope_date = scope_start_date(range = dateScopeRange)

    # Post all reviews
    attachments = []
    tsvRows = []

    app_name = entries[0].find('.//{http://itunes.apple.com/rss}name').text

    for entry in entries[1:]:
        entity = ReviewEntity(entry)
        if entity.update_date < scope_date:
            continue

        attachment = entity.convertToSlackAttachment()
        attachments.append(attachment)

        tsvRows.append(entity.convertToTSVRow())

    if attachments.count == 0:
        print('post data is empty')
        return

    tsv = ('\n').join(tsvRows)

    s3key = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S') + '.tsv'
    putToS3Result = putToS3(key=s3key, body=tsv)

    s3ResultAttachment = {
        'color': '#E84985',
        'title': 'TSV DATA',
        'title_link': putToS3Result
    }
    attachments.append(s3ResultAttachment)

    slack = PostSlack(slack_url = slackUrl, name = app_name, channel_name = channelName)
    slack.post(attachments)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {'data': putToS3Result}
    }
