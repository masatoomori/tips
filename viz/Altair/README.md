# Altair 備忘録

## 環境設定

### インストール

```shell
$ pip install -U altair vega_datasets notebook vega
```

## 描写設定

### 初期設定

```python
import altair as alt

# for the notebook only (not for JupyterLab) run this command once per session
alt.renderers.enable('notebook')

# Optional in JupyterLab: requires an up-to-date vega labextension.
alt.renderers.enable('mimetype')

# 上限エラー無効化
alt.data_transformers.enable('default', max_rows=None)

# カラーセットの選択
COLOR1 = ['#006a4d', '#69be2b', '#00b2dd', '#ec008c', '#a23f97', '#ffdd00', '#f58220', '#004b35', '#00a657', '#bfd857']
COLOR2 = ['#bfd857', '#00a657', '#004b35']

scale_color_cud = alt.Scale(range=COLOR1)
# color=alt.Color('<hue>:N', scale=scale_color_cud)
```

### Configure

#### .configure_view

[Altair Docs](https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html#altair.Chart.configure_view)

```python
stroke='transparent'        # 境界線の色
strokeWidth=0               # 境界線の幅
```

## Charts

### Bar

```python
import altair as alt
import pandas as pd

df_orig = pd.DataFrame()
x_axis = {'name': '<column name>', 'type': 'Q'}         # 時系列の場合は 'type': 'T'、カテゴリの場合は 'type': 'N'
y_axis = {'name': '<column name>', 'type': 'Q', 'op': 'sum'}
hue = {'name': '<column name>', 'type': 'N', 'sort_col': '<column name>', 'sort_ascending': False}

df_ = df_orig[[x_axis['name'], y_axis['name'], hue['name']]].copy()

y_ = y_axis['name']
if 'op' in y_axis:
    y_ = y_axis['op'] + '(' + y_ + ')'

hue_sort_list = df_orig[[hue['name'], hue['sort_col']]].groupby(hue['name']).count().sort_values(by=hue['sort_col'], ascending=hue['sort_ascending']).index.tolist()
    
chart = alt.Chart(df_).mark_bar().encode(
    x=alt.X('{n}:{t}'.format(n=hue['name'], t=hue['type']),
            sort=alt.EncodingSortField(field=y_axis['name'], op="sum", order='descending')),
    y=alt.Y(y_),
    color=alt.Color('{n}:{t}'.format(n=hue['name'], t=hue['type'])),
)
```

### Stacked Bar

```python
import altair as alt
import pandas as pd

df = pd.DataFrame()
hue_col = '<hue col>'
hue_sorted_list = ['list to sort hue']

sorted_x_axis_list = ['items for x axis']
total_for_x_axis = '<total col name for x axis>'

# 積み上げの順序を指定したい場合
temp_col_for_sort = str(hash('{}'.format(''.join(df.columns))))     # 何でもいいので他と被らないテンポラリのカラムを作る
df[temp_col_for_sort] = df[hue_col].apply(lambda x: hue_sorted_list.index(x))

# 横軸に全体を付けたしたい場合（normalize のときのみ推奨）
if sorted_x_axis_list:
    sorted_x_axis_list = [total_for_x_axis] + sorted_x_axis_list
else:
    sorted_x_axis_list = alt.EncodingSortField(field='<y axis>', op="sum", order='descending')

bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('<x axis>:N', sort=sorted_x_axis_list),
    y=alt.Y('<y axis>:Q', axis=alt.Axis(format='%'), stack='normalize'),
    color=alt.Color('{}:N'.format(hue_col), scale=scale_color_cud, sort=hue_sorted_list),
    order='{}'.format(temp_col_for_sort)
)

df.drop([temp_col_for_sort], axis=1, inplace=True)
```

### Histogram

```python
import altair as alt
import pandas as pd

df = pd.DataFrame()
x_axis = {'name': '<column name>', 'type': 'Q'}         # 時系列の場合は 'type': 'T'、カテゴリの場合は 'type': 'N'
y_axis = {'name': 'count()', 'type': 'Q'}
hue = {'name': '<column name>', 'type': 'N'}
bin_min = float
bin_max = float
bin_step = float

df_ = df[[x_axis['name'], hue['name']]].copy()

hist = alt.Chart(df_).mark_bar().encode(
    x=alt.X('{n}:{t}'.format(n=x_axis['name'], t=x_axis['type']), bin=alt.Bin(extent=[bin_min, bin_max], step=bin_step)),
    y=alt.Y('{n}:{t}'.format(n=y_axis['name'], t=y_axis['type'])),
    color=alt.Color('{n}:{t}'.format(n=hue['name'], t=hue['type']))
)
```

### Bubble Chart

```python
import altair as alt
import pandas as pd

x_axis = {'name': '<column name>', 'type': 'Q'}         # 時系列の場合は 'type': 'T'、カテゴリの場合は 'type': 'N'
y_axis = {'name': '<column name>', 'type': 'Q'}
color = {'name': '<column name>', 'type': 'N'}

df = pd.DataFrame()
bubble = alt.Chart(df).mark_point().encode(
    x=alt.X('{n}:{t}'.format(n=x_axis['name'], t=x_axis['type']), axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title=x_axis['name'], labelAngle=0)),
    y=alt.Y('{n}:{t}'.format(n=y_axis['name'], t=y_axis['type']), axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title=y_axis['name'], labelAngle=0)),
    size=alt.Size('sum(<value for size>):Q', scale=alt.Scale()),
    color=alt.Color('<hue>:N', legend=None, scale=scale_color_cud, sort=['<sort list>']),
    tooltip=['<column name>', ...]
)
```

### Scatter Chart

```python

import altair as alt
import pandas as pd

x_axis = {'name': '<column name>', 'type': 'Q'}         # 時系列の場合は 'type': 'T'、カテゴリの場合は 'type': 'N'
y_axis = {'name': '<column name>', 'type': 'Q'}
color = {'name': '<column name>', 'type': 'N'}
other_cols_on_tooltip = '<list of columns to show as tooltip>'

df = pd.DataFrame()
df_ = df[[x_axis['name'], y_axis['name'], color['name']] + other_cols_on_tooltip].copy()

point = alt.Chart(df).mark_circle(size=20).encode(
    x=alt.X('{n}:{t}'.format(n=x_axis['name'], t=x_axis['type']), axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title=x_axis['name'], labelAngle=0)),
    y=alt.Y('{n}:{t}'.format(n=y_axis['name'], t=y_axis['type']), axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title=y_axis['name'], labelAngle=0)),
    color=alt.Color('{n}:{t}'.format(n=color['name'], t=color['type'])),
    tooltip=other_cols_on_tooltip + [[x_axis['name'], y_axis['name'], color['name']]
)
```

### Boxplot

```python
import altair as alt
import pandas as pd

df = pd.DataFrame()

boxplot = alt.Chart(df).mark_boxplot(ticks=alt.MarkConfig(color='black'), median=alt.MarkConfig(color='black')).encode(
    x=alt.X('<x axis>:N', axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title='<x axis name>', labelAngle=0)),
    y=alt.Y('mean(<y axis>):Q', axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title='<y axis name>', labelAngle=0)),
    # column=alt.Column('<col split>', sort=<list for col order>, header=alt.Header(labelFontSize=11, labelAngle=0, titleFontSize=11)),
    # row=alt.Row('<row split>', sort=<list for row order>, header=alt.Header(labelFontSize=11, labelAngle=-90, titleFontSize=11)),
    color=alt.Color('<hue>:N', legend=None, scale=scale_color_cud)
)
```

### Rect

```python
import altair as alt
import pandas as pd

df = pd.DataFrame()

rect = alt.Chart(df).mark_rect().encode(
    x=alt.X('<x axis>:N', axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title='<x axis name>', labelAngle=0)),
    y=alt.Y('<y axis>:N', axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title='<y axis name>', labelAngle=0)),
    color=alt.Color('count()', scale=alt.Scale(range=scale_color_cud))
)
```

### Marimekko

[Creating Marimekko chart](https://github.com/altair-viz/altair/issues/1632)

```python
import altair as alt
import pandas as pd


df = pd.DataFrame({
    'year': [2017, 2018, 2019],
    'year_weight': [340, 170, 520],
    'food': [12, 16, 17],
    'medicine': [15, 22, 17],
    'rent': [14, 35, 10],
    'other': [13, 15, 23]
})

alt.Chart(df).transform_stack(
    stack='year_weight',
    as_=['x1', 'x2'],
    groupby=[],
).transform_fold(
    ['food', 'medicine', 'rent', 'other'],
    as_=['category', 'category_weight'],
).transform_stack(
    stack='category_weight',
    groupby=['year'],
    offset='normalize',
    as_=['y1', 'y2'],
).mark_rect(strokeWidth=0.3).encode(
    x=alt.X('x1:Q', title='Yearly expenses'), 
    x2='x2:Q',
    y=alt.Y('y1:Q',title='Expense item share'), 
    y2='y2:Q',
    fill='category:N',
    tooltip=['year:N', 'category:N'],
    stroke=alt.value('black'),
).configure_axis( grid=False )
```

## 集計

[Doc](https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html?highlight=transform_fold#altair.Chart.transform_fold)

横長のテーブルを縦長にしてからチャートにする

```python
import altair as alt
import pandas as pd

df = pd.DataFrame()

rect = alt.Chart(df).transform_fold(
    ['<縦に結合するカラムのリスト>'],
    as_=['<上記カラム名を入れておく変数名>', '<上記カラムの値を格納する変数名>']
).mark_rect().encode(
    x=alt.X('<x axis>:N', axis=alt.Axis(labelFontSize=11, ticks=True, titleFontSize=11, title='<x axis name>', labelAngle=0)),
    y=alt.Y('{}:N'.format('<上記カラム名を入れておく変数名>')),
    color=alt.Color('sum(<上記カラムの値を格納する変数名>):Q', scale=alt.Scale(range=scale_color_cud))
)
```

## データの連動

```python
import altair as alt
from vega_datasets import data

cars = data.cars()

brush = alt.selection_interval()

points = alt.Chart(cars).mark_point().encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    color=alt.condition(brush, 'Origin:N', alt.value('lightgray'))
).add_selection(
    brush
)

bars = alt.Chart(cars).mark_bar().encode(
    y='Origin:N',
    color='Origin:N',
    x='count(Origin):Q'
).transform_filter(
    brush
)

points & bars
```

## 描写

```python
chart.properties(height=400, width=400).interactive()
```

## Useful Links

[Bar Chart Examples](https://colab.research.google.com/github/altair-viz/altair_notebooks/blob/master/notebooks/04-BarCharts.ipynb)