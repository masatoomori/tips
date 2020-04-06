# Standard I/O
## print()
### 表示できない文字を無視する
```python
message = 'string with illegal characters'
print(message.encode('cp932', errors='ignore').decode('cp932'))
```
