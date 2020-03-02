import msoffcrypto
import tempfile
import pandas as pd


def read_crypto_excel(file, sheet, password):
    with open(file, "rb") as f, tempfile.TemporaryFile() as tf:
        office_file = msoffcrypto.OfficeFile(f)
        office_file.load_key(password=password)
        office_file.decrypt(tf)
        # テンポラリファイルから回答をロード
        df = pd.read_excel(tf, sheet_name=sheet)

        return df

