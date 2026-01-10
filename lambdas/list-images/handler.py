import os
import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

# Initialize dynamodb
dynamodb = boto3.resource("dynamodb", endpoint_url=os.getenv("DYNAMODB_URL", None))
images = dynamodb.Table('Images')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def is_valid_number(value):
    try:
        Decimal(str(value))
        return True
    except:
        return False

def handler(event, context):
    try:
        image_items = []

        last_key = None

        print(f"Received event: {json.dumps(event)}")
        query_params = event.get("queryStringParameters", {}) or None

        if not query_params:
            response = images.scan()
            print(f"===Response== {response}")
            image_items = response.get('Items', [])            

        else:
            
            attr_filter = None
            last_key_param = query_params.get("last_key", None)
            param_size_gte = query_params.get("size_gte", None)
            param_size_lte = query_params.get("size_lte", None)

            scan_kwargs = {}

            if last_key_param:
                last_key = json.loads(last_key_param)
                scan_kwargs['ExclusiveStartKey'] = last_key

            if param_size_gte and is_valid_number(param_size_gte):
                attr_filter = Attr('Size').gte(Decimal(param_size_gte))

            if param_size_lte and is_valid_number(param_size_lte):
                lte_filter = Attr('Size').lte(Decimal(param_size_lte))
                # Combine with AND if attr_filter already exists
                attr_filter = (attr_filter & lte_filter) if attr_filter else lte_filter

            if attr_filter:
                scan_kwargs['FilterExpression'] = attr_filter

            response = images.scan(**scan_kwargs)
            print(f"===Response with pagination== {response}")
            image_items = response.get('Items', [])
            last_key = response.get('LastEvaluatedKey', None)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data':image_items, 
                'lastKey':last_key
            }, 
            default=decimal_default)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to process: {str(e)}")
        }