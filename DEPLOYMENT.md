## The AWS Secrets:
The app requires an AWS Secret named **prod/django/databade_url** formatted as a JSON dictionary (engine, username, password, host, port, dbname).

## Secrets required for GitHub Actions to run:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- VPC_SECURITY_GROUP_ID
- VPC_SUBNET_ID
- API_GATEWAY_STAGING

## AWS Amplify
In Amplify, specify the variable VITE_API_URL (backend api url)