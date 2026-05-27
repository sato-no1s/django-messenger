from google import genai
from django.conf import settings

# AIとの通信を管理する「魔法の関数」
def ask_ai(user_message):
    # ここにGeminiのAPIキーを設定
    # 受講生には Google AI Studio (aistudio.google.com) で取得してもらう
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    try:
        # AIへメッセージを送信
        # 新しい書き方：models.generate を使用
        prompt  = "あなたは親切なAIアシスタントです。次のユーザーからのメッセージに日本語で親身に答えてください。"
        prompt += "また、必ず絵文字を使わずに回答してください。内容: " + user_message

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        # 回答テキストを返却
        return response.text
        
    except Exception as e:
        return f"Gemini APIエラーが発生しました: {e}"