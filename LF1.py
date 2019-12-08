import json
import os
import math
import dateutil.parser
import datetime
import time
import logging
import boto3
from datetime import datetime
from botocore.vendored import requests
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def greeting_intent(intent_request):
    #return "Hi there, how can I help? Keval here"
    return {
        'dialogAction': {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            'message': {
                'contentType': 'PlainText', 
                'content': 'Hi there, how can I help? Keval here'}
        }
    }
  
def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }  
   
def thank_you_intent(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText', 
                'content': 'Thankyou for using our service. We hope you like it !!'}
        }
    }
    
def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
        
def validate_dining_suggestion(Location, Cuisine, Dining_Time, Number_of_people, Phone_number,Dining_Date):
    
        
    locations = ['brooklyn', 'new york', 'manhattan']
    if Location is not None and Location.lower() not in locations:
        return build_validation_result(False,
                                       'Location',
                                       'Please enter correct location')
                                       
    cuisines = ['indian', 'mexican', 'japanese','chinese', 'american']
    if Cuisine is not None and Cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'Cuisine',
                                       'Please enter correct Cuisine')
                                       
    if Number_of_people is not None:
        Number_of_people = int(Number_of_people)
        if Number_of_people > 50 or Number_of_people < 0:
            return build_validation_result(False,
                                      'Number_of_people',
                                      'Please add people betweek 0 to 50')
    
    x = str(datetime.now()).split()
    
    if Dining_Date is not None:
        if not isvalid_date(Dining_Date):
            return build_validation_result(False, 'Dining_Date', 'I did not understand that, what date would you like to add?')
        if x[0] > str(Dining_Date):
         #   print("inside Dining_date")
            return build_validation_result(False, 'Dining_Date', 'You can search restaurant from today onwards. What day would you like to search?')
        else:
           # print("outside Dining_date")
            print(x[0],str(Dining_Date))
    if Dining_Time is not None:
        print("========")
        print(Dining_Time)
        if len(Dining_Time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Dining_Time', None)

        hour, minute = Dining_Time.split(':')
        hour = int(hour)
        minute = int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Dining_Time', 'Not a valid time')

        if (hour < 10 or hour > 22) :
            # Outside of business hours
            return build_validation_result(False, 'Dining_Time', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')
        
        if (x[0]==str(Dining_Date) and (x[1] > str(Dining_Time) )):
            print("inside")
            return build_validation_result(False, 'Dining_Time', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')
        else:
            print("not inside")
    if Phone_number is not None :
        temp_Phone_number = Phone_number
        if len(Phone_number)!= 12 or not is_int(temp_Phone_number[1:]):
            return build_validation_result(False,
                                      'Phone_number',
                                      'Please enter correct phone format')
                                       
    return build_validation_result(True, None, None)

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def restaurantSQSRequest(requestData):
    
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/313591084191/Queue_1'
    delaySeconds = 5
    messageAttributes = {
        'Term': {
            'DataType': 'String',
            'StringValue': requestData['term']
        },
        'Location': {
            'DataType': 'String',
            'StringValue': requestData['location']
        },
        'Categories': {
            'DataType': 'String',
            'StringValue': requestData['categories']
        },
        "DiningTime": {
            'DataType': "String",
            'StringValue': requestData['Time']
        },
        "Dining_Date": {
            'DataType': "String",
            'StringValue': requestData['Dining_Date']
        },
        'PeopleNum': {
            'DataType': 'Number',
            'StringValue': requestData['peoplenum']
        },
        'Phone_number': {
            'DataType': 'Number',
            'StringValue': requestData['Phone_number']
        }
    }
    
    messageBody=('Recommendation for the food')
    
    response = sqs.send_message(
        QueueUrl = queue_url,
        DelaySeconds = delaySeconds,
        MessageAttributes = messageAttributes,
        MessageBody = messageBody
        )
    
    print ('send data to queue')
    print(response['MessageId'])
    
    return response['MessageId']

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }
    
def dining_suggestion_intent(intent_request):
    
    Location = get_slots(intent_request)["Location"]
    Cuisine = get_slots(intent_request)["Cuisine"]
    Dining_Time = get_slots(intent_request)["Dining_Time"]
    Number_of_people = get_slots(intent_request)["Number_of_people"]
    Phone_number = get_slots(intent_request)["Phone_number"]
    source = intent_request['invocationSource']
    Dining_Date = get_slots(intent_request)["Dining_Date"]
    
    # if not Cuisine:
    #     return {
    #     'dialogAction': {
    #         "type":"ElicitIntent",
    #         'message': {
    #             'contentType': 'PlainText', 
    #             'content': 'oooooooooooGot it.Enter cuisine you might be interested in' }
    #     }
    # }
    
    # print(Cuisine)
    
    if source == 'DialogCodeHook':
        slots = get_slots(intent_request) 
    
        validation_result = validate_dining_suggestion(Location, Cuisine, Dining_Time, Number_of_people, Phone_number,Dining_Date)
        
        print (validation_result)
        if not validation_result['isValid']:
                slots[validation_result['violatedSlot']] = None
                print(elicit_slot(intent_request['sessionAttributes'],
                                  intent_request['currentIntent']['name'],
                                  slots,
                                  validation_result['violatedSlot'],
                                  validation_result['message'])    )
                                   
                return elicit_slot(intent_request['sessionAttributes'],
                                  intent_request['currentIntent']['name'],
                                  slots,
                                  validation_result['violatedSlot'],
                                  validation_result['message'])    
        
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        
        print ('here')
        print ('uncomment below to get the ')
        return delegate(output_session_attributes, get_slots(intent_request))
        
        
    
    requestData = {
                    "term":Cuisine+", restaurants",
                    "location":Location,
                    "categories":Cuisine,
                    # "open_at": dt_unix,
                    "Phone_number": Phone_number,
                    "peoplenum": Number_of_people,
                    "Time": Dining_Time,
                    "Dining_Date": Dining_Date
                }
                
    messageId = restaurantSQSRequest(requestData)
                    
    print(messageId)
    
    print(Location+ "---" + Cuisine+ "---"  + Dining_Time+ "---"  + Number_of_people+ "---"  + Phone_number +"----" +messageId)
    
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText', 
                'content': 'You will receive the recommendations on the provided phone number shortly' }
        }
    }

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']
    print("asdd")
    print(intent_name)
    
    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greeting_intent(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return dining_suggestion_intent(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you_intent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')
    

def lambda_handler(event, context):
    # TODO implement
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }
    # By default, treat the user request as coming from the America/New_York time zone.

    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    print(event)
    return dispatch(event)