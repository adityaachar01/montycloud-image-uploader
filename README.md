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


### 6. After running the command in step 5 you will get instructions to access URLs 

## Using the End points
    
