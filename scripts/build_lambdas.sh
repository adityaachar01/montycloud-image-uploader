#!/bin/bash

(cd lambdas/hello-world; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/get-presigned-url; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/list-images; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/store-image-metadata; rm -f lambda.zip; zip lambda.zip handler.py)

(cd lambdas/delete-image; rm -f lambda.zip; zip lambda.zip handler.py)