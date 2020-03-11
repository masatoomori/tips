## Binning
左を閉区間としてビニングする。
ラベルは「未満」となるようにし、ソートしやすいようにカテゴリに番号をつける。
区間をの下限は実データの最小値に合わせる。
カテゴリを超える値にはカテゴリ上限値以上となるようにラベルを付ける。
```python
import pandas as pd

value_col = '<value>'
range_col = '<range>'

df = pd.DataFrame({value_col: [-1, 40, 20, 0, 1000, 203, 40, 30]})

bins = [df[value_col].min(), 0, 30, 100, 300, 500]
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
