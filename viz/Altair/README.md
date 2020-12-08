# Charts

## Marimekko

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