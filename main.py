import os
import errno
import tempfile
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage, FollowEvent
)
from keras.models import Sequential, load_model
from keras.preprocessing import image
import tensorflow as tf
import numpy as np
import urllib.request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

line_bot_api = LineBotApi('###') #アクセストークンを入れてください
handler = WebhookHandler('###') #Channel Secretを入れてください

#ユーザから送信された画像を保存するファイルを作成
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
try:
    os.makedirs(static_tmp_path)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
        pass
    else:
        raise

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

    #テキストメッセージが送信されたときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    
    # Aidemyの演習用Webページを取得する
    authority = "https://news.yahoo.co.jp/"
    r = requests.get(authority)
    # lxmlでパースする
    soup = BeautifulSoup(r.text, "html.parser")

    # ページ遷移のリンクを探すために<a>要素を取得する
    urls = soup.find_all("a")
    limitation=urls[28:34]

    title_list=[]
    url_list=[]
    for url in limitation:
        title=url.getText()
        title_list.append(title)
        whole_url = authority + url.get("href")
        url_list.append(whole_url)

    txt1=str(1)+"番目のニュースは「"+title_list[0]+"」です"
    url1="URL:"+url_list[0]
    txt2=str(2)+"番目のニュースは「"+title_list[1]+"」です"
    url2="URL:"+url_list[1]
    txt3=str(3)+"番目のニュースは「"+title_list[2]+"」です"
    url3="URL:"+url_list[2]
    
    
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=txt1+url1+txt2+url2+txt3+url3))

    #フォローイベント時の処理
@handler.add(FollowEvent)
def handle_follow(event):
    #誰が追加したかわかるように機能追加
    profile = line_bot_api.get_profile(event.source.user_id)
    line_bot_api.push_message("あなたのuserid",
        TextSendMessage(text="表示名:{}\nユーザID:{}\n画像のURL:{}\nステータスメッセージ:{}"\
        .format(profile.display_name, profile.user_id, profile.picture_url, profile.status_message)))

    #友達追加したユーザにメッセージを送信
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='友達追加ありがとうございます'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host ='0.0.0.0',port = port)