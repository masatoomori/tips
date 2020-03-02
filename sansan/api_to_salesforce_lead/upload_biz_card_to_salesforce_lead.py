import json
import os
import datetime
import re
import argparse
# Lambda用のnumpy, pandas, simple-salesforce, requestsを同一ディレクトリに置く
# numpy, pandasはgit clone https://github.com/pbegle/aws-lambda-py3.6-pandas-numpy.gitで入手
# それ以外はpip install [package] -t .で入手
import pandas as pd
import simple_salesforce as ss
import requests

SF_CONF_FILE = os.path.join(os.curdir, 'salesforce_conf.json')
SANSAN_CONF_FILE = os.path.join(os.curdir, 'sansan_conf.json')
API_ENDPOINT = 'https://api.sansan.com/v1.2/'
LEAD_SOURCE = ''
DEFAULT_TAG_ID = '<SanSan Tag ID>'

PREFECTURE = {
    '北海道': 'Hokkaido', '青森県': 'Aomori', '岩手県': 'Iwate', '宮城県': 'Miyagi', '秋田県': 'Akita',
    '山形県': 'Yamagata', '福島県': 'Fukushima', '茨城県': 'Ibaraki', '栃木県': 'Tochigi', '群馬県': 'Gumma',
    '埼玉県': 'Saitama', '千葉県': 'Chiba', '東京都': 'Tokyo', '神奈川県': 'Kanagawa', '新潟県': 'Niigata',
    '富山県': 'Toyama', '石川県': 'Ishikawa', '福井県': 'Fukui', '山梨県': 'Yamanashi', '長野県': 'Nagano',
    '岐阜県': 'Gifu', '静岡県': 'Shizuoka', '愛知県': 'Aichi', '三重県': 'Mie', '滋賀県': 'Shiga', '京都府': 'Kyoto',
    '大阪府': 'Osaka', '兵庫県': 'Hyogo', '奈良県': 'Nara', '和歌山県': 'Wakayama', '鳥取県': 'Tottori',
    '島根県': 'Shimane', '岡山県': 'Okayama', '広島県': 'Hiroshima', '山口県': 'Yamaguchi', '徳島県': 'Tokushima',
    '香川県': 'Kagawa', '愛媛県': 'Ehime', '高知県': 'Kochi', '福岡県': 'Fukuoka', '佐賀県': 'Saga',
    '長崎県': 'Nagasaki', '熊本県': 'Kumamoto', '大分県': 'Oita', '宮崎県': 'Miyazaki', '鹿児島県': 'Kagoshima',
    '沖縄県': 'Okinawa',
}


def get_api_call(path, param):
    header = {'X-Sansan-Api-Key': json.loads(open(SANSAN_CONF_FILE).read())['API_KEY']}
    request_data = requests.get(
        API_ENDPOINT + path,
        params=param,
        headers=header
    )
    return request_data.json()


def get_owner_id(sf, emails):
    """
    メールに該当するSalesforceのユーザIDを得る。
    :param sf: Salesforceのハンドラ
    :param emails: 検索するメールのリスト
    :return: メールのリストで1つでも該当すればそのうちで1つの任意のIDを返す
    """
    soql = """
        SELECT
            Id, Email
        FROM
            User
        WHERE
            Email in ('{}')
    """.format("', '".join(emails))

    result = sf.query(soql)
    df = pd.DataFrame(result['records'])

    return df['Id'].tolist()[0]


def capitalize_email(email):
    """
    emailをすべて小文字にしたものとドメイン以前の先頭とピリオド直後を大文字にしたものを返す
    :param email: 元のメールアドレス
    :return: 2つのメールアドレスのリスト
    """

    lower_case = email.lower()
    name, domain = re.split('@', email)
    items = re.split('\.', name)
    for i, item in enumerate(items):
        if len(item) > 0:
            items[i] = item[0].upper() + item[1:]
    camel_case = '.'.join(items) + '@' + domain

    return [lower_case, camel_case]


def download_biz_card_by_tag(user_email, target_date, tag_id):
    target_range = 'all'
    path = 'bizCards/search'
    min_registered_date = target_date
    has_more = True
    offset = 0
    df = pd.DataFrame()

    while has_more:
        param = {
            "range": target_range,
            "tagId": tag_id,
            "entryStatus": "completed",
            "offset": offset
        }
        result = get_api_call(path, param)
        result_data = result['data']

        for i, d in enumerate(result_data):
            if d['owner']['email'] is None:
                print('{i}: owner email is None'.format(i=i+offset))
                continue

            df_i = pd.DataFrame({
                'id': [d['id']],
                'companyId': [d['companyId']],
                'personId': [d['personId']],
                'LastName': [d['lastName']],
                'FirstName': [d['firstName']],

                'Company': [d['companyName']],
                'Department__c': [d['departmentName']],
                'Title': [d['title']],

                'Phone': [d['tel']],
                'MobilePhone': [d['mobile']],
                'Fax': [d['fax']],
                'Email': [d['email']],
                'Website': [d['url']],

                'PostalCode': [d['postalCode']],
                'prefecture': [d['prefecture']],
                'City': [d['city']],
                'street': [d['street']],
                'building': [d['building']],

                'Description': [d['id']],
                'Note_Placeholder__c': [d['personId']],
                'Status_Comments__c': [d['companyId']],
                
                'registeredTime': [d['registeredTime']],
                'owner_email': [d['owner']['email']],
            })

            # 都道府県を英語に直す
            df_i['prefecture'] = df_i['prefecture'].apply(lambda x: PREFECTURE[x] if x in PREFECTURE.keys() else '')

            df_i['registeredTime'] = pd.to_datetime(df_i['registeredTime'])
            df_i['registeredDate'] = df_i['registeredTime'].apply(lambda x: x.date())
            min_registered_date = df_i['registeredDate'].min()

            # 対象日以前のデータを取り除く
            df_i = df_i[df_i['registeredDate'] >= target_date].copy()

            # 対象ユーザ以外のデータを取り除く
            if user_email is not None and not df_i.empty:
                df_i = df_i[df_i['owner_email'].apply(lambda x: x.upper() == user_email.upper())].copy()

            # Emailが空欄のレコードを除く
            if not df_i.empty:
                if len(df_i[df_i['Email'].isnull()]) > 0:
                    print('Record(s) below without email(s) will not be uploaded')
                    print(df_i[df_i['Email'].isnull()])

                df_i = df_i[df_i['Email'].notnull()]

            if not df_i.empty:
                df = pd.concat([df, df_i])

        # もしdf_iの中に対象日以前のデータが含まれていた場合、それ以降はすべてそれより古いはずなのでループを抜ける
        if min_registered_date < target_date:
            break

        offset += len(result_data)
        has_more = result['hasMore']

    if len(df) == 0:
        return df

    for c in ['prefecture', 'street', 'building']:
        df[c].fillna('', inplace=True)
    df['Street'] = df.apply(lambda row: ' '.join([row['street'], row['building']]), axis=1)
    df.drop(['street', 'building'], axis=1, inplace=True)

    return df.reset_index(drop=True)


def upload_biz_card(records):
    def get_lead(s, key, value):
        cols = ['Id', 'Email', 'Owner_Full_Name__c', 'OwnerId', 'CreatedDate', 'IsDeleted']
        try:
            soql = """
                SELECT
                    {c}
                FROM
                    Lead
                WHERE
                    {k} = '{v}'
                    AND IsDeleted = False
            """.format(c=','.join(cols), k=key, v=value)
            result = s.query(soql)
            df_l = pd.DataFrame(result['records'])
            return df_l[cols]

        except Exception as e:
            print(e)
            return pd.DataFrame()

    sf_conf = {
        "client_id": json.loads(open(SF_CONF_FILE).read())["client_id"],
        "client_secret": json.loads(open(SF_CONF_FILE).read())["client_secret"],
        "username": json.loads(open(SF_CONF_FILE).read())["username"],
        "password": json.loads(open(SF_CONF_FILE).read())["password"],
        "sandbox": False,
        "access_token_url": "https://login.salesforce.com/services/oauth2/token",
        "access_token_url_sandbox": "https://test.salesforce.com/services/oauth2/token"
    }

    access_token_url = sf_conf["access_token_url"]
    data = {
        'grant_type': 'password',
        'client_id': sf_conf["client_id"],
        'client_secret': sf_conf["client_secret"],
        'username': sf_conf["username"],
        'password': sf_conf["password"]
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(access_token_url, data=data, headers=headers)
    response = response.json()
    if response.get('error'):
        raise Exception(response.get('error_description'))

    session = requests.Session()
    sf = ss.Salesforce(instance_url=response['instance_url'],
                       session_id=response['access_token'],
                       sandbox=sf_conf['sandbox'],
                       session=session)

    df_lead = pd.DataFrame()

    for record in records:
        owner_emails = list()

        owner_id = get_owner_id(sf, owner_emails)

        param = {
            'LastName': record['LastName'],
            'FirstName': record['FirstName'],
            'Company': record['Company'],
            'Department__c': record['Department__c'],
            'Title': record['Title'],

            'Phone': record['Phone'],
            'MobilePhone': record['MobilePhone'],
            'Fax': record['Fax'],
            'Email': record['Email'],
            'Website': record['Website'],

            'Country': 'Japan',
            'PostalCode': record['PostalCode'],
            'State': record['prefecture'],  # 都道府県名まで英語（空欄も可）で入れればそれ以降の住所は自由（空欄も可）
            'City': record['City'],
            'Street': record['Street'],

            'Status': 'Open',
            'LeadSource': LEAD_SOURCE,
            'Description': record['Description'],
            'Note_Placeholder__c': record['Note_Placeholder__c'],
            'Status_Comments__c': record['Status_Comments__c'],

            'OwnerId': owner_id
        }

        # リード登録がない場合（メールアドレスで判定）、paramで登録し、データを出力
        # 対象ユーザのIDでリードにすでに登録されている場合（メールアドレスで判定）、旧データを出力
        # 対象ユーザ以外のIDでリードにすでに登録されている場合、paramで登録し、旧データも出力
        df_old = get_lead(sf, 'Email', record['Email'])
        if len(df_old) == 0:
            print('create new lead for {}'.format(record['Email']))
            sf.Lead.create(param)
            df = get_lead(sf, 'Email', record['Email'])
            df_lead = pd.concat([df_lead, df])
        else:
            if len(df_old[df_old['OwnerId'] == owner_id]) > 0:
                print('lead for {t} was created by {o}'.format(t=record['Email'], o=record['owner_email']))
            else:
                print('create new lead for {} though created by others'.format(record['Email']))
                sf.Lead.create(param)
                df = get_lead(sf, 'Email', record['Email'])
                df_lead = pd.concat([df_lead, df])

        df_lead = pd.concat([df_lead, df_old])

    return df_lead


def run(user_email, target_date, tag_id):
    df = download_biz_card_by_tag(user_email, target_date, tag_id)

    if len(df) == 0:
        print('{e} has no records at {t}'.format(e=user_email, t=datetime.datetime.now()))
        return pd.DataFrame()
    else:
        df_lead = upload_biz_card(df.to_dict(orient='records'))
        return df_lead


def main():
    parser = argparse.ArgumentParser(
        prog='upload_biz_card_to_salesforce_lead.py',
        description='create Saleforce lead from biz card in SanSan registered on the day',
        add_help=True
    )
    parser.add_argument('-o', '--owner',
                        help='email address of biz card owner',
                        required=True)
    parser.add_argument('-t', '--tag_id',
                        help='tag ID in SanSan for download filter',
                        default=DEFAULT_TAG_ID)
    parser.add_argument('-d', '--target_date',
                        help='scan biz card registered on that date or later',
                        default=datetime.date.today().isoformat())
    args = parser.parse_args()

    user_email = args.owner
    tag_id = args.tag_id
    tdatetime = datetime.datetime.strptime(args.target_date, '%Y-%m-%d')
    target_date = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day)

    df_res = run(user_email, target_date, tag_id)

    print(df_res)


if __name__ == '__main__':
    main()
