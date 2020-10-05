import boto3
from botocore.client import ClientError, Config
import frameioclient
import os
import mimetypes
import json
from time import time

###### ADD YOUR TOKEN HERE ######
FRAMEIO_TOKEN = 'your_token'

s3 = boto3.resource('s3')
lambda_client = boto3.client('lambda', config=Config(region_name='us-east-1'))
frameio_client = frameioclient.FrameioClient(FRAMEIO_TOKEN)
LAMBDA_TIMEOUT = 720    # 12 minutes


class Asset:
    def __init__(self, name, path, size, parent_asset_id, bucket_name, is_file):
        self.name = name
        self.path = path
        self.size = size
        self.parent_asset_id = parent_asset_id
        self.bucket_name = bucket_name
        self.is_file = is_file


def generate_s3_url(bucket, file_path):
    return s3.meta.client.generate_presigned_url('get_object',
                                                 Params={'Bucket': bucket,
                                                         'Key': file_path})


def create_folder(name, parent_asset_id):
    return frameio_client.create_asset(
        parent_asset_id=parent_asset_id,
        name=name,
        type="folder"
    )


def upload_file(file):
    s3_url = generate_s3_url(file.bucket_name, file.path)

    frameio_client.create_asset(
        parent_asset_id=file.parent_asset_id,
        name=file.name,
        type="file",
        filetype=mimetypes.guess_type(file.name)[0],
        filesize=file.size,
        source={'url': s3_url}
    )


def project_root_asset_id(project_name):
    """Translate project name into project root_asset_id"""
    projects = []

    for team in frameio_client.get_all_teams():
        projects += frameio_client.get_projects(team['id'])

    for project in projects:
        if project['name'].lower() == project_name.lower():
            return project['root_asset_id']

    return None


def lambda_timeout(start_time):
    if time() - start_time > LAMBDA_TIMEOUT:
        return True

    return False


def copy(event, context):
    """Copy files and folders from S3 to Frame.io. Restart if Lambda timeouts"""
    bucket_name = event['bucket_name']
    previous_asset = event['previous_asset']
    continued_run = event['continued_run']
    parent_ids = event['parent_ids']

    start_time = time()
    previous_folder = ''

    objects = s3.Bucket(bucket_name).objects.all()
    for object in objects:
        # If this lambda continues where another left of, first iterate down to the last uploaded file.
        if continued_run == 'true':
            if object.key == previous_asset:
                continued_run = 'false'
            continue

        # Delete finished folder from parent_ids dict to keep size down.
        current_folder = os.path.dirname(object.key[:-1])
        if len(current_folder) < len(previous_folder):     # We've moved back up in folder structure
            del parent_ids[previous_folder]

        # If lambda timeout is getting close, spawn a new one and end this one.
        if lambda_timeout(start_time):
            lambda_client.invoke(
                FunctionName='s3-to-frameio-lambda-copy-dev-copy',
                InvocationType='Event',
                Payload=json.dumps({
                    'bucket_name': bucket_name,
                    'previous_asset': previous_asset,
                    'continued_run': 'true',
                    'parent_ids': parent_ids})  # Dict with folder:asset_id pairs. '' is root.
            )

            return

        # Process files and folders.
        if object.key.endswith('/'):
            asset = Asset(
                name=os.path.basename(os.path.normpath(object.key)),
                is_file=False,
                path=object.key,
                size=0,
                parent_asset_id=parent_ids[current_folder],
                bucket_name=bucket_name
            )

        else:
            asset = Asset(
                name=os.path.basename(object.key),
                is_file=True,
                path=object.key,
                size=object.Object().content_length,
                parent_asset_id=parent_ids[current_folder],
                bucket_name=bucket_name
            )

        if asset.is_file:
            print(f'Uploading file: {object.key}')
            upload_file(asset)

        else:
            print(f'Creating folder: {object.key}')
            new_folder = create_folder(
                name=asset.name,
                parent_asset_id=asset.parent_asset_id
            )

            parent_ids[asset.path[:-1]] = new_folder['id']

        previous_asset = object.key
        previous_folder = current_folder


def main(event, context):
    """Validate POST request and trigger Lambda copy function."""
    try:
        body = json.loads(event['body'])

        bucket = body['bucket']
        project = body['project']
        token = body['token']

    except (TypeError, KeyError):
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Please provide bucket, project and token"})
        }

    # Simple authentication
    if not token == FRAMEIO_TOKEN:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Unauthorized"})
        }

    # Validate project and bucket
    root_asset_id = project_root_asset_id(project)
    if not root_asset_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Unable to find Frame.io project {project}"})
        }

    try:
        s3.meta.client.head_bucket(Bucket=bucket)
    except ClientError as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Unable to find bucket {bucket}"})
        }

    lambda_client.invoke(
        FunctionName='s3-to-frameio-lambda-copy-dev-copy',
        InvocationType='Event',
        Payload=json.dumps({
            'bucket_name': bucket,
            'previous_asset': '',
            'continued_run': 'false',
            'parent_ids': {'': root_asset_id}})     # Dict with folder:asset_id pairs. '' is root.
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Copy started!"})
    }
