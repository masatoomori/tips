# MySQL

## コマンドラインから実行して、結果をコマンドラインに返す

### 直接SQL文を書くパターン

```bash
mysql -h <host name> -P <port#> -u <username> -p<password> <database name> -e'
show tables;
'
```

### テキストにあるSQL文を実行するパターン

```bash
mysql -h <host name> -P <port#> -u <username> -p<password> <database name> < text.sql
```

## クエリを二次元配列に書き出す

```python
import pymysql

DB_SETTINGS = {
    'host': "",
    'database': "",
    'user': "",
    'password': "",
    'port': "",
    'charset': 'utf8mb4'
}

def download_records_from(table):
    conn = pymysql.connect(**DB_SETTINGS)
    cur = conn.cursor()

    cur.execute("SELECT * FROM {}".format(table))
    result = cur.fetchall()

    cols = [i[0] for i in cur.description]
    conn.close()

    return [cols] + list([list(r) for r in result])
```
