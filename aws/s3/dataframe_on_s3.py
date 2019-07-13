import pandas as pd
import s3fs
import boto3
import io
import re

# S3へのアクセス
CREDENTIAL_FILE = 'credentials.csv'
USER_NAME = 'AWS -> IAM -> Userで作成したユーザ名'
CRED = pd.read_csv(CREDENTIAL_FILE, encoding='cp932', dtype=object, index_col='User name').to_dict()
S3_KEY = CRED['Access key ID'][USER_NAME]
S3_SECRET = CRED['Secret access key'][USER_NAME]

BUCKET = '<bucket name>'
BUCKET_KEY = '<path to file in a bucket>'
FILE_NAME = '<file name>'


def write_df_to_s3(df, s3_path):
    bytes_to_write = df.to_csv(None, index=False).encode()
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    with fs.open(s3_path, 'wb') as f:
        f.write(bytes_to_write)


def s3_key_exists(s3_path):
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    try:
        fs.ls(s3_path, refresh=True)
        return fs.exists(s3_path)
    except FileNotFoundError:
        return False


def find_files_in_s3(s3_path, full_path=False):
    """
        no need 's3://' for s3_path
    """
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    files = [f for f in fs.ls(s3_path, refresh=True)]

    if not full_path:
        files = [re.split('/', f)[-1] for f in files]

    return files


def read_df_from_s3(s3_path, encoding='utf8', dtype=object, quoting=csv.QUOTE_MINIMAL, delimiter=','):
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    with fs.open(s3_path) as f:
        df = pd.read_csv(f, encoding=encoding, dtype=dtype, quoting=quoting, delimiter=delimiter)
        return df


def read_df_from_s3_by_lambda(event, context):
    client = boto3.client('s3')
    key = event['Records'][0]['s3']['object']['key']
    obj = client.get_object(Bucket=BUCKET, Key=key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))

    return df


def test():
    data = pd.DataFrame()
    s3_path = '/'.join(['s3:/', BUCKET, BUCKET_KEY, FILE_NAME])
    write_df_to_s3(data, s3_path)


if __name__ == '__main__':
    test()
