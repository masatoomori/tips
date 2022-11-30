# Viz with DataFrame

## レジェンド

### 外に出す

```python
ax = df.plot()
ax.legend(bbox_to_anchor=(1.0, 1.0))
ax.plot()
```

### フォントサイズを変更する

```python
ax = df.plot()
ax.legend(fontsize=18)
ax.plot()
```
