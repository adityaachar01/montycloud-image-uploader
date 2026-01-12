#!/bin/bash

(cd lambdas/hello-world; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/get_presigned_url; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/list_images; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/store_image_metadata; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/delete_image; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/get_presigned_download_url; rm -f lambda.zip; zip lambda.zip handler.py)