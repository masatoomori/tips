import boto3
import time
import datetime
import io
import pandas as pd
from io import StringIO
import re

DEFAULT_TIMEOUT_IN_SEC = 300
DEFAULT_WAIT_IN_SEC = 1


class SingleResult:
    timeout_in_sec = DEFAULT_TIMEOUT_IN_SEC
    wait_in_sec = DEFAULT_WAIT_IN_SEC
    response_keys = list()
    query_for_view_creation = None
    df_result = pd.DataFrame()

    def __init__(self, db_region, db_name, bucket, prefix):
        self.db_name = db_name
        self.result_bucket = bucket
        self.result_prefix = prefix
        self.athena = boto3.client('athena', region_name=db_region)

    def __del__(self):
        print('deleting SimpleAthena instance...')
        if self.response_keys:
            print('consider to delete files in S3://{b}/{p};'.format(b=self.result_bucket, p=self.result_prefix))
        else:
            print('no result file remains in S3://{b}/{p};'.format(b=self.result_bucket, p=self.result_prefix))
        for k in self.response_keys:
            print(k)

    def set_timeout_in_sec(self, x):
        self.timeout_in_sec = x

    def set_wait_in_sec(self, x):
        self.wait_in_sec = x

    def get_response_keys(self):
        return self.response_keys

    def get_view(self):
        return self.df_result

    def get_table(self):
        return self.df_result

    def get_query(self):
        return self.query_for_view_creation

    def __wait_for_execution_done(self, response):
        # ステータスがSUCCEEDEDかFAILEDになるまで待つ
        status = 'RUNNING'
        exec_id = response['QueryExecutionId']

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < self.timeout_in_sec:
            try:
                status = self.athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['State']
            except Exception as e:
                print(e)
            if status in ('SUCCEEDED', 'FAILED'):
                break
            else:
                time.sleep(self.wait_in_sec)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

    def __delete_log(self, response_key):
        s3 = boto3.resource('s3')

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < self.timeout_in_sec:
            res = s3.Object(self.result_bucket, response_key).delete()

            if res['ResponseMetadata']['HTTPStatusCode'] == 204:
                break
            else:
                time.sleep(self.wait_in_sec)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

    def __delete_result(self, response_key, and_metadata=False):
        s3 = boto3.resource('s3')

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < self.timeout_in_sec:
            res = s3.Object(self.result_bucket, response_key).delete()
            if res['ResponseMetadata']['HTTPStatusCode'] == 204:
                break
            else:
                time.sleep(self.wait_in_sec)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

        if and_metadata:
            start_time = datetime.datetime.now()
            time_elapsed = (datetime.datetime.now() - start_time).seconds
            while time_elapsed < self.timeout_in_sec:
                res = s3.Object(self.result_bucket, response_key + '.metadata').delete()
                if res['ResponseMetadata']['HTTPStatusCode'] == 204:
                    break
                else:
                    time.sleep(self.wait_in_sec)
                    time_elapsed = (datetime.datetime.now() - start_time).seconds

    def create_view(self, query, delete_log=True):
        if query.upper().startswith('CREATE OR REPLACE VIEW') or query.upper().startswith('CREATE VIEW'):
            output_bucket_key = 's3://{b}/{p}'.format(b=self.result_bucket, p=self.result_prefix)
            self.query_for_view_creation = query

            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': self.db_name
                },
                ResultConfiguration={
                    'OutputLocation': output_bucket_key
                }
            )

            self.__wait_for_execution_done(response)

            response_key = '/'.join([self.result_prefix, response['QueryExecutionId']])

            if delete_log:
                self.__delete_log(response_key + '.csv')
                self.__delete_log(response_key + '.txt')
            else:
                self.response_keys.append(response_key + '.csv/txt')

            view_name = re.split(' ', re.split('\n', query)[0])[-2]

            return view_name

        else:
            print('query should starts with "CREATE OR REPLACE VIEW" or "CREATE VIEW"')
            print('----------------------------------------')
            print(query)
            print('----------------------------------------')
            return None

    def download_table(self, query, keep_result=True):
        if query.upper().startswith('SELECT'):
            output_bucket_key = 's3://{b}/{p}'.format(b=self.result_bucket, p=self.result_prefix)

            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': self.db_name
                },
                ResultConfiguration={
                    'OutputLocation': output_bucket_key
                }
            )

            self.__wait_for_execution_done(response)

            response_key = '/'.join([self.result_prefix, response['QueryExecutionId'] + '.csv'])

            client = boto3.client('s3')
            obj = client.get_object(Bucket=self.result_bucket, Key=response_key)

            self.df_result = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8', dtype=object)

            if keep_result:
                self.response_keys.append(response_key)
                self.response_keys.append(response_key + '.metadata')
            else:
                self.__delete_result(response_key, and_metadata=True)

            return self.df_result
        else:
            print('query should starts with "SELECT"')
            print('----------------------------------------')
            print(query)
            print('----------------------------------------')
            return pd.DataFrame

    def download_view(self, query, keep_result=True):
        return self.download_table(query, keep_result)

    def download_table_all(self, table, keep_result=True):
        query = 'select * from {}'.format(table)
        self.download_table(query, keep_result)

    def download_view_all(self, view, keep_result=True):
        query = 'select * from {}'.format(view)
        self.download_view(query, keep_result)

    def save_table(self, dst_bucket, dst_key):
        s3 = boto3.resource('s3')

        csv_buffer = StringIO()
        self.df_result.to_csv(csv_buffer)

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < self.timeout_in_sec:
            res = s3.Object(dst_bucket, dst_key).put(Body=csv_buffer.getvalue())

            if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                break
            else:
                time.sleep(self.wait_in_sec)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

        self.response_keys.append('/'.join([dst_bucket, dst_key]))
        return res

    def save_view(self, dst_bucket, dst_key):
        return self.save_table(dst_bucket, dst_key)
