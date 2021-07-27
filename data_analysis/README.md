# Data Analysis

## DataFrame

### オーバーフローした日時の修正

上限の日付の年だったらその年の1月1日に変更する

```python
import datetime
import pandas as pd


def fix_overflow_datetime(x):
    if x != x:
        return x
    if int(str(x)[:4]) >= pd.Timestamp.max.year:
        return datetime.datetime(year=pd.Timestamp.max.year, month=1, day=1)
    return x
```

### マルチカラムの解除

```python
import pandas as pd

df_data = pd.DataFrame({'index': ['a', 'b', 'c', 'a'],
                        'column': ['x', 'y', 'x', 'y'],
                        'value': [2, 3, 5, 6]})


df = df_data.groupby(['index', 'column']).sum().unstack()

# 最下レイヤの値のみを採用する場合
df.columns = df.columns.levels[1]


# 全レイヤをつなげる場合 1
def flatten_multi_columns(df_, *, to_snake_case=True, reverse_layer=False):
  new_col_items = df_.columns.values
  if to_snake_case:
    if reverse_layer:
      return ['_'.join(reversed(items)) for items in new_col_items]
    else:
      return ['_'.join(items) for items in new_col_items]
  else:
    if reverse_layer:
      return [''.join(reversed([item.capitalize() for item in items])) for items in new_col_items]
    else:
      return [''.join([item.capitalize() for item in items]) for items in new_col_items]


df.columns = flatten_multi_columns(df)

# 全レイヤをつなげる場合 2
df.columns = ["_".join(c) for c in df.columns.to_flat_index()]
```

## List

### 二次元リストの一次元化

sum()の第一引数に二次元リスト、第二引数に空リストを入れると一次元リストになる。
[参考](https://note.nkmk.me/python-list-flatten/)

```python
l_2d = [[0, 1], [2, 3]]
print(sum(l_2d, []))

# [0, 1, 2, 3]
```

## 数値分析

### Binning

左を閉区間としてビニングする。
ラベルは「未満」となるようにし、ソートしやすいようにカテゴリに番号をつける。
区間をの下限は実データの最小値に合わせる。
カテゴリを超える値にはカテゴリ上限値以上となるようにラベルを付ける。

```python
import pandas as pd

value_col = '<value>'
range_col = '<range>'
null_value = -1              # 欠測値に -1 を与える

df = pd.DataFrame({value_col: [-1, 40, 20, 0, 1000, 203, 40, 30]})
df[value_col] = pd.to_numeric(df[value_col])
df[value_col].fillna(null_value, inplace=True)

bins = sorted(list(set([df[value_col].min(), 0, 30, 100, 300, 500])))
labels = ['{i}: ~{b}'.format(i=i+1, b=b) for i, b in enumerate(bins[1:])]
df[range_col] = pd.cut(df[value_col], bins=bins, labels=labels, right=False).astype(str)
df[range_col] = df[range_col].apply(lambda x: x if x != 'nan' else '{i}: {b}+'.format(i=len(bins), b=bins[-1]))
```

実行結果

| # |\<value\>|\<range\>|
|---|---------|---------|
| 0 | 1       | 1: ~0   |
| 1 | 40      | 3: ~100 |
| 2 | 20      | 2: ~30  |
| 3 | 0       | 2: ~30  |
| 4 | 1000    | 6: 500+ |
| 5 | 203     | 4: ~300 |
| 6 | 40      | 3: ~100 |
| 7 | 30      | 3: ~100 |

## Web Access Log Analysis

[urllib](../web/urllib/README.md)

### 人間にやさしい表記

```python
def human_friendly_format(x, round_digit):
    """
    x (float)を人間が読みやすいように文字列にする。
    round_digitまで丸める。
    絶対値が1未満の値はそのまま返す
    """
    negative = -1 if x < 0 else 1
    abs_x = abs(x)
    if abs_x < 1:
        return x

    # 整数部分の桁数を取得する
    int_digit = len(re.split('\.', str(abs_x))[0])

    # 最高位が1の位になるように調整する
    abs_x_1 = abs_x / 10 ** (int_digit - 1)

    # 数値を丸める
    abs_x_1_round = round(abs_x_1, round_digit - 1)

    # 桁を元に戻す
    abs_x_round = abs_x_1_round * 10 ** (int_digit - 1)

    for d, n in {12: '兆', 8: '億', 4: '万'}.items():
        if int_digit > d:
            result = negative * abs_x_round / 10 ** d

            # 整数で表せる場合は整数にする
            result = int(result) if result == int(result) else result

            return '{x}{n}'.format(x=result, n=n)

    # 整数で表せる場合は整数にする
    abs_x_round = int(abs_x_round) if abs_x_round == int(abs_x_round) else abs_x_round

    return abs_x_round * negative
```
