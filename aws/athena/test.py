from Athena import SingleResult


DATABASE_REGION = '<aws region>'
DATABASE_NAME = '<database name in glue>'
ATHENA_BUCKET = '<bucket to store athena result / log>'
ATHENA_BUCKET_PREFIX = 'prefix to store athena result / log'


def load_query(f):
    lines = open(f).readlines()

    query = ''.join(lines)

    return query


def main():
    query = load_query('test.sql')

    print(query)

    athena = SingleResult(DATABASE_REGION, DATABASE_NAME, ATHENA_BUCKET, ATHENA_BUCKET_PREFIX)
    athena.create_view(query)

    df = athena.download_view('select * from test_view', keep_result=False)

    print(df)

    athena.save_result(ATHENA_BUCKET, ATHENA_BUCKET_PREFIX + '/view_result.csv')


if __name__ == '__main__':
    main()
