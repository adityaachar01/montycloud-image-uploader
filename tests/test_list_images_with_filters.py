import os
import json
import boto3
import pytest
from moto import mock_aws

@mock_aws
def test_list_images_with_filters(monkeypatch):

    print("\n\nStarting test_list_images_with_filters\n\n")
    # monkeypatch.setenv("DYNAMODB_URL", "") 
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    # 1. Setup Mock DynamoDB
    db = boto3.resource("dynamodb", region_name="us-east-1")
    table = db.create_table(
        TableName="Images",
        KeySchema=[{'AttributeName': 'ID', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'ID', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    from lambdas.list_images.handler import handler

    # 2. Seed Data with Metadata
    table.put_item(Item={'ID': '1', 'Path': 'images/123456.jpg', 'Size': 10})
    table.put_item(Item={'ID': '2', 'Path': 'images/098767.jpg', 'Size': 5})
    table.put_item(Item={'ID': '3', 'Path': 'images/56789.jpg',   'Size': 2})

    print("Testing listing images with filters of size_gte param\n\n")
    # 3. Test Filter 1: Filter by Size
    event_filter_size_gte_five = {
        "queryStringParameters": {"size_gte": "5"}
    }
    
    response_filter_one = handler(event_filter_size_gte_five, None)
    response_body_one = json.loads(response_filter_one["body"])
    data_one = response_body_one.get('data',[])

    # Should find 2 images with size >= 5
    assert response_filter_one["statusCode"] == 200
    assert len(data_one) == 2

    print("Testing listing images with filters of size_lte param\n\n")
    # 4. Test Filter 2: Filter by Category AND Size
    event_filter_size_lte_four = {
        "queryStringParameters": {"size_lte": "4"}
    }

    response_filter_two = handler(event_filter_size_lte_four, None)
    response_body_two = json.loads(response_filter_two["body"])
    data_two = response_body_two.get('data',[])
    
    # Should find only 1 image (ID: 1)
    assert len(data_two) == 1
    assert data_two[0]['ID'] == '3'

    print("\n\nCompleted test_list_images_with_filters\n\n")