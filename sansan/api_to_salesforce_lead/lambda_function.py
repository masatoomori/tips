import urllib.parse
import boto3
import datetime
import re
import upload_biz_card_to_salesforce_lead as ss_lead

print('Loading function')

s3 = boto3.client('s3')
SANSAN_LEAD_AGENT = '<email address>'
COMPANY_DOMAINS = ['@<company domain for email>']
MIN_LEN_OF_VALID_EMAIL = 10
BACK_DAYS = 0               # さかのぼる登録日
DEFAULT_TAG_ID = '<SanSan Tag ID>'
TODAY = datetime.date.today()


def is_employee(email):
    for domain in COMPANY_DOMAINS:
        if email.endswith(domain):
            return True
    return False


def find_email(bodystr, a):
    """
    入力を改行して最初の[From / To]から始まる行を見つけ、メールアドレスを抽出する
    """
    lines = [l for l in bodystr.split('\r\n') if l.startswith(a)]

    if len(lines) > 0:
        words = [w for w in lines[0].split(' ') if '@' in w and len(w) > MIN_LEN_OF_VALID_EMAIL]
        if len(words) > 0:
            email = re.search(r'[A-Za-z0-9._@]+', words[0]).group(0)

            return email

    return ''


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    target_date = (datetime.datetime.now() - datetime.timedelta(days=BACK_DAYS)).date()

    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        print("CONTENT TYPE: " + response['ContentType'])

    except Exception as e:
        print(e)
        print('Object {} from bucket {}.'.format(file_name, bucket_name))
        raise e

    body = response['Body'].read()

    sender = find_email(body.decode('utf-8'), 'From')
    receiver = find_email(body.decode('utf-8'), 'To')

    print('sender: {}'.format(sender))
    print('receiver: {}'.format(receiver))

    if receiver == SANSAN_LEAD_AGENT:
        if is_employee(sender):
            print('run sansan biz card to salesforce lead')
            res = ss_lead.run(sender, target_date, DEFAULT_TAG_ID)
            print(res)
        else:
            print('run sansan biz card to salesforce lead')
            res = ss_lead.run(None, TODAY, DEFAULT_TAG_ID)
            print(res)

    return response['ContentType']
