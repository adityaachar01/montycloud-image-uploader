import json
import boto3
import pytest
from moto import mock_aws

@mock_aws
def test_list_images_with_filters(monkeypatch):
    
    print("\n\nStarting test_get_presigned_url\n\n")

    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    monkeypatch.setenv("BUCKET_NAME", "test-bucket")

    s3_client = boto3.client("s3")

    # Create a mock S3 bucket
    s3_client.create_bucket(Bucket="test-bucket")

    from lambdas.get_presigned_url.handler import handler

    print("Testing presigned URL generation\n\n")
    
    event = {"httpMethod": "GET"}

    response = handler(event, None)

    response_body = json.loads(response["body"])

    presigned_url = response_body.get("url", None)

    assert response["statusCode"] == 200

    assert presigned_url is not None

    print("\n\nCompleted test_get_presigned_url\n\n")