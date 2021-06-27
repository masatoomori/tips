# I/O

## python

### Standard I/O

#### print()

##### 表示できない文字を無視する

```python
message = 'string with illegal characters'
print(message.encode('cp932', errors='ignore').decode('cp932'))
```

### Path

#### Path をディレクトリごとに分解してリストにする

```python
def parse_path(path):
    path_items = list()
    while True:
        path, item = os.path.split(path)

        if item:
            path_items.append(item)
        elif path:
            path_items.append(path)
            break

    path_items.reverse()
    return path_items
```

## Console

### terminal on Mac

#### less

##### utf-8 の csv ファイルを表示させる

```shell script
column -t -s"," sample.csv | less -#20 -N -S
```

\#20 は ESC の後に ¥( や ¥) を押すことでスクロールする横幅

下記のようにショートカットを用意すると便利

```shell script
alias csvv='column -t -s"," | less -#20 -N -S'
cat test.csv | csvv
```
