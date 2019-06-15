utf8をcp932に書き換える
# Windowsのアプリケーションを使って書き換える方法
## 環境
- Windows 7
- Python 3.6以降

## 準備
Pythonスクリプトと同じ場所に[nkf32.exe](https://www.vector.co.jp/soft/dl/win95/util/se295331.html)を置く

## サンプルスクリプト
```python
import subprocess

UTF8_FILE = "cp932に変換したいutf8の元データファイル"
CP932_FILE = "元データファイルをcp932にエンコードした出力ファイル"

res = subprocess.run(['nkf32.exe', UTF8_FILE], stdout=subprocess.PIPE)
with open(CP932_FILE, 'wb') as f:
    f.write(res.stdout)
```
