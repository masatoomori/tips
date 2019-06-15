import subprocess
import os

NKF_PATH = 'path to nkf'
NKF_EXE = os.path.join(NKF_PATH, 'nkf32.exe')


def utf8_to_cp932(in_file, out_file):
    """

    :param in_file: cp932に変換したいutf8の元データファイル
    :param out_file: 元データファイルをcp932にエンコードした出力ファイル
    :return: 実行されればプロセス実行結果、失敗すればExceptionを返す
    """

    try:
        res = subprocess.run([NKF_EXE, in_file], stdout=subprocess.PIPE)
        with open(out_file, 'wb') as f:
            f.write(res.stdout)
    except Exception as e:
        return e

    return res


def test():
    utf8_file = 'test_utf8.txt'
    cp932_file = 'test_cp932.txt'

    res = utf8_to_cp932(utf8_file, cp932_file)

    print('{u} converted to {c}'.format(u=utf8_file, c=cp932_file))
    print(res)


if __name__ == '__main__':
    test()
