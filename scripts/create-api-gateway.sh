#!/bin/bash

export AWS_DEFAULT_REGION=us-east-1

echo "Creating API Gateway Container..."
# 1. Create the API and save the ID
API_ID=$(awslocal apigateway create-rest-api --name "ImageServiceAPI" --query 'id' --output text)

# 2. Get the Root Resource ID (the "/")
ROOT_ID=$(awslocal apigateway get-resources --rest-api-id $API_ID --query 'items[0].id' --output text)

echo "Creating API Gateway resources and methods..."
# Path 1: /get-images
GET_IMAGES_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part "get-images" --query 'id' --output text)

# Path 2: /delete-image/{imageid}
# We create 'delete-image' first, then the parameter under it
DELETE_BASE_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part "delete-image" --query 'id' --output text)
DELETE_PARAM_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $DELETE_BASE_ID --path-part "{imageid}" --query 'id' --output text)

# Path 3: /get-presigned-url/
PRESIGNED_ID=$(awslocal apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part "get-presigned-url" \
    --region us-east-1 --query 'id' --output text)

# Path 4: /get-presigned-download-url/{imageid}
DOWNLOAD_BASE_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part "get-presigned-download-url" --query 'id' --output text)
DOWNLOAD_PARAM_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $DOWNLOAD_BASE_ID --path-part "{imageid}" --query 'id' --output text)


echo "Creating methods and integrations..."
echo "Setting up GET /get-images"

awslocal apigateway put-method --rest-api-id $API_ID --resource-id $GET_IMAGES_ID --http-method GET --authorization-type "NONE"

awslocal apigateway put-integration --rest-api-id $API_ID --resource-id $GET_IMAGES_ID --http-method GET --type AWS_PROXY --integration-http-method POST \
--uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:list-images/invocations

echo "Setting up DELETE /delete-image/{imageid}"

awslocal apigateway put-method --rest-api-id $API_ID --resource-id $DELETE_PARAM_ID --http-method DELETE --authorization-type "NONE"

awslocal apigateway put-integration --rest-api-id $API_ID --resource-id $DELETE_PARAM_ID --http-method DELETE --type AWS_PROXY --integration-http-method POST \
--uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:delete-image/invocations

echo "Setting up GET /get-presigned-url"
awslocal apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $PRESIGNED_ID \
    --http-method GET \
    --authorization-type "NONE" \


# 3. Add the integration
awslocal apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $PRESIGNED_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:get-presigned-url/invocations \
    --region us-east-1

echo "Setting up GET /get-presigned-download-url/{imageid}"

awslocal apigateway put-method --rest-api-id $API_ID --resource-id $DOWNLOAD_PARAM_ID --http-method GET --authorization-type "NONE"

awslocal apigateway put-integration --rest-api-id $API_ID --resource-id $DOWNLOAD_PARAM_ID --http-method GET --type AWS_PROXY --integration-http-method POST \
--uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:get-presigned-download-url/invocations


echo "Deploying the API to 'dev' stage..."
awslocal apigateway create-deployment --rest-api-id $API_ID --stage-name dev

echo "Granting API Gateway permission to invoke Lambda functions..."

# Permission for list-images
awslocal lambda add-permission \
  --function-name list-images \
  --statement-id apigw-list \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:000000000000:$API_ID/*/*/*"

# Permission for delete-image
awslocal lambda add-permission \
  --function-name delete-image \
  --statement-id apigw-delete \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:000000000000:$API_ID/*/*/*"

# Permission for get-presigned-url
awslocal lambda add-permission \
  --function-name get-presigned-url \
  --statement-id apigw-presigned \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:000000000000:$API_ID/*/*/*"

# Permission for get-presigned-download-url
awslocal lambda add-permission \
  --function-name get-presigned-download-url \
  --statement-id apigw-download \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:000000000000:$API_ID/*/*/*"

echo "API Gateway setup complete. API ID: $API_ID"
echo "You can access the API endpoints at the following URLs:"
echo "GET Images: http://localhost:4566/restapis/$API_ID/dev/_user_request_/get-images"
echo "DELETE Image: http://localhost:4566/restapis/$API_ID/dev/_user_request_/delete-image/{imageid}"
echo "GET Presigned URL: http://localhost:4566/restapis/$API_ID/dev/_user_request_/get-presigned-url"
echo "GET Presigned Download URL: http://localhost:4566/restapis/$API_ID/dev/_user_request_/get-presigned-download-url/{imageid}"

echo -e "\n\n"

echo "OR"

echo -e "\n\n"

echo -e "Simply use the following format:\n"
echo "http://$API_ID.execute-api.localhost.localstack.cloud:4566/dev/<ENPOINT>"
echo -e "\n\n"
echo "Replace <ENDPOINT> with get-images, delete-image/{imageid}, get-presigned-url, get-presigned-download-url/{imageid} as needed."

echo "DONE!!"