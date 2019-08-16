"""
SQLクエリを書いてAthenaでデータをダウンロードし、DataFrameに読み込む
結果をS3に保存しているので、不要な場合は削除すること
"""

import pandas as pd
import s3fs
import boto3
import csv


DATABASE_REGION = '<aws region>'
DATABASE_NAME = '<database name defined by AWS Glue>'
OUTPUT_BUCKET = 's3://{}'.format('<S3 bucket for temporary result storage>')

# S3へのアクセス (../s3/file_handle_on_o3.py参照)
CREDENTIAL_FILE = 'credentials.csv'
USER_NAME = 'AWS -> IAM -> Userで作成したユーザ名'
CRED = pd.read_csv(CREDENTIAL_FILE, encoding='cp932', dtype=object, index_col='User name').to_dict()
S3_KEY = CRED['Access key ID'][USER_NAME]
S3_SECRET = CRED['Secret access key'][USER_NAME]

BUCKET = '<bucket name>'
BUCKET_KEY = '<path to file in a bucket>'
FILE_NAME = '<file name>'


def read_df_from_s3(s3_path, encoding='utf8', dtype=object, quoting=csv.QUOTE_MINIMAL, delimiter=','):
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    with fs.open(s3_path) as f:
        df = pd.read_csv(f, encoding=encoding, dtype=dtype, quoting=quoting, delimiter=delimiter)
        return df


def main():
    athena = boto3.client('athena', region_name=DATABASE_REGION)
    query = '<SQL Query>'

    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': DATABASE_NAME
        },
        ResultConfiguration={
            'OutputLocation': OUTPUT_BUCKET
        }
    )

    """
    response = {
        'QueryExecutionId': 'xxx',
        'ResponseMetadata': {
            'HTTPHeaders': {
                'connection': 'keep-alive',
                'content-length': 'xx',
                'content-type': 'application/x-amz-json-1.1',
                'date': 'Sat, 20 Jul 2019 07:48:49 GMT',
                'x-amzn-requestid': 'xxx'
            },
            'HTTPStatusCode': 200,
            'RequestId': 'xxx',
            'RetryAttempts': 0
        }
    }
    """

    # ステータスがSUCCEEDEDかFAILEDになるまで待つ
    status = 'RUNNING'
    exec_id = response['QueryExecutionId']
    while status not in ('SUCCEEDED', 'FAILED'):
        try:
            status = athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['State']
        except Exception as e:
            print(e)

    response_key = '/'.join([OUTPUT_BUCKET, response['QueryExecutionId'] + '.csv'])
    df = read_df_from_s3(response_key)

    print(df.describe())


if __name__ == '__main__':
    main()
