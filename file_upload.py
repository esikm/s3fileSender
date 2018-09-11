# -*- coding: utf-8 -*-
import sys
import requests
import boto3
import os
import string
import random
import urllib.parse
import unicodedata
import uuid

### こちらがカスタム設定です ###
filedomain = '独自ドメイン'
# 例
#    独自ドメインの場合 : 'https://mydomain.com/' 注意！最後のスラッシュは必要
#    S3直接の場合      : 'https://{s3のregion}.amazonaws.com/{バケット名}/'
bucket = 'バケット名'
s3prefix = 'temporary/' #任意のプレフィックス（ディレクトリ）
############################
zip_flg = False　　　# デフォルトではzip化なしに設定

try:
    filepath = sys.argv[1]
    if (len(sys.argv) >=3 and sys.argv[2] == 'zip'):
        zip_flg = True
    else:
        s3prefix += '45days/'
    if (len(sys.argv) >=4 and sys.argv[3]):
        s3prefix += sys.argv[3] + '/'
    else:
        s3prefix += '45days/'
except:
    print("*** エラー: ファイルパスを入力してください")
    sys.exit()

def is_japanese(string):
    for ch in string:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name \
        or "HIRAGANA" in name \
        or "KATAKANA" in name:
            return True
    return False

def rand_str(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])

def upload_to_s3(filepath):
    if os.path.exists(filepath):
        random_str = rand_str(10)
        if (zip_flg):
            password = rand_str(10)
            unique_code=uuid.uuid4()
            to_path =  s3prefix + random_str + '/'+ str(unique_code) + '.zip'
            fp = filepath
            if (filepath[-1:]=='/'):    fp = filepath[:-1]  # 末尾が'/'なら削除
            dir = os.path.dirname(fp)
            zip_path = dir + '/'+ str(unique_code)  + '.zip'
            if os.path.isdir(filepath):
                print("エラー：現在、ディレクトリzip圧縮はできません。ファイルを指定してください。")
                return
                # cmd = ['zip','-p',password, '-r', zip_path,filepath,'-x','*.DS_Store'] # ディレクトリzip化やるとしたらこんな感じだけどうまく行かなかったので、中止！
            else:
                cmd = ['zip', '-jP', password,zip_path,filepath]
            output = subprocess.run(cmd, stdout=subprocess.PIPE)
            output = output.stdout
            print(output)
            print ('*PasssWord : '+password)
            filepath = zip_path
        elif is_japanese(os.path.basename(filepath)):
            extension = os.path.splitext(filepath)[1]
            unique_code=uuid.uuid4()
            to_path =  s3prefix + random_str + '/'+ str(unique_code) + extension
        else:
            to_path =  s3prefix + random_str + '/'+ urllib.parse.quote(os.path.basename(filepath))
        boto3.resource('s3').Bucket(bucket).upload_file(filepath,to_path)
        boto3.resource('s3').ObjectAcl(bucket,to_path).put(ACL='public-read')
        print("**ファイルをアップロードしました。パス =  " + filedomain + to_path)
    else:
        print("**ファイルが存在しません。パス =  " + filepath)

upload_to_s3(filepath)
