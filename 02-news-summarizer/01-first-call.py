from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个金融分析助手。"},
        {"role": "user", "content": "请用一句话解释什么是市盈率（PE）。"}
    ]
)

print(response.choices[0].message.content)
print(f"--- 使用 token: {response.usage.total_tokens} ---")
