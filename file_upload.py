# coding: utf-8
import sys
import requests
import boto3
import os
import string
import random

### こちらがカスタム設定です ###
filedomain = '独自ドメイン'
# 例
#    独自ドメインの場合 : 'https://mydomain.com/' 注意！最後のスラッシュは必要
#    S3直接の場合      : 'https://{s3のregion}.amazonaws.com/{バケット名}/'
bucket = 'バケット名'
s3prefix = 'temporary/45days/' #任意のプレフィックス（ディレクトリ）
############################

try:
    filepath = sys.argv[1]
except:
    print("*** エラー: ファイルパスを入力してください")
    sys.exit()

def upload_to_s3(filepath):
    if os.path.exists(filepath):
        n = 10  # 10文字の乱数を作成
        random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
        to_path =  s3prefix + random_str + '/'+ os.path.basename(filepath)
        boto3.resource('s3').Bucket(bucket).upload_file(filepath,to_path)
        boto3.resource('s3').ObjectAcl(bucket,to_path).put(ACL='public-read')
        print("**ファイルをアップロードしました。パス = "+ filedomain + to_path)
    else:
        print("**ファイルが存在しません。パス = "+filepath)

upload_to_s3(filepath)
