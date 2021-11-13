import json
import logging
import boto3
import datetime
import requests
from requests_aws4auth import AWS4Auth
from copy import deepcopy

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

DEFAULT_TEXT = 'Say or Type-in something to start searching ..'
ES_NAME = 'search-nm3223-hw2-photos-htltzo3ajr7twpke37rnijfzkm'
ES_REGION = 'us-east-1'
ES_HOST = 'https://' + ES_NAME + '.' + ES_REGION + '.es.amazonaws.com/'
PATH = 'photos'


def format_success_response(message):
    return {
        'statusCode' : 200,
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'message': {
            'id': '0',
            'text': message,
            'timestamp': str(datetime.datetime.today())
        }
    }

def process_lex_response(response):
    labels = []
    if 'slots' in response:
        for slot in response['slots']:
            labels.append(response['slots'][slot])
    return labels

def get_elastic_query(labels):
    unit = {
        'fuzzy': {
            'labels': {
                'value': None,
                'fuzziness': 'AUTO'
            }
        }
    }
    should = []
    for l in labels:
        u = deepcopy(unit)
        u['fuzzy']['labels']['value'] = l
        should.append(u)
    return {
        'query': {
            'bool': {
                'should': should
            }
        }
    }
 
def lambda_handler(event, context):

    lex_runtime = boto3.client('lex-runtime')

    # Get latest user messages
    logging.info('Event : {}'.format(str(event)))
    msg = event["queryStringParameters"]['q']

    # Set the guest user
    usr = 'guest'
    labels = []

    if msg is None or len(msg) < 1:
        return format_success_response(DEFAULT_TEXT)

    resp = lex_runtime.post_text(
        botName = 'PhotoSearchQueries',
        botAlias = 'photoSearchBot',
        userId = usr,
        inputText = msg
    )

    labels = process_lex_response(resp)
    labels = [x for x in labels if x is not None]
    logging.info('Labels: {}'.format(str(labels)))
    credentials = boto3.Session().get_credentials()
    aws_auth_creds = AWS4Auth(
        credentials.access_key, 
        credentials.secret_key, 
        ES_REGION, 
        'es', 
        session_token=credentials.token
    )

    # Get Creds for Postman Requests to ES
    logging.info('Access Key : %s', credentials.access_key)
    logging.info('Secret Key : %s', credentials.secret_key)
    logging.info('Region Key : %s', ES_REGION)
    logging.info('Session Key: %s', credentials.token)
    logging.info('Elastic Search Query : %s' , json.dumps(get_elastic_query(labels)))

    # Invoke and Index in Elastic
    el_resp = requests.get(
        url=ES_HOST + PATH + '/_search',
        auth=aws_auth_creds,
        json=get_elastic_query(labels)
    )

    logging.info('Elastic Response : %s', str(el_resp.text))

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': el_resp.text
    }
