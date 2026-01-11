import json
import boto3
import pytest
from moto import mock_aws

@mock_aws
def test_list_images_with_filters(monkeypatch):
    
    print("\n\nStarting test_delete_image\n\n")

    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    monkeypatch.setenv("BUCKET_NAME", "test-bucket")

    # 1. Setup Mock DynamoDB
    db = boto3.resource("dynamodb", region_name="us-east-1")

    s3_client = boto3.client("s3")

    s3_client.create_bucket(Bucket="test-bucket")

    table = db.create_table(
        TableName="Images",
        KeySchema=[{'AttributeName': 'ID', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'ID', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    # 2. Seed Data with Metadata
    table.put_item(Item={'ID': '1', 'Path': 'images/123456.jpg', 'Size': 10})
    table.put_item(Item={'ID': '2', 'Path': 'images/098767.jpg', 'Size': 5})
    table.put_item(Item={'ID': '3', 'Path': 'images/56789.jpg',   'Size': 2})

    from lambdas.delete_image.handler import handler

    handler_event = {
        "pathParameters": {
            "imageid": "2"
        }
    }

    print("Testing deletion of image with ID 2\n\n")

    handler_response = handler(handler_event, None)

    print("Delete Image Response:", handler_response)

    assert handler_response["statusCode"] == 200

    print("Testing deletion of non existing entry with ID 999\n\n")

    handler_event_not_found = {
        "pathParameters": {
            "imageid": "999"
        }
    }

    handler_response_not_found = handler(handler_event_not_found, None)

    print("Delete Image Not Found Response:", handler_response_not_found)    

    assert handler_response_not_found["statusCode"] == 404

    print("\n\nCompleted test_delete_image\n\n")