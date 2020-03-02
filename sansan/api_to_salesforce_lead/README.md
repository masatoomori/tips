SanSanから登録完了通知が来たら、そのメールを所定の場所に転送することで、登録した名刺情報をSalesforceのリードに登録する

# 手順
1. SanSanに名刺を登録し、データ入力が完了するのを待つ
1. 所定のタグをつける
    - 名刺スキャン時につけてもPCからつけても可
1. 毎日23:50(JST)にAmazon SES（<所定のメールアドレス>）にメールを自動送信する。（Amazon SNSとcloudWatchで設定）  
ただし、即座にリードを作成したい場合は、手動でAmazon SES（<所定のメールアドレス>）にメールを送る。
    - Toに上記に追加して別のメールアドレスを指定すると動作が保証されないので注意
    - CCに追加しても問題はない
1. S3にメールが保存され、Lambdaが起動する
    1. SanSan APIにより対象データをダウンロードする。対象データは下記すべてを満たす
        - 送信者がSanSanに登録した名刺
        - 所定のタグをつけた名刺
        - メール送信日より3日以内に登録された名刺
        - 都道府県名が正しく入力された名刺（国外はスキップ）
    1. 対象データがすでにSalesforceに登録されているかを判別する
        - 対象データのEmailがSalesforceにある場合
            - リード所有者が本人の場合、何もしない
            - リード所有者が他人の場合、次のステップに進む
        - 対象データのEmailがSalesforceにない場合、次のステップに進む
    1. Salesforceのリードとして登録する
        - 苗字
        - 名前
        - 社名
        - 国名（日本限定）
        - 部署
        - 職位
        - 連絡先：固定電話、携帯電話、メールアドレス、FAX
        - 住所：郵便番号、都道府県、市区町村以降住所、ビル名
        - 名刺ID：Descriptionに保存
        - SanSan人物ID：Note_Placeholder__cに保存
        - SanSan会社ID：Status_Comments__cに保存
        - リードソース：<所定の値>
    1. 登録されたリード一覧を出力する（AWSログ上）
1. Salesforceにリードとして登録されていることを確認する
    - 登録完了通知が<所定のメールアドレス>から送られる（未実装）

# 設定
## API
SanSanからのダウンロード、SalesforceへのアップロードともにAPIを利用する

### SanSan
管理者権限には有効期限があるので、切れる前に延長申請すること

### Salesforce
すべてのSalesforceアカウントで利用可能なKeyとSecretを利用する。
Salesforceアカウントのパスワードには有効期限があるので、適時変更のこと

## ドメインの取得
Route 53で<ドメイン>を取得

## メール受信bucketの設定
<所定のメールアドレス>へのメールをAmazon S3に保存

## Lambdaの設定
### Lambda実行ロールの作成
IAM > ロールを作成
#### AWSLambdaExecute（既存選択）
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::*"
        }
    ]
}
```
#### s3-write（マニュアル作成）
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "*"
        }
    ]
}
```

### 基本設定
タイムアウト：1分
メモリ：128MB（108MB使用される）

## スクリプトの作成
### パッケージのダウンロード
Lambdaではpipインストールができないので、Lambda標準以外に必要なパッケージは同一ディレクトリにダウンロードし、
zipでまとめてアップロードする必要がある

#### simple-salesforce
```bash
$ pip install simple-salesforce -t .
```

#### requests
```bash
$ pip install requests -t .
```

#### pandas, numpy
numpyはC言語で実装されているため、Amazon Linuxでコンパイルされたバージョンが必要
```bash
$ git clone https://github.com/pbegle/aws-lambda-py3.6-pandas-numpy.git
```
