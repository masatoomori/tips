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
