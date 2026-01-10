
import json

def handler(event, context):
    # Your handler code here
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from the presigned download URL handler!'
        })
    }