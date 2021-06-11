import json
import os

import requests
from simple_salesforce import Salesforce

CRED_PATHS = [os.curdir, os.path.join(os.pardir, 'cred')]
CRED_FILE = 'salesforce_api_cred.json'


def load_cred(cred_paths, cred_file, env) -> dict:
    for path in cred_paths:
        if os.path.exists(os.path.join(path, cred_file)):
            cred_file_full = os.path.join(path, cred_file)
            cred = json.load(open(cred_file_full, 'r'))
            if env in cred:
                print('profile: {e} found in {f}'.format(e=env, f=cred_file_full))
                return cred[env]
            else:
                print('{e} does not exist in {c}'.format(e=env, c=cred_file_full))
                return None

    print('{f} does not exist in any of {d}'.format(f=cred_file, d=cred_paths))
    return dict()


def connect_to_salesforce_instance(cred_paths=CRED_PATHS, cred_file=CRED_FILE, env='sandbox'):
    cred = load_cred(cred_paths, cred_file, env)
    data = {
        "grant_type": 'password',
        "client_id": cred['API_KEY'],
        "client_secret": cred['API_SECRET'],
        "username": cred['API_USER'],
        "password": cred['API_PWD'],
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(cred['ACCESS_TOKEN_URL'], data=data, headers=headers)
    response = response.json()
    if response.get('error'):
        raise Exception(response.get('error_description'))

    session = requests.Session()
    sf = Salesforce(instance_url=response['instance_url'],
                    session_id=response['access_token'],
                    session=session,
                    version=cred['VERSION'])

    return sf


def test():
    sf = connect_to_salesforce_instance()
    print(sf)


if __name__ == "__main__":
    test()
