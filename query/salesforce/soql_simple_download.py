# -*- coding: utf-8 -*-
import datetime
import json
import numpy as np
import pandas as pd
import requests
from simple_salesforce import Salesforce

SF_CONF_FILE = '<json file>'
with open(SF_CONF_FILE, 'r') as F:
    SF_CONF = json.load(F)


def table_cols(sf, table, key='name'):
    if table == 'Account':
        return [f[key] for f in sf.Account.describe()['fields']]
    elif table == 'AccountHistory':
        return [f[key] for f in sf.AccountHistory.describe()['fields']]
    elif table == 'AccountContactRelation':
        return [f[key] for f in sf.AccountContactRelation.describe()['fields']]
    elif table == 'ChatterActivity':
        return [f[key] for f in sf.ChatterActivity.describe()['fields']]
    elif table == 'CollaborationGroupFeed':
        return [f[key] for f in sf.CollaborationGroupFeed.describe()['fields']]
    elif table == 'CollaborationGroupMember':
        return [f[key] for f in sf.CollaborationGroupMember.describe()['fields']]
    elif table == 'Contact':
        return [f[key] for f in sf.Contact.describe()['fields']]
    elif table == 'EntitySubscription':
        return [f[key] for f in sf.EntitySubscription.describe()['fields']]
    elif table == 'GroupMember':
        return [f[key] for f in sf.GroupMember.describe()['fields']]
    elif table == 'Lead':
        return [f[key] for f in sf.Lead.describe()['fields']]
    elif table == 'LeadFeed':
        return [f[key] for f in sf.LeadFeed.describe()['fields']]
    elif table == 'Task':
        return [f[key] for f in sf.Task.describe()['fields']]
    elif table == 'User':
        return [f[key] for f in sf.User.describe()['fields']]
    elif table == 'UserFeed':
        return [f[key] for f in sf.UserFeed.describe()['fields']]
    elif table == 'UserRole':
        return [f[key] for f in sf.UserRole.describe()['fields']]
    elif table == 'Opportunity':
        return [f[key] for f in sf.Opportunity.describe()['fields']]
    elif table == 'OpportunityContactRole':
        return [f[key] for f in sf.OpportunityContactRole.describe()['fields']]
    elif table == 'OpportunityFieldHistory':
        return [f[key] for f in sf.OpportunityFieldHistory.describe()['fields']]
    elif table == 'OpportunityHistory':
        return [f[key] for f in sf.OpportunityHistory.describe()['fields']]
    elif table == 'OpportunityPartner':
        return [f[key] for f in sf.OpportunityPartner.describe()['fields']]
    elif table == 'OpportunityTag':
        return [f[key] for f in sf.OpportunityTag.describe()['fields']]
    elif table == 'OpportunityTeamMember':
        return [f[key] for f in sf.OpportunityTeamMember.describe()['fields']]
    elif table == 'Private_Tag_with_Opportunity__Tag':
        return [f[key] for f in sf.Private_Tag_with_Opportunity__Tag.describe()['fields']]
    elif table == 'RecordType':
        return [f[key] for f in sf.RecordType.describe()['fields']]
    elif table == 'RecordTypeLocalization':
        return [f[key] for f in sf.RecordTypeLocalization.describe()['fields']]
    else:
        return []


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


def download_as_dataframe(object_name, conditions, cols, split=1):
    sf = connect_to_salesforce_instance()

    if not cols:
        cols = table_cols(sf, object_name)

    arr_col_groups = np.array_split(cols, split)

    df = pd.DataFrame(columns=['Id'])
    for arr_cols in arr_col_groups:
        # オブジェクトにはIdカラムが必ずあるので、それをキーにJoinするために追加
        cols = arr_cols.tolist()
        if 'Id' not in cols:
            cols = ['Id'] + cols

        soql = 'SELECT {i} FROM {t}'.format(i=','.join(cols), t=object_name)
        if conditions:
            condition = ' and '.join(conditions)
            soql += ' WHERE {c}'.format(c=condition)
        res = sf.query_all(soql)

        if res['done']:
            df_i = pd.DataFrame(res['records'])

            if not df_i.empty:
                df = pd.merge(df, df_i.drop(['attributes'], axis=1), how='outer', on=['Id'])
                del df_i

        else:
            print('fail to download with {}'.format(soql))

    del sf

    return df


def test():
    download_conditions = {         # ダウンロードするレコードの条件。WHERE句。空リストの場合は条件なし
        'Account': [
            "BillingCountry = 'Japan'"
        ],
    }
    download_cols = {               # ダウンロードする項目。空リストの場合はすべてダウンロード
        'Account': list(),
    }
    splits = {                      # ダウンロード時に項目を分割する個数（使用メモリ削減のため）。1以上の整数をとる
        'Account': 1,
    }

    for object_name, conditions in download_conditions.items():
        print('Object Name: {}'.format(object_name))

        start_dt = datetime.datetime.now()
        print('start time: {}'.format(start_dt))

        # メインの関数。対象オブジェクトとダウンロード条件を引数とする
        df = download_as_dataframe(object_name, conditions, download_cols[object_name], splits[object_name])

        end_dt = datetime.datetime.now()
        duration = (end_dt - start_dt).seconds
        print('end time: {}'.format(end_dt))
        print('duration: {:.2f} sec'.format(duration))
        print()

        if not df.empty:
            print(df.describe())
            print(df.info())


if __name__ == '__main__':
    test()
