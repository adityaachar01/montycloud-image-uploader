
import json
import boto3
import os

s3_client = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT", None))
dynamodb = boto3.resource("dynamodb", endpoint_url=os.getenv("DYNAMODB_URL", None))
images = dynamodb.Table('Images')


def handler(event, context):    
    try:

        method = event.get('requestContext', {}).get('http', {}).get('method')

        ## Ensure only DELETE method is allowed
        if method != 'DELETE':
            return {
                'statusCode': 405,
                'body': json.dumps({'error': f'Method {method} not allowed. Use DELETE.'})
            }

        raw_path = event.get('rawPath', '')

        # Simple logic to get the image_id from the end of the path
        image_id = raw_path.split('/')[-1]

        response = images.delete_item(
        Key={'ID': image_id},
        ReturnValues='ALL_OLD'
        )

        ## Code to delete the actual image from S3 as well        
        s3_client.delete_object(Bucket=os.getenv("BUCKET_NAME", None), Key=image_id)

        # Check if 'Attributes' exists in the response
        # If it's there, the item existed. If not, the item was already gone.
        if 'Attributes' in response:
            return {
                'statusCode': 204, # Success, no content to return
                'body': json.dumps({'message': 'Image deleted successfully'})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }
    
    except Exception as e:

        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
