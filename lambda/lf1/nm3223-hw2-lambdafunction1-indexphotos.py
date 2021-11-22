from datetime import datetime
import json
import logging
import boto3
import urllib.parse
import requests
from dateutil.parser import parse
import datetime
from requests_aws4auth import AWS4Auth

# First Lambda Function - 1

# ES Lookup Configuration
ES_NAME = 'search-nm3223-hw2-photos-htltzo3ajr7twpke37rnijfzkm'
ES_REGION = 'us-east-1'
ES_HOST = 'https://' + ES_NAME + '.' + ES_REGION + '.es.amazonaws.com/'
PATH = 'photos'

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

def get_user_labels(response_body):
    '''
    Description
        Get the user defined lables from the S3 resoure being PUT
    Returns
        An array of user defined labels
    Note
        ResponseMetadata by default converts all keys to lowercase.
        Hence x-amz-meta-customLabels is converted to x-amz-meta-customlabels
        in the HTTP response.
    '''
    labels = []
    try:
        l = response_body['ResponseMetadata']
        l = l['HTTPHeaders']['x-amz-meta-customlabels']
        labels = [x.strip() for x in l.split(',')]
    except Exception as e:
        logging.info(str(response_body))
        logging.info(
            'The uploaded image does not have any customLabels. RequestId: {}'
            .format(response_body['ResponseMetadata']['RequestId'])
        )
    return labels

def get_creation_timestamp(response_body):
    '''
    Description
        Get the creation timestamp for the object
    Returns
        timestamp
    '''
    date = ''
    try:
        date = parse(response_body['ResponseMetadata']['HTTPHeaders']['date'])
        date = datetime.date.strftime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    except Exception as e:
        logging.info('Timestamp does not exist on the image mentioned')
    return date

def get_resource(event, s3_client):
    '''
    Description
        Get the s3 resource attached in the event
    Returns
        - resource bucket
        - URI of the resource
        - response body (s3 resource)
    '''
    response_body = {}
    labels = []
    bucket = event['Records'][0]['s3']['bucket']['name']
    uri = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8'
    )
    try:
        response_body = s3_client.get_object(Bucket=bucket, Key=uri)
        labels = get_user_labels(response_body)
        creation_timestamp = get_creation_timestamp(response_body)
    except Exception as e:
        logging.error(
            'An exception occured while fetching object from s3 event' +
            'Key: {}'.format(uri) + ' Bucket: {}'.format(bucket)
        )
        raise e
    return {
        'uri': uri,
        'bucket': bucket,
        'response_body': json.dumps(
            response_body, 
            indent=4, 
            sort_keys=True, 
            default=str
        ),
        'labels': labels,
        'creation_timestamp': creation_timestamp
    }

def get_rekognized_labels(rekognize_client, uri, bucket):
    '''
    Description
        Get auto-tagged labels from Rekognition
    Returns
        tags inferred from Rekognition
    Note
        Rekognition returns the labels in a camel case format.
        E.g. for an image of a tree, 'Tree' would be the label returned.
    '''
    response = rekognize_client.detect_labels(
        Image = {
            'S3Object':  {
                'Bucket': bucket,
                'Name': uri
                }
        },
        MaxLabels = 20
    )

    labels = []

    for l in response['Labels']:
        labels.append(l['Name'])
    return labels

def get_elastic_photo_view(image):
    return {
        'objectKey': image['uri'],
        'bucket': image['bucket'],
        'createdTimestamp': image['creation_timestamp'],
        'labels': image['labels']
    }

def lambda_handler(event, context):
    logging.info('Begin Invocation: nm3223-hw2-lambdafunction1-indexphotos')
    s3_client = boto3.client('s3')

    # Get Resource from S3
    response = get_resource(event, s3_client)

    # Use Rekognition to get auto-detected labels 
    rekognize_client = boto3.client('rekognition')
    rekognized_labels = get_rekognized_labels(
        rekognize_client,
        response['uri'],
        response['bucket']
    )

    # Merge manually tagged labels and inference labels
    response['labels'] = response['labels'] + rekognized_labels

    # Get a ES Client Credentials
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

    # Invoke and Index in Elastic
    el_resp = requests.put(
        url= ES_HOST + PATH + '/_doc/' + response['uri'],
        auth=aws_auth_creds,
        json=get_elastic_photo_view(response)
    )

    # Check Response
    logging.info('Elastic Response : %s', str(el_resp.text))

    return {
        'statusCode': 200,
        'body': 'SUCCESS'
    }
