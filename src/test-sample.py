import main

event = {
    "queryStringParameters": {
        "slack_url": [your slack incoming-webhook URL],
        "app_id": [your App_id],
        "date_scope_range": [date scope],
        "channel_name": [slack channel name]
    }
}

result = main.lambda_handler(event=event, context='')

print(result)
