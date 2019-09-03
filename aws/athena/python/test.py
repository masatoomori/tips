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

    view = athena.create_view(query)
    print(view)

    df = athena.download_view('select * from {}'.format(view), keep_result=False)

    print(df)

    athena.save_table(ATHENA_BUCKET, ATHENA_BUCKET_PREFIX + '/view_result.csv')


if __name__ == '__main__':
    main()
