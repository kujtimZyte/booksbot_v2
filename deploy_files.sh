#!/bin/bash

# Change custom_settings if set
if [ ! -z "$NEWS_HTTP_USER" ]
then
    echo "Writing new custom_settings.py"
    cat >./news/spiders/custom_settings.py <<EOL
NEWS_HTTP_AUTH_USER = '$NEWS_HTTP_USER'
GCS_BUCKET_NAME = '$GCS_BUCKET_NAME'
GCP_PROJECT = '$GCP_PROJECT'
GCP_PRIVATE_KEY_ID = '$GCP_PRIVATE_KEY_ID'
GCP_PRIVATE_KEY = '$GCP_PRIVATE_KEY'
GCP_CLIENT_EMAIL = '$GCP_CLIENT_EMAIL'
GCP_CLIENT_ID = '$GCP_CLIENT_ID'
GCP_CLIENT_X509_CERT_URL = '$GCP_CLIENT_X509_CERT_URL'
EOL
else
    echo "Nothing to write for custom_settings.py"
fi
