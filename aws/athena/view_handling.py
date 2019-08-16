import boto3
import time
import datetime

QUERY_FILES = ['<query file to create view 0>', '<query file to create view 1>']
DATABASE_REGION = '<aws region>'
ATHENA_BUCKET = '<s3 bucket to store query output>'
ATHENA_BUCKET_PREFIX = '<s3 bucket prefix to store query output>'
DESTINATION_BUCKET = '<s3 bucket to store final result>'
DESTINATION_BUCKET_KEY = '<s3 key to store final result>'
DATABASE_NAME = '<database name in aws glue>'
TIMEOUT_IN_SEC = 300        # total time to wait for athena query done
WAIT_IN_SEC = 1             # interval to check if athena query done


def load_query(f):
    lines = open(f, encoding='utf8').readlines()

    query = ''.join(lines)

    return query


def create_view_by_athena(query, delete_log=True):
    athena = boto3.client('athena', region_name=DATABASE_REGION)
    output_bucket_key = 's3://{b}/{p}'.format(b=ATHENA_BUCKET, p=ATHENA_BUCKET_PREFIX)

    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': DATABASE_NAME
        },
        ResultConfiguration={
            'OutputLocation': output_bucket_key
        }
    )

    # ステータスがSUCCEEDEDかFAILEDになるまで待つ
    status = 'RUNNING'
    exec_id = response['QueryExecutionId']
    while status not in ('SUCCEEDED', 'FAILED'):
        try:
            status = athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['State']
        except Exception as e:
            print(e)

    response_key = '/'.join([ATHENA_BUCKET_PREFIX, response['QueryExecutionId'] + '.csv'])

    if delete_log:
        s3 = boto3.resource('s3')

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < TIMEOUT_IN_SEC:
            res = s3.Object(ATHENA_BUCKET, response_key).delete()
            if res['ResponseMetadata']['HTTPStatusCode'] == 204:
                break
            else:
                time.sleep(WAIT_IN_SEC)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

    return response_key


def download_view(query, result_bucket, result_key):
    athena = boto3.client('athena', region_name=DATABASE_REGION)
    output_bucket_key = 's3://{b}/{p}'.format(b=ATHENA_BUCKET, p=ATHENA_BUCKET_PREFIX)

    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': DATABASE_NAME
        },
        ResultConfiguration={
            'OutputLocation': output_bucket_key
        }
    )

    # ステータスがSUCCEEDEDかFAILEDになるまで待つ
    status = 'RUNNING'
    exec_id = response['QueryExecutionId']
    while status not in ('SUCCEEDED', 'FAILED'):
        try:
            status = athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['State']
        except Exception as e:
            print(e)

    response_key = '/'.join([ATHENA_BUCKET_PREFIX, response['QueryExecutionId'] + '.csv'])

    s3 = boto3.resource('s3')

    start_time = datetime.datetime.now()
    time_elapsed = (datetime.datetime.now() - start_time).seconds
    while time_elapsed < TIMEOUT_IN_SEC:
        res = s3.Object(result_bucket, result_key).copy_from(CopySource={'Bucket': ATHENA_BUCKET, 'Key': response_key})

        if res['ResponseMetadata']['HTTPStatusCode'] == 200:
            break
        else:
            time.sleep(WAIT_IN_SEC)
            time_elapsed = (datetime.datetime.now() - start_time).seconds

    start_time = datetime.datetime.now()
    time_elapsed = (datetime.datetime.now() - start_time).seconds
    while time_elapsed < TIMEOUT_IN_SEC:
        res = s3.Object(ATHENA_BUCKET, response_key).delete()
        if res['ResponseMetadata']['HTTPStatusCode'] == 204:
            break
        else:
            time.sleep(WAIT_IN_SEC)
            time_elapsed = (datetime.datetime.now() - start_time).seconds

    start_time = datetime.datetime.now()
    time_elapsed = (datetime.datetime.now() - start_time).seconds
    while time_elapsed < TIMEOUT_IN_SEC:
        res = s3.Object(ATHENA_BUCKET, response_key + '.metadata').delete()
        if res['ResponseMetadata']['HTTPStatusCode'] == 204:
            break
        else:
            time.sleep(WAIT_IN_SEC)
            time_elapsed = (datetime.datetime.now() - start_time).seconds


def lambda_handler(event, context):
    for f in QUERY_FILES:
        q = load_query(f)
        create_view_by_athena(q, delete_log=True)

    query = """
        SELECT
            *
        FROM {}
    """.format('<view name>')

    download_view(query, DESTINATION_BUCKET, DESTINATION_BUCKET_KEY)

