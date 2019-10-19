import os
from hashids import Hashids
import pandas as pd


def read_jp_name_csv(f, encoding='utf8', dtype=object, delimiter=','):
    # read_csvは日本語ファイルを読めないので英数字にHash関数で変換する
    hashed_file = Hashids(salt=f, min_length=8).encode(0)

    os.rename(f, hashed_file)
    df = pd.read_csv(hashed_file, encoding=encoding, dtype=dtype, delimiter=delimiter)
    os.rename(hashed_file, f)

    return df


def save_jp_name_csv(df, f, encoding='utf8', index=False, sep=','):
    # read_csvは日本語ファイルを読めないので英数字にHash関数で変換する
    hashed_file = Hashids(salt=f, min_length=8).encode(0)

    df.to_csv(hashed_file, encoding=encoding, index=index, sep=sep)

    if os.path.exists(f):
        os.remove(f)
    os.rename(hashed_file, f)
