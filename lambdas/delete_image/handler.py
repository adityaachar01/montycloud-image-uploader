
import json
import boto3
import os
from boto3.dynamodb.conditions import Key

s3_client = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT", None))
dynamodb = boto3.resource("dynamodb", endpoint_url=os.getenv("DYNAMODB_URL", None))
images = dynamodb.Table('Images')


def handler(event, context):    
    try:

        # 1. Safely get pathParameters (prevents NoneType errors)
        path_params = event.get('pathParameters') or {}
        
        # 2. Access the 'imageid' key (matches the {imageid} in your script)
        image_id = path_params.get('imageid')

        if not image_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing Image ID in path"})
            }

        # 2. Query DynamoDB to find the record
        response = images.query(
            KeyConditionExpression=Key('ID').eq(image_id)
        )
        items = response.get('Items', [])

        if not items:
            return {"statusCode": 404, "body": "Image record not found in database"}
        # 3. Get the Path from the result
        s3_key_to_delete = items[0].get('Path')
        

        if s3_key_to_delete:
            # 4. Delete from S3
            s3_client.delete_object(Bucket=os.environ['BUCKET_NAME'], Key=s3_key_to_delete)

            # 5. Delete from DynamoDB
            images.delete_item(Key={'ID': image_id})

            return {
                "statusCode": 200, 
                "body": json.dumps({
                    "message": f"Deleted record {image_id} and S3 object {s3_key_to_delete}"
                })
            }
    
        return {"statusCode": 500, "body": "Record found, but S3 key was missing"}
    
    except Exception as e:

        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
