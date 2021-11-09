import json
import logging

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

def lambda_handler(event, context):
    logging.info('Starting invocation of Lambda function: nm3223-hw2-lambdafunction1-indexphotos')
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
