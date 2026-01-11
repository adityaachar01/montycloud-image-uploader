## The initial setup

### 1. Clone the repository using 
```
git clone https://github.com/adityaachar01/montycloud-image-uploader.git
```

### 2. Run the following commands to setup python environment
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

### 3. Run the command
   ```
   scripts/build_lambdas.sh
   ```

   This command will zip the lambda functions into individual lambda.zip files

### 4. Run the command    
    scripts/deploy.sh
   
   This command will do the following

   - Create s3 bucket
   - deploy lambda functions
   - create lambda function URLs
   - Give permissions to call the respective lambda on uploading images to s3 bucket

### 5. Run the command
    scripts/create-api-gateway
   
   This command will do the following:

   - Create "Container" REST API ImageServiceAPI 
   - Creates new resources
   - Creates method for the respective resource
   - Create integrations of the methods with the respective Lambda functions
   - Gives permissions to connect API gateway with lambdas


### 6. After running the command in step 5. you will get instructions to access URLs 
```
API Gateway setup complete. API ID: i60myflxrm
You can access the API endpoints at the following URLs:
GET | http://localhost:4566/restapis/i60myflxrm/dev/_user_request_/get-images
DELETE | http://localhost:4566/restapis/i60myflxrm/dev/_user_request_/delete-image/{imageid}
GET | http://localhost:4566/restapis/i60myflxrm/dev/_user_request_/get-presigned-url

OR

Simply use the following format:
http://i60myflxrm.execute-api.localhost.localstack.cloud:4566/dev/<ENPOINT>
Replace <ENDPOINT> with get-images, delete-image/{imageid}, or get-presigned-url as needed.
```



## Accessing the endpoints

### 1. Access the GET /get-presigned-url using 
```
curl --location 'http://<API_ID>.execute-api.localhost.localstack.cloud:4566/dev/get-presigned-url'
```
You will get url in response. Copy the entire value for usage in the next step.

### 2. Using the URL yielded in the step 1, make a PUT request to upload image

```
curl --location --request PUT '<URL-FROM-STEP-1>' \
--header 'Content-Type: image/jpeg' \
--data '@/your/path/to/resource/your-image.jpg'
```
This step uploads resource to S3 bucket and makes an entry of the metadata in DynamoDB

### 3. Access the GET /get-images using
```
curl --location 'http://<API_ID>.execute-api.localhost.localstack.cloud:4566/dev/get-images'
```
Lists out the uploaded images

Sample Response:
```
{
    "data": [
        {
            "Path": "images/image_1768132659.jpg",
            "Type": "image/jpeg",
            "UploadDate": "2026-01-11 11:57:50+00:00",
            "ID": "5418187d-7718-4451-8d83-90934b6c3314",
            "Bucket": "montycloud-images-aditya",
            "Size": 42771.0
        }
    ],
    "lastKey": null
}
```

### 4. Access the DELETE /delete-image/{imageid} to Delete an image
```
curl --location --request DELETE 'http://<API_ID>.execute-api.localhost.localstack.cloud:4566/dev/delete-image/<ID>'
```
Will delete entry from DynamoDB table Images and also delete resource from S3


