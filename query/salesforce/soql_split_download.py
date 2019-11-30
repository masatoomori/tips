# -*- coding: utf-8 -*-
import datetime
import json
import pandas as pd
import numpy as np
import requests
from simple_salesforce import Salesforce

SF_CONF_FILE = '<json file>'
with open(SF_CONF_FILE, 'r') as F:
    SF_CONF = json.load(F)


def table_cols(sf, table, key='name'):
    if table == 'Account':
        return [f[key] for f in sf.Account.describe()['fields']]
    elif table == 'Activity__History':
        return [f[key] for f in sf.Activity__History.describe()['fields']]
    elif table == 'Lead':
        return [f[key] for f in sf.Lead.describe()['fields']]
    elif table == 'User':
        return [f[key] for f in sf.User.describe()['fields']]
    elif table == 'Opportunity':
        return [f[key] for f in sf.Opportunity.describe()['fields']]
    else:
        return None


def connect_to_salesforce_instance():
    access_token_url = SF_CONF["access_token_url"]
    data = {
        'grant_type': 'password',
        "client_id": SF_CONF["client_id"],
        "client_secret": SF_CONF["client_secret"],
        "username": SF_CONF["username"],
        "password": SF_CONF["password"],
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(access_token_url, data=data, headers=headers)
    response = response.json()
    if response.get('error'):
        raise Exception(response.get('error_description'))

    session = requests.Session()
    sf = Salesforce(instance_url=response['instance_url'],
                    session_id=response['access_token'],
                    sandbox=SF_CONF["sandbox"],
                    session=session)

    return sf


def download_opportunity_by_year(sf, cols, table, condition, account_ids):
    """
    アカウントについて全件ダウンロードできなかった場合、年ごとに分割してダウンロードを試みる
    :param sf: Salesforceへのコネクタ
    :param cols: ダウンロードする項目
    :param table: ダウンロード元オブジェクト
    :param condition: 年以外のダウンロード条件
    :param account_ids: ダウンロードする対象のアカウントID
    :return: DataFrame形式の商談リスト
    """
    soql = """
    SELECT
        MIN(CloseDate),
        MAX(CloseDate)
    FROM {t}
    WHERE {c}""".format(i=','.join(cols), t=table, c=condition)
    res = sf.query(soql)
    min_date = res['records'][0]['expr0']
    max_date = res['records'][0]['expr1']

    min_year = datetime.datetime.strptime(min_date, '%Y-%m-%d').year
    max_year = datetime.datetime.strptime(max_date, '%Y-%m-%d').year

    target_year = max_year
    df = pd.DataFrame()
    while target_year >= min_year:
        condition_year = ' and '.join([condition, 'CALENDAR_YEAR(CloseDate) = {}'.format(target_year)])
        soql = 'SELECT {i} FROM {t} WHERE {c}'.format(i=','.join(cols), t=table, c=condition_year)
        res = sf.query(soql)

        if res['done']:
            if res['totalSize'] > 0:
                df = pd.concat([df, pd.DataFrame(res['records'])], sort=False)
        else:
            if res['totalSize'] > 0:
                df_i = pd.DataFrame({'AccountId': account_ids})
                df_i['Id'] = 'Fail to Download in {}'.format(target_year)
                df = pd.concat([df, df_i], sort=False)
        target_year -= 1
    return df


def download_opportunity(sf, account_ids):
    table_name = 'Opportunity'
    cols = table_cols(sf, table_name)

    conditions = list()
    conditions.append("AccountId in ('{}')".format("', '".join(account_ids)))
    condition = ' and '.join(conditions)

    soql = 'SELECT {i} FROM {t} WHERE {c}'.format(i=','.join(cols), t=table_name, c=condition)
    res = sf.query(soql)

    if res['done']:
        if res['totalSize'] > 0:
            df = pd.DataFrame(res['records'])
            print('{n:,d} opportunities for {a}'.format(n=len(df), a=account_ids))
            return df.drop(['attributes'], axis=1)
        else:
            df = pd.DataFrame({'AccountId': account_ids})
            df['Id'] = 'No Opportunities for this Account'
            return df
    else:
        print('retry to download opportunities for {a}: total size = {t}'.format(a=account_ids, t=res['totalSize']))

        # 失敗した場合、アカウントのサイズを半分にして再挑戦する
        if res['totalSize'] > 0:
            if len(account_ids) > 1:
                account_id_groups = np.array_split(account_ids, 2)
                df = pd.DataFrame()
                for account_id_group in account_id_groups:
                    df_i = download_opportunity(sf, account_id_group)
                    df = pd.concat([df, df_i], sort=False)
                return df
            else:
                print('failed to download opportunities for {a}. try to download by year'.format(a=account_ids))
                df = download_opportunity_by_year(sf, cols, table_name, condition, account_ids)

                return df
        else:
            df = pd.DataFrame({'AccountId': account_ids})
            df['Id'] = 'No Opportunities for this Account'
            return df


def lambda_handler(event, context):
    account_ids = []
    df = download_opportunity(sf, account_ids)

    print(df)


def test():
    event = {}
    context = {}

    lambda_handler(event, context)


if __name__ == '__main__':
    test()
