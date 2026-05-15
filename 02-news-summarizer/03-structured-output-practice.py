"""
Day 17 — Structured Output（强制返回 JSON）

学习目标：
1. 什么是 Pydantic BaseModel
2. 为什么需要 JSON 输出（对比自然语言）
3. 两种方式实现结构化输出：
   方式 A：prompt 要求 JSON + json.loads()     ← DeepSeek 可用
   方式 B：OpenAI 原生 response_format parse() ← 仅 OpenAI
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# =============================================
# 方式 A 加强版：用 Pydantic 让代码更规范
# =============================================
print("\n" + "=" * 60)
print("方式 A + Pydantic：定义数据模型")
print("=" * 60)

# Pydantic：一个 Python 库，用来定义"数据长什么样"
# BaseModel 是 Pydantic 的核心类
# 你只需要写 class，它自动做类型校验

from pydantic import BaseModel

class StockRecommendation(BaseModel):
    stock_name: str              # 字符串
    current_price: float
    pe_ratio: float           # 市盈率
    recommendation: str        # 买入/持有/卖出
    reasons: list[str]         # 理由列表

# 用同样的 prompt 获取 JSON
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": "你是一个金融分析师。请严格按 JSON 格式输出，不要加任何额外文字。"
        },
        {
            "role": "user",
            "content": """分析茅台2024年财报，返回以下 JSON：

{
  "stock_name": "公司名称",
  "current_price": 现在价格（亿元）,
  "pe_ratio": 市盈率（如 0.2 表示20%）,
  "recommendation": 买入/持有/卖出,
  "reasons": ["理由1", "理由2"]
}"""
        }
    ],
    temperature=0
)

content = response.choices[0].message.content
print("\n--- 原始输出 ---")
print(content[:200])

try:
    raw = json.loads(content)
    # 用 Pydantic 模型来校验和转换数据
    analysis = StockRecommendation(**raw)

    print("\n--- Pydantic 校验通过 ✅ ---")
    print(f"公司: {analysis.stock_name}")
    print(f"当前股价: {analysis.current_price} 亿元")
    print(f"市盈率: {analysis.pe_ratio}")
    print(f"建议: {analysis.recommendation}")
    print(f"理由: {analysis.reasons}")

    # Pydantic 自动做了类型转换：
    # - 如果模型返回的是字符串 "2000"，Pydantic 会自动转成 float 2000
    # - 如果模型返回缺失字段，Pydantic 会报错
    # - 如果类型不对（比如营收是字符串"未知"），Pydantic 会报错
    print(f"\n类型整理: stock_name 是 {type(analysis.stock_name).__name__}")

except (json.JSONDecodeError, Exception) as e:
    print(f"\n❌ 出错: {e}")


