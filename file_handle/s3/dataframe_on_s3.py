import pandas as pd
import s3fs

# S3へのアクセス
CREDENTIAL_FILE = 'credentials.csv'
USER_NAME = 'AWS -> IAM -> Userで作成したユーザ名'
CRED = pd.read_csv(CREDENTIAL_FILE, encoding='cp932', dtype=object, index_col='User name').to_dict()
S3_KEY = CRED['Access key ID'][USER_NAME]
S3_SECRET = CRED['Secret access key'][USER_NAME]

REPOSITORY_PATH = '<file path in S3>'
FILE_NAME = '<file name>'


def write_df_to_s3(df, s3_path):
    bytes_to_write = df.to_csv(None, index=False).encode()
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    with fs.open(s3_path, 'wb') as f:
        f.write(bytes_to_write)


def read_df_from_s3(s3_path, encoding='utf8', dtype=object):
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    with fs.open(s3_path) as f:
        df = pd.read_csv(f, encoding=encoding, dtype=dtype)
        return df


def test():
    data = pd.DataFrame()
    s3_path = '/'.join(['s3:/', REPOSITORY_PATH, FILE_NAME])
    write_df_to_s3(data, s3_path)


if __name__ == '__main__':
    test()
