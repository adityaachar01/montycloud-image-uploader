
import os
import json

def handler(event, context):

    username = os.getenv("USERNAME", "default_user")
    print(f"Hello, {username}!")
    return {
        'statusCode': 200,
        'body': json.dumps({'message': f'Hello, {username}!'})        
    }