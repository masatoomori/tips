# 正規表現

## ISOフォーマットの日付を含む文字列から日付を取り出す

```python
import re

str_with_iso_format_date = 'xxxx_2019-03-21.csv'
m = re.search(r'(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})', str_with_iso_format_date)
print(str_with_iso_format_date, m.group('year'))
print(str_with_iso_format_date, m.group('month'))
print(str_with_iso_format_date, m.group('day'))
```

## 数値を抜き出す

```python
NUM_PATTERN = r'([+-]?[0-9]+\.?[0-9]*)'
n = ''.join(re.findall(NUM_PATTERN, str(s)))
```

## 改行、タブを削除しtsv形式で保存できるようにする

```python
def strip(x):
    x = str(x).replace('\n', '').replace('\r', '').replace('\t', ' ')

    return x
```

## 改行などの特殊文字を除く

```python
new_string = '_'.join(re.findall(r"[0-9a-zA-Zあ-んア-ン一-鿐]+", old_string))
```

## クオートで囲まれた文字列を抜き出す

```python
m = re.findall(r"'(.+)'", string)
```
