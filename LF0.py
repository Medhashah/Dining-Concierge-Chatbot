import json
import boto3

client = boto3.client('lex-runtime')

def lambda_handler(event, context):
    
    response = client.post_text(
        botName='chatbot',
        botAlias='$LATEST',
        userId='admin',
        inputText=event["message"])
    #print("--------")
    #print(response)
    #print(response.message)
    inputText=event["message"]
    return {
        'statusCode': 200,
        'body': response#"Inside Lambda1" + inputText#response
    }