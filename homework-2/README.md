
# AWS Infrastructure Monitoring

## Project Overview
- A Flask-based monitoring solution that provides real-time insights into AWS infrastructure components.
<br>This application enables to monitor AWS services through an intuitive dashboard and detailed API endpoints.


## Key Features

- **Real-time Monitoring**: Get up-to-date status of AWS resources
- **Secure Authentication**: AWS credentials management with session-based access

## Supported AWS Services

### Amazon S3
- Bucket inventory and properties
- Storage utilization and classification
- Lifecycle rule management
- Encryption status and security posture

## Environment Setup

- AWS IAM setup
  - Create IAM Group
  - Create Customer Managed IAM Policy (least priviledge)
    ```json
    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketPublicAccessBlock",
                "s3:GetEncryptionConfiguration",
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:GetBucketVersioning",
                "s3:GetBucketLocation"
            ],
            "Resource": "*"
        }
      ]
    }
    ```
  - Attach the IAM Policy to the IAM Group
  - Create IAM user in the IAM Group
  - For this IAM User, create Access keys for programmatic access
  - You will use those aws_access_key_id and aws_secret_access_key, to authenticate to the App

- SSL setup
  - HTTPS required for all communications with the Flask APP

  - Obtain SSL Certificates
    - You need SSL certificates for HTTPS to work. There are two options for this:
      - Self-Signed Certificates: 
        <br>You can generate your own SSL certificate and key for testing purposes, but this is not suitable for production.
      - Valid SSL Certificates: 
        <br>For production, you'll need to get an SSL certificate from a trusted Certificate Authority (CA)

    - How to Generate Self-Signed Certificates
      - This will generate a server.key (private key) and server.crt (public certificate) in the current directory.
      <br>You will use the generated server.key and server.crt later, when you will run the Flask App.
        ```bash
        openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -out server.crt
        ```
- App setup (Flask)
  - Go to the project folder
    ```bash
    cd homework-2
    ```

  - Create virtual env and activate it
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

  - Install python packages
    ```bash
    pip install -r requirements.txt
    ```

  - export PYTHONPATH
    ```bash
    export PYTHONPATH=$(pwd)
    ```

## How to start the App

- First make sure all the [Environment Setup](#environment-setup) is in place, as mentioned above.

- Run the Flask App
  - Once you have your certificates (either self-signed or from a trusted CA), 
  <br>you can configure Flask to use HTTPS by providing the certificate and key path to the run method.

  - Note regarding the --host flag
    - For testing on localhost use --host 127.0.0.1,
    <br>otherwise choose an ip of your choise, of the host interface the app run on, 
    <br>in which you want the App to serve request (--host 0.0.0.0 for all the host interfaces)

  - Note regarding port 443
    - Run Flask as a Superuser (Root) (Not Recommended for Production):
      <br>You can use sudo to run the Flask app with superuser privileges. This will allow Flask to bind to port 443. 
    - Use a Port Above 1024 (Recommended):
      <br>A safer, more common approach is to use a port number above 1024 for your Flask app. 
      <br>For example, you could use port 8443 for HTTPS instead of port 443.
  - Run the app (here we use localhost and port 8443)
    ```bash
    flask run --host 127.0.0.1 --port 8443 --cert=<path-to>/server.crt  --key=<path-to>/server.key 
    ```

  - Environment Variables (Optional)
    - If you want to use environment variables to specify the SSL certificate and key, 
    <br>you can set the environment variables and then run the Flask app
      ```bash
      export FLASK_RUN_CERT=server.crt  # Path to the certificate
      export FLASK_RUN_KEY=server.key   # Path to the private key
      ```
    - Run the app (here we dont provid the certificate and key path to the run method)
      ```bash
      flask run --host 127.0.0.1 --port 8443
      ```

## API Reference
- To use the Monitoring endpoints, you first need to authenticate to the app, using the "login" endpoint, 
<br>in order to obtain a token based session
- Session duration can range from 900 seconds (15 minutes), up to a maximum of 129,600 seconds (36 hours)
- This is configurable by setting SESSION_TIMEOUT_SECONDS in config.py file



- For ease of use, you can use "Postman" (Recomendation)
  - "Postman" Set the session coockie Header in subsecuent requests automatically after login.
  - Otherwise you will need to manually derive the session returned in "Set-Cookie" header in the login Reponse
  <br>and manually set "Cookie" header with this session value, when sending other APIs


#### Authentication

```
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "aws_access_key_id": "<aws_access_key_id>",
  "aws_secret_access_key": "<aws_secret_access_key>",
  "aws_region": "<aws_region>"
}
```

**Response:**
```json
{
  "expires_at": "2025-03-06T14:30:00Z"
}
```

#### S3 Monitoring

##### List Buckets

```
GET /api/v1/s3/buckets
```

**Response:**
```json
{
  "buckets": [
    {
      "name": "company-assets",
      "creation_date": "2023-01-15T10:30:00Z",
      "region": "us-west-2",
      "object_count": 15420,
      "total_size_bytes": 1073741824,
      "versioning_enabled": true,
      "public_access_blocked": true
    }
  ]
}
```

##### Get Bucket Details

```
GET /api/v1/s3/buckets/{bucket_name}/details
```

**Response:**
```json
{
  "name": "company-assets",
  "creation_date": "2023-01-15T10:30:00Z",
  "region": "us-west-2",
  "storage_class_summary": {
    "STANDARD": 1073741824,
    "STANDARD_IA": 536870912,
    "GLACIER": 268435456
  },
  "lifecycle_rules": [
    {
      "id": "archive-old-logs",
      "status": "Enabled",
      "transitions": [
        {
          "days": 30,
          "storage_class": "STANDARD_IA"
        },
        {
          "days": 90,
          "storage_class": "GLACIER"
        }
      ]
    }
  ],
  "encryption": {
    "enabled": true,
    "type": "AES256"
  }
}
```

#### Dashboard

(Currently Support only For S3)
```
GET /api/v1/dashboard/summary
```

**Response:**
```json
{
  "summary": {
    "ecs": {
      "total_clusters": 3,
      "total_services": 12,
      "total_tasks": 45,
      "unhealthy_services": 1
    },
    "s3": {
      "total_buckets": 8,
      "total_storage_gb": 1250,
      "buckets_without_encryption": 1,
      "publicly_accessible_buckets": 0
    },
    "ebs": {
      "total_volumes": 25,
      "total_storage_gb": 4500,
      "unattached_volumes": 2,
      "unencrypted_volumes": 3
    },
    "network": {
      "total_vpcs": 4,
      "total_subnets": 24,
      "security_groups_with_open_ssh": 2,
      "route_tables": 12
    }
  }
}
```

## How to test the App
- We test the app using "pytest"
- Test Environment Setup
  - First make sure all [Environment Setup](#environment-setup) is in place, as mentioned above.
  - AWS IAM setup (policy addition)
    - For pytest testing for S3 Monitoring, create and attach this custome policy 
    <br>to the IAM Group You created in IAM as part of the [Environment Setup](#environment-setup) mentioned above.
      ```json
        {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Sid": "VisualEditor0",
              "Effect": "Allow",
              "Action": [
                  "s3:PutObject",
                  "s3:GetLifecycleConfiguration",
                  "s3:PutBucketPublicAccessBlock",
                  "s3:DeleteObjectVersion",
                  "s3:PutLifecycleConfiguration",
                  "s3:ListBucketVersions",
                  "s3:CreateBucket",
                  "s3:DeleteObject",
                  "s3:DeleteBucket",
                  "s3:PutBucketVersioning"
              ],
              "Resource": "*"
          }
        ]
        }
      ```
  - Export env vars
    ```bash
    export AWS_ACCESS_KEY_ID='your_access_key_id'
    export AWS_SECRET_ACCESS_KEY='your_secret_access_key'
    export AWS_REGION='your-aws-region' # real region needed
    ```

- Run Tests
  - In your AWS test account, make sure no S3 buckets exist.
    <br>The tests for S3 create test buckets as part of the tests setup,
    <br>so test result will be expected!
  - Go to the project "tests" folder
    ```bash
    cd homework-2/tests
    ```

  - To run a specific test module, specifiy the test module name.
  <br>This will run all the tests in the module, for example to run all the auth related tests
    ```bash
    pytest -s -v --color=yes test_auth.py
    ```

  - To run All the test modules
    ```bash
    pytest -s -v --color=yes
    ```

  - To run test(s) which contains specific keywork in the name, use the -k flag
    ```bash
    pytest -s -v --color=yes -k <test-name-keyword>
    ```

