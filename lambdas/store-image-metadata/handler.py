import os
import boto3
import json
import uuid

print("Loading function store-image-metadata")
# Initialize clients
s3_client = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT", None))
print("Initialized S3 client")
dynamodb = boto3.resource("dynamodb", endpoint_url=os.getenv("DYNAMODB_URL", None))
print("Initialized DynamoDB resource")
table = dynamodb.Table('Images')


def handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")
        # 1. Loop through the S3 event records
        for record in event['Records']:
            print(f"Processing record: {record}")
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            print(f"Fetching metadata for object: s3://{bucket}/{key}")
            # 2. Fetch object details (Size, ContentType, etc.) from S3
            s3_metadata = s3_client.head_object(Bucket=bucket, Key=key)
            
            print(f"Fetched S3 metadata: {s3_metadata}")
            # 3. Prepare the item for DynamoDB
            image_item = {
                'ID': str(uuid.uuid4()),            # Unique ID for the DB entry
                'Path': key,                         # The S3 Key (e.g. images/photo.jpg)
                'Bucket': bucket,
                'Size': s3_metadata['ContentLength'],# Size in bytes
                'Type': s3_metadata['ContentType'],  # e.g. image/jpeg
                'UploadDate': str(s3_metadata['LastModified'])
            }
            
            print(f"Prepared DynamoDB item: {image_item}")
            # 4. Save to DynamoDB
            table.put_item(Item=image_item)
            print(f"Successfully indexed {key} into DynamoDB.")

        return {
            'statusCode': 200,
            'body': json.dumps("Metadata stored successfully")
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to process: {str(e)}")
        }