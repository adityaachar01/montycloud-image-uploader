### Lambda function to Get Presigned URLs for uploading Images ###
import os
import boto3
import time
import json

s3_client = boto3.client("s3")

ALLOWED_EXTENSIONS = {'.jpg'}

def handler(event, context):
    
    try:

        print(f"Received event: {json.dumps(event)}")

        bucket_name = os.getenv("BUCKET_NAME")

        query_params = event.get('queryStringParameters') or {}

        # 1. Extract the filename
        filename = query_params.get('filename')
        
        # 2. Mandatory Check: If no filename, stop here
        if not filename:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing mandatory 'filename' query parameter."})
            }
        
        extension = os.path.splitext(filename)[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            return {
                "statusCode": 400, 
                "body": json.dumps({
                    "error": f"Unsupported file type '{extension}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                })
            }        
        
        # 3. Process the file details
        content_type = query_params.get('contentType', 'application/octet-stream')
        
        # 4. Create the unique key with RequestID prefix
        request_id = context.aws_request_id
        timestamp = int(time.time())
        
        # Using the original filename ensures the user sees their name on download
        object_key = f"images/{request_id}_{timestamp}_{filename}"
            
        
        # 1. Use the dynamic name in the S3 Key
        presigned_url = s3_client.generate_presigned_url("put_object",
            Params={"Bucket": bucket_name, 
                    "Key": object_key, 
                    "ContentType": content_type},
            ExpiresIn=3600)
        
        # 2. Modify the presigned URL to point to LocalStack S3 endpoint
        split_url = presigned_url.split('/')        
        split_url[2] = 'localhost:4566'        
        final_presigned_url = "/".join(split_url)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                "url": final_presigned_url
            })
        }
    
    except Exception as e:

        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }