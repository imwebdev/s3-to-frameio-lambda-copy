### S3 to Frame.io Lambda copy

Serverless workflow to copy a bucket into a [Frame.io](https://frame.io) project using Lambda. [Medium article.](https://medium.com/@strombergdev/s3-to-frame-io-copy-using-lambda-8a671c8a574f)

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
    
   Setup AWS credentials: https://www.youtube.com/watch?v=KngM5bfpttA
    
    Open handler.py and add your Frame.io developer token.
    sls deploy



Trigger by making a [POST request](https://reqbin.com/req/v0crmky0/rest-api-post-example) with the below JSON content to your new endpoint.
    
    {
      "bucket": "your_bucket",
      "project": "your_frameio_project",
      "token": "your_frameio_dev_token"
    }


    *****************************
STEP BY STEP USING CLOUD 9

    Install Python 3.8 - https://tecadmin.net/install-python-3-8-amazon-linux/

Step by Step:
sudo yum install gcc openssl-devel bzip2-devel libffi-devel  zlib-devel
cd /opt
sudo wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
sudo tar xzf Python-3.8.12.tgz
cd Python-3.8.12
sudo ./configure --enable-optimizations
sudo make altinstall
sudo rm -f /opt/Python-3.8.12.tgz
python3.8 -V

INSTALL REPOSITORY (Run below commands)

git clone https://github.com/strombergdev/s3-to-frameio-lambda-copy.git
cd s3-to-frameio-lambda-copy 
npm install -g serverless
sls plugin install -n serverless-python-requirements

    Open handler.py and add your Frame.io developer token.
    sls deploy

SETUP SERVERLESS (Run below commands)
serverless (then follow prompts on screen to connect Github/AWS)
pip install pipenv
sudo cp /home/ec2-user/.local/lib/python3.7/site-packages/certifi/cacert.pem /usr/lib/python3.7/site-packages/pip/_vendor/certifi/
docker system prune --all --force
sls deploy

You will get results back like this
Serverless: Stack update finished...
Service Information
service: s3-to-frameio-lambda-copy
stage: dev
region: us-east-1
stack: s3-to-frameio-lambda-copy-dev
resources: 21
api keys:
  None
endpoints:
  POST - https://xxxxxx.us-east-1.amazonaws.com/dev/
functions:
  main: s3-to-frameio-lambda-copy-dev-main
  copy: s3-to-frameio-lambda-copy-dev-copy
layers:
  None
Serverless: Publishing service to the Serverless Dashboard...


TEST VIDEO PROCESSING 
Go to https://reqbin.com/req/v0crmky0/rest-api-post-example
For the URL type in the POST Endpoint URL you got from the previous step.  It should look like this: https://xxxxxx.us-east-1.amazonaws.com/dev/
Select the Content Tab and enter the below.  Substituting the values with your own

{
  "bucket": "lsg-recordings",
  "project": "S3Upload",
  "token": "XXXX"
}