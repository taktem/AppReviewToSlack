# coding:utf-8

from datetime import datetime, timedelta

# python2.7では%zが無効化されるので、ロケール反映した時刻に変換する
def stringToLocalDateTimeWithISO8601(date_string):
    result =  datetime.strptime(date_string[0:19], '%Y-%m-%dT%H:%M:%S')
    adjustTime = timedelta(hours=int(date_string[20:22]),minutes=int(date_string[23:]))

    if date_string[19] == '+':
        result += adjustTime
    elif date_string[19] == '-':
        result -= adjustTime

    return result

def scope_start_date(range):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return today - timedelta(days=range)
