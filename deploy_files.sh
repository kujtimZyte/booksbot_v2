#!/bin/bash

# Change custom_settings if set
if [ ! -z "$NEWS_HTTP_USER" ]
then
    echo "Writing new custom_settings.py"
    cat >./news/spiders/custom_settings.py <<EOL
NEWS_HTTP_AUTH_USER = '$NEWS_HTTP_USER'
GCS_BUCKET_NAME = '$GCS_BUCKET_NAME'
EOL
else
    echo "Nothing to write for custom_settings.py"
fi

# Create gcp-credentials if set
if [ ! -z "$GCP_PROJECT" ]
then
    echo "Writing new gcp-credentials.json"
    cat >./gcp-credentials.json <<EOL
{
  "type": "service_account",
  "project_id": "$GCP_PROJECT",
  "private_key_id": "$GCP_PRIVATE_KEY_ID",
  "private_key": "$GCP_PRIVATE_KEY",
  "client_email": "$GCP_CLIENT_EMAIL",
  "client_id": "$GCP_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "$GCP_CLIENT_X509_CERT_URL"
}
EOL
else
    echo "Nothing to write for gcp-credentials.json"
fi
