## 日付
### created_iso_dateが本日より１ヵ月以内
```sql
created_iso_date > CURRENT_DATE - interval '1' month
```

## 文字列
### 連結
```sql
string1 || string2
```

### 大文字小文字
```sql
UPPER(string1)
LOWER(string2)
```
