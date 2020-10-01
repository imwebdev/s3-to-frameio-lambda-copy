import json
from time import sleep
import boto3
from datetime import datetime

aws_client = boto3.client('lambda')


def child(event, context):
    sleep(5)
    print(f'Sleeping done at {datetime.now()}')
    
    return


def hello(event, context):
    i = 0
    while i < 10:
        resp = aws_client.invoke(
            FunctionName='s3-to-frameio-lambda-copy-dev-child',
            InvocationType='Event'
        )
        print(f'invo: {i}')
        print(resp)

        i += 1

    body = {
        "message": f"Returning at {datetime.now()}",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
