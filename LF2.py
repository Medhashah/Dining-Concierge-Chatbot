import json
import argparse
import pprint
from botocore.vendored import requests
import sys
import urllib
import datetime
import boto3


from boto3.dynamodb.conditions import Key, Attr
from ast import literal_eval


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode
    
API_KEY= "RhoiGjM-JuqZTSNIlW6CoNJVG4zYeh8AY-_iSnwYLcBgiqRjqWq0vWtcF9a5EXXTyxvh_P-SDf6Z4zi4MXlgnm5KYASg4XvDFD-K5TVG-SB8M3dqxwBPo8DUWn2bXXYx" 

def lambda_handler(event, context):
    
    

    sqs = boto3.client('sqs')

    queue_url = 'https://sqs.us-east-1.amazonaws.com/313591084191/Queue_1'
    
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    
    if('Messages' not in response):
        range_loop = 0
    else:
        range_loop = len(response['Messages'])
        
    #print(range_loop)
    for i in range(range_loop):
        message = response['Messages'][i]
        receipt_handle = message['ReceiptHandle']

        # # Delete received message from queue
        del_response = sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
      
    
        
        message = message['MessageAttributes']
        location = message['Location']['StringValue']
        party_people = message['PeopleNum']['StringValue']
        cuisine = message['Categories']['StringValue']
        timestamp = message['DiningTime']['StringValue']
        phone_number = message['Phone_number']['StringValue']
        Dining_Date = message['Dining_Date']['StringValue']
        print(cuisine)
        
        businessIds = []
        #cuisine = 'indian'
        url = 'https://search-restaurants-f3m3ryeapquwtywsuglhk7uvgu.us-east-1.es.amazonaws.com/restaurants/Restaurant/_search?q=' + cuisine
        r = requests.post(url)
        x = r.json()
        # print(x)
    
    
    
        for items in x['hits']['hits']:
            #print(items['_source']['RestaurantID'])
        
        #print(x['hits']['hits'][0]['_source']['RestaurantID'])
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
            table = dynamodb.Table('yelp-restaurants')
        #businessIds = []
            businessIds.append(items['_source']['RestaurantID'])
        
        output = getDynemoDbData(table,  businessIds)
        print(output)
        
        sns_client = boto3.client('sns')
        sns_client.publish(
            PhoneNumber=phone_number,
          Message="Hi, your results for the request for "+cuisine+" are as follows: "+ output
        )
        
        
    return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda! Projecty successuful')
        }

   
def getDynemoDbData(table,businessIds):
    
    if len(businessIds) <= 0:
        return 'We can not find any restaurant under this description, please try again.'
    
    # textString = "Hello! Here are my " + requestData['Categories']['StringValue'] + " restaurant suggestions for " + requestData['PeopleNum']['StringValue'] +" people, for " + requestData['DiningDate']['StringValue'] + " at " + requestData['DiningTime']['StringValue'] + ". "
    textString = ""
    count = 1
    
    for business in businessIds:
        responseData = table.query(KeyConditionExpression=Key('id').eq(business))
        #print(responseData['Items'][0])
    
        if len(responseData['Items']) >= 1 :
            responseData1 = responseData['Items'][0]
            location = str(responseData1['location'])
            python_dict = literal_eval(location)
            #dict=json.loads(location)
            # print(python_dict)
            # print(python_dict['display_address'][0])
            #print(str(location['display_address']))
            #display_address = ', '.join(responseData['display_address'])
            
            textString = textString + " " + str(count) + "." + responseData1['name'] + ", located at " + python_dict['display_address'][0] + " " + python_dict['display_address'][1]
            count += 1
        
    textString = textString + " Enjoy your meal!"
    #print(textString)
    return textString
    