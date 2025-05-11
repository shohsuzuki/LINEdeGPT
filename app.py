
from flask import Flask, request, abort
import os
import openai
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

load_dotenv()
print("DEBUG LINE_CHANNEL_SECRET:", os.getenv("LINE_CHANNEL_SECRET"))


app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
openai.api_key = os.getenv("OPENAI_API_KEY")

import traceback

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    print("Signature:", signature)
    if signature is None:
        print("Signature missing!") 
        abort(400)
    body = request.get_data(as_text=True)
    print("Request Body:", body )
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Signature invalid!") 
        abort(400)

    except Exception as e:
        print("🔥 Unexpected Error:")
        traceback.print_exc()
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )
    reply = response.choices[0].message['content']

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

