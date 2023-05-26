import os
import tempfile
import boto3
import urllib3
from botocore.exceptions import ClientError
import json
import re


def upload_file_to_s3(file_path: str, s3_uri: str):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    s3_client = boto3.client('s3')

    parsed = urllib3.util.parse_url(s3_uri)
    bucket_name = parsed.hostname
    object_prefix = re.sub(r"\/{1,}$", "", parsed.path[1:])

    s3_client.upload_file(file_path, bucket_name, object_prefix)


STAGE = os.environ.get("STAGE", "dev")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "jocasso")


def get_secret(secret_name: str):
    secret_full_name = f"{STAGE}/{SERVICE_NAME}/{secret_name}"

    # Create a Secrets Manager client
    session = boto3.session.Session()

    client = session.client(
        service_name="secretsmanager"
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_full_name,
        )

    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    try:
        parsed = json.loads(secret)
        return parsed
    except:
        return secret


def check_s3_file_exists(s3_uri: str):
    parsed_uri = urllib3.util.parse_url(s3_uri)
    bucket_name = parsed_uri.hostname
    object_name = parsed_uri.path[1:]

    s3 = boto3.client('s3')

    try:
        s3.head_object(
            Bucket=bucket_name,
            Key=object_name,
        )

        return True

    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            print(e)


def download_s3_file(s3_uri: str):
    parsed_uri = urllib3.util.parse_url(s3_uri)
    bucket_name = parsed_uri.hostname
    object_name = parsed_uri.path[1:]
    basename = os.path.basename(s3_uri)

    filepath = os.path.join(tempfile.mkdtemp(), basename)

    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_name, filepath)

    return filepath
