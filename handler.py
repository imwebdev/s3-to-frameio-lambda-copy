import boto3
import frameioclient
import os
import mimetypes
import json

s3_client = boto3.client('s3')
frameio_client = frameioclient.FrameioClient(os.getenv('PIXELVIEW_FIO_TOKEN'))


class File:
    def __init__(self, name, path, size, parent_asset_id, bucket):
        self.name = name
        self.path = path
        self.size = size
        self.parent_asset_id = parent_asset_id
        self.bucket = bucket


def generate_s3_url(bucket, file_path):
    return s3_client.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket,
                                                    'Key': file_path})


def create_folder(parent_asset_id, name):
    return frameio_client.create_asset(
        parent_asset_id=parent_asset_id,
        name=name,
        type="folder"
    )


def upload_file(file):
    s3_url = generate_s3_url(file.bucket, file.path)

    frameio_client.create_asset(
        parent_asset_id=file.parent_asset_id,
        name=file.name,
        type="file",
        filetype=mimetypes.guess_type(file.name)[0],
        filesize=file.size,
        source={'url': s3_url}
    )


def project_root_asset_id(project_name):
    projects = []

    for team in frameio_client.get_all_teams():
        projects += frameio_client.get_projects(team['id'])

    for project in projects:
        if project['name'].lower() == project_name.lower():
            return project['root_asset_id']

    return None


def recursive_copy(bucket, path, parent_asset_id):
    result = s3_client.list_objects_v2(Bucket=bucket, Prefix=path, Delimiter='/')

    # Files in path
    for file in result.get('Contents'):
        if file.get('Size') != 0:
            upload_file(File(
                name=os.path.basename(file.get('Key')),
                path=file.get('Key'),
                size=file.get('Size'),
                parent_asset_id=parent_asset_id,
                bucket=bucket
            ))

    # Folders in path
    if result.get('CommonPrefixes'):  # If folders in path
        for folder in result.get('CommonPrefixes'):
            folder_path = folder.get('Prefix')

            new_frameio_folder = create_folder(
                parent_asset_id=parent_asset_id,
                name=os.path.basename(os.path.normpath(folder_path))
            )

            recursive_copy(
                bucket=bucket,
                path=folder_path,
                parent_asset_id=new_frameio_folder['id']
            )


def hello(event, context):
    # bucket = 'simplezapp'
    # project = 'test'

    # recursive_copy(bucket=bucket, path='', parent_asset_id=project_root_asset_id(project))

    body = {
        "message": f"Returning",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response