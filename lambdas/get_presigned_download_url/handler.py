
import os
import json
import boto3
from boto3.dynamodb.conditions import Key


s3_client = boto3.client("s3")
images = boto3.resource("dynamodb").Table('Images')
bucket_name = os.environ.get('BUCKET_NAME')

def modify_presigned_url(presigned_url):

    split_url = presigned_url.split('/')  

    split_url[2] = 'localhost:4566'        

    final_presigned_url = "/".join(split_url)

    return final_presigned_url
    
def handler(event, context):
    # Your handler code here
    try:
        image_id = event['pathParameters']['imageid']

        query_params = event.get('queryStringParameters') or {}

        is_download = query_params.get('download', 'false').lower() == 'true'

        image_data = images.query(
            KeyConditionExpression=Key('ID').eq(image_id)
        )        

        image_data_item = image_data.get('Items', [])

        if not image_data_item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }
        
        if 'Path' not in image_data_item[0] or not image_data_item[0]['Path']:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Image path missing in database record'})
            }
        # Get the s3 key from the database record
        s3_key = image_data_item[0]['Path']

        s3_params = {
            'Bucket': bucket_name,
            'Key': s3_key
        }

        if is_download:
            s3_params['ResponseContentDisposition'] = f'attachment; filename="{os.path.basename(s3_key)}"'
        
        # Generate the presigned URL for downloading
        url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params=s3_params,
                ExpiresIn=300 # Link valid for 5 minutes
            )

        return {
            'statusCode': 200,
            'body': json.dumps({                
                'url': modify_presigned_url(url)
            })
        }
    
    except Exception as e:

        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }