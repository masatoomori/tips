# Tips for Web Access Log Analysis

```python
import urllib

def parse_params(df):
    # URLからパラメータを取り出し、Dictに変換する
    df['params'] = df['ga_pagePath'].fillna('').apply(lambda x: dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(x).query)))

    # 興味のあるパラ―メタを抜き出す
    for p in ['<param A>', '<baram B>', ...]:
        df['param_{}'.format(p)] = df['params'].apply(lambda x: x[p] if p in x else None)

    return df
```
