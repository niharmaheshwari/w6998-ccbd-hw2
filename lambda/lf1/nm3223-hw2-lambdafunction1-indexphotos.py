import json
import logging
import boto3
import urllib.parse

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
        logging.info(
            'The uploaded image does not have any customLabels. RequestId: {}'
            .format(response_body['ResponseMetadata']['RequestId'])
        )
    return labels

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
        'labels': labels
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
    

    return {
        'statusCode': 200,
        'body': get_resource(event, s3_client)
    }
