### s3-to-frameio-lambda-copy

Serverless workflow to copy a bucket into a [Frame.io](https://frame.io) project using Lambda.

#### Features:
- Quick copy from S3 to Frame.io
- Handles any file and bucket size
- Preserves folder structure

#### Architecture:

- API Gateway triggers the workflow from a POST request
- Main Lambda verifies project info
- Copy Lambda copies S3 -> Frame.io
- Copy restarts itself if Lambda timeouts

Copying is done by generating a presigned S3 URL and sending it Frame.io for ingest.

#### Getting started:

Make sure you have npm and docker installed and running.
    
    git clone https://github.com/strombergdev/s3-to-frameio-lambda-copy.git
    cd s3-to-frameio-lambda-copy 
    npm install -g serverless
    sls plugin install -n serverless-python-requirements
    
    Open handler.py and add your Frame.io developer token.
    sls deploy