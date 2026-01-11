### Lambda function to Get Presigned URLs for uploading Images ###
import os
import boto3
import time
import json

s3_client = boto3.client("s3")

def handler(event, context):
    
    try:

        print(f"Received event: {json.dumps(event)}")

        bucket_name = os.getenv("BUCKET_NAME")
        
        default_filename = f"image_{int(time.time())}.jpg"        
        
        # 1. Use the dynamic name in the S3 Key
        object_key = f"images/{default_filename}"
        presigned_url = s3_client.generate_presigned_url("put_object",
            Params={"Bucket": bucket_name, "Key": object_key},
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