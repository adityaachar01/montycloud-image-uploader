#!/bin/bash

python3.11 -m pytest tests/test_list_images_with_filters.py -v -s
python3.11 -m pytest tests/test_get_presigned_url.py -v -s
python3.11 -m pytest tests/test_delete_image.py -v -s