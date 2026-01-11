#!/bin/bash

export AWS_DEFAULT_REGION=us-east-1

awslocal s3 mb s3://montycloud-images-aditya

# Create DynamoDB tables
echo "Creating DynamoDB tables..."

echo "Creating 'Images' table..."
awslocal dynamodb create-table \
    --table-name Images \
    --attribute-definitions \
        AttributeName=ID,AttributeType=S \
    --key-schema AttributeName=ID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --output text >/dev/null


awslocal lambda create-function \
    --function-name hello-world \
    --runtime python3.11 \
    --timeout 10 \
    --zip-file fileb://lambdas/hello-world/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{USERNAME=aditya}"

awslocal lambda wait function-active-v2 --function-name hello-world

awslocal lambda create-function-url-config \
    --function-name hello-world \
    --auth-type NONE

awslocal lambda create-function \
    --function-name get-presigned-url \
    --runtime python3.11 \
    --timeout 10 \
    --zip-file fileb://lambdas/get_presigned_url/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{BUCKET_NAME=montycloud-images-aditya}"

awslocal lambda wait function-active-v2 --function-name get-presigned-url

awslocal lambda create-function-url-config \
    --function-name get-presigned-url \
    --auth-type NONE

awslocal lambda create-function \
    --function-name list-images \
    --runtime python3.11 \
    --timeout 10 \
    --zip-file fileb://lambdas/list_images/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{BUCKET_NAME=montycloud-images-aditya,DYNAMODB_URL=http://localhost.localstack.cloud:4566}"

awslocal lambda wait function-active-v2 --function-name list-images

awslocal lambda create-function-url-config \
    --function-name list-images \
    --auth-type NONE


awslocal lambda create-function \
    --function-name delete-image \
    --runtime python3.11 \
    --timeout 10 \
    --zip-file fileb://lambdas/delete_image/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{BUCKET_NAME=montycloud-images-aditya,DYNAMODB_URL=http://localhost.localstack.cloud:4566}"

awslocal lambda wait function-active-v2 --function-name delete-image

awslocal lambda create-function-url-config \
    --function-name delete-image \
    --auth-type NONE



awslocal lambda create-function \
    --function-name store-image-metadata \
    --runtime python3.11 \
    --timeout 10 \
    --zip-file fileb://lambdas/store_image_metadata/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{BUCKET_NAME=montycloud-images-aditya,S3_ENDPOINT=http://localhost.localstack.cloud:4566,DYNAMODB_URL=http://localhost.localstack.cloud:4566}"

awslocal lambda wait function-active-v2 --function-name store-image-metadata

awslocal lambda create-function-url-config \
    --function-name store-image-metadata \
    --auth-type NONE

awslocal lambda add-permission \
    --function-name store-image-metadata \
    --action lambda:InvokeFunction \
    --statement-id s3-trigger \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::montycloud-images-aditya

awslocal s3api put-bucket-notification-configuration \
    --bucket montycloud-images-aditya \
    --notification-configuration file://triggers/file-upload.json

echo "Fetching function URL for 'hello-world' Lambda..."
awslocal lambda list-function-url-configs --function-name hello-world --output json | jq -r '.FunctionUrlConfigs[0].FunctionUrl'

echo "Fetching function URL for 'get-presigned-url' Lambda..."
awslocal lambda list-function-url-configs --function-name get-presigned-url --output json | jq -r '.FunctionUrlConfigs[0].FunctionUrl'

echo "Fetching function URL for 'list-images' Lambda..."
awslocal lambda list-function-url-configs --function-name list-images --output json | jq -r '.FunctionUrlConfigs[0].FunctionUrl'

echo "Fetching function URL for 'delete-image' Lambda..."
awslocal lambda list-function-url-configs --function-name delete-image --output json | jq -r '.FunctionUrlConfigs[0].FunctionUrl'
