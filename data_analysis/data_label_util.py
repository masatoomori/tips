import re

import pandas as pd


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


def bin_col(s_values, bin_range, null_value=-1, unit_name='', human_friendly=False, round_digit=1, lang='en'):
    """DataFrameの対象数値が入ったカラムをレンジにグルーピングする

    Args:
        s_valuse (pd.series): レンジにカテゴライズする値のシリーズ
        bin_range (sorted list of int/ float): レンジ
        null_value (int/ float): 欠測値に入れる値
        unit_name (str, optional): Defaults to ''. レンジに入れる単位
        human_friendly (bool, optional): Defaults to False. 単位を人間がわかりやすいように丸めるか
        round_digit (int, optional): Defaults to 1. 単位を丸める際の桁
        lang (str, optional): Defaults to 'en'. ['en', 'ja']のどちらか。無効の値の場合は'en'
    """

    _s_values = pd.to_numeric((s_values)).fillna(null_value)
    bin_range.append(_s_values.min())
    bins = sorted(list(set(bin_range)))

    prefix = '~'
    suffix = ''
    suffix_last = '+'
    if lang == 'ja':
        prefix = ''
        suffix = '未満'
        suffix_last = '以上'

    if human_friendly:
        labels = ['{i}: {p}{b}{u}{s}'.format(i=i+1, p=prefix,
                                             b=human_friendly_format(b, round_digit),
                                             u=unit_name, s=suffix) for i, b in enumerate(bins[1:])]
        s_range = pd.cut(_s_values, bins=bins, labels=labels, right=False).astype(str)
        s_range = s_range.apply(lambda x: x if x != 'nan' else '{i}: {b}{u}{s}'.format(i=len(bins),
                                                                                       b=human_friendly_format(bins[-1], round_digit),
                                                                                       u=unit_name, s=suffix_last))
    else:
        labels = ['{i}: {p}{b}{u}{s}'.format(i=i+1, p=prefix,
                                             b=b,
                                             u=unit_name, s=suffix) for i, b in enumerate(bins[1:])]
        s_range = pd.cut(_s_values, bins=bins, labels=labels, right=False).astype(str)
        s_range = s_range.apply(lambda x: x if x != 'nan' else '{i}: {b}{u}{s}'.format(i=len(bins),
                                                                                       b=bins[-1],
                                                                                       u=unit_name, s=suffix_last))

    return s_range


def test():
    value_col = 'a'
    df = pd.DataFrame({value_col: [-1, 40, 20, 0, 1000, 203, 40, 30, 100000, 3432343]})
    print(df)

    df['range'] = bin_col(df[value_col], [0, 1, 2000, 200000, 300000], unit_name='円', lang='ja',
                          human_friendly=True)
    print(df)

    df['range'] = bin_col(df[value_col], [0, 1, 2000, 200000, 300000])
    print(df)


if __name__ == '__main__':
    test()
