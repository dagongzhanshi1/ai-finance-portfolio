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
# 方式 A：用 prompt 要求 JSON + json.loads()
# =============================================
print("=" * 60)
print("方式 A：在 prompt 里要求 JSON 格式")
print("=" * 60)

# 第 1 步：定义我们想要的 JSON 结构（用字典来描述）
# 这就相当于"告诉模型长什么样"
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": "你是一个金融分析师。请严格按 JSON 格式输出，不要加任何额外文字。"
        },
        {
            "role": "user",
            "content": """分析贵州茅台2024年财报，返回以下 JSON：

{
  "company": "公司名称",
  "revenue_billion": 营收（单位：亿元，float）,
  "revenue_growth": 营收同比增长率（如 0.15 表示15%）,
  "net_profit_billion": 净利润（亿元）,
  "gross_margin": 毛利率（如 0.9 表示90%）,
  "risk_points": ["风险1", "风险2", "风险3"],
  "rating": "看好" 或 "中性" 或 "谨慎"
}"""
        }
    ],
    temperature=0  # 设0让输出更稳定
)

content = response.choices[0].message.content
print("\n--- 原始输出 ---")
print(content)

# 第 2 步：用 json.loads() 解析成 Python 对象
try:
    result = json.loads(content)
    print("\n--- 解析后（Python 对象） ---")
    print(f"公司: {result['company']}")
    print(f"营收: {result['revenue_billion']} 亿元")
    print(f"净利润: {result['net_profit_billion']} 亿元")
    print(f"风险点: {result['risk_points']}")
    print(f"评级: {result['rating']}")

    # 这里展示 JSON 的好处——可以直接做计算
    if result['revenue_billion'] and result['net_profit_billion']:
        net_margin = result['net_profit_billion'] / result['revenue_billion']
        print(f"\n净利率（= 净利润/营收）: {net_margin:.1%}")
        # ↑ 自然语言做不到这个，必须 JSON 结构化数据

except json.JSONDecodeError as e:
    print(f"\n❌ JSON 解析失败: {e}")
    print("有时候模型输出的 JSON 格式不太标准，需要后处理修正。")


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

class FinancialAnalysis(BaseModel):
    """金融分析结果的标准化数据结构"""
    company: str               # 字符串
    revenue_billion: float     # 浮点数（营收，亿元）
    revenue_growth: float      # 浮点数（增长率）
    net_profit_billion: float  # 浮点数（净利润）
    gross_margin: float        # 浮点数（毛利率）
    risk_points: list[str]     # 字符串列表
    rating: str                # 字符串（评级）

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
            "content": """分析宁德时代2024年财报，返回以下 JSON：

{
  "company": "公司名称",
  "revenue_billion": 营收（亿元）,
  "revenue_growth": 营收同比增长率（如 0.2 表示20%）,
  "net_profit_billion": 净利润（亿元）,
  "gross_margin": 毛利率（如 0.25 表示25%）,
  "risk_points": ["风险1", "风险2"],
  "rating": "看好" 或 "中性" 或 "谨慎"
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
    analysis = FinancialAnalysis(**raw)

    print("\n--- Pydantic 校验通过 ✅ ---")
    print(f"公司: {analysis.company}")
    print(f"营收: {analysis.revenue_billion} 亿元")
    print(f"营收增速: {analysis.revenue_growth:.1%}")
    print(f"风险点: {analysis.risk_points}")
    print(f"评级: {analysis.rating}")

    # Pydantic 自动做了类型转换：
    # - 如果模型返回的是字符串 "2000"，Pydantic 会自动转成 float 2000
    # - 如果模型返回缺失字段，Pydantic 会报错
    # - 如果类型不对（比如营收是字符串"未知"），Pydantic 会报错
    print(f"\n类型整理: company 是 {type(analysis.company).__name__}，revenue 是 {type(analysis.revenue_billion).__name__}")

except (json.JSONDecodeError, Exception) as e:
    print(f"\n❌ 出错: {e}")


# =============================================
# 对比实验：自然语言 vs JSON
# =============================================
print("\n" + "=" * 60)
print("对比实验：自然语言输出 vs JSON 输出")
print("=" * 60)

# 问同一个问题两次，一次只要文字，一次要 JSON
for mode in ["自然语言", "JSON"]:
    if mode == "自然语言":
        msg = "比亚迪2024年营收和净利润是多少？赚了多少钱？"
        sys_prompt = "你是一个金融分析师。"
    else:
        msg = """比亚迪2024年营收和净利润是多少？返回 JSON：
{
  "company": "公司名称",
  "revenue_billion": 营收（亿元）,
  "net_profit_billion": 净利润（亿元）
}"""
        sys_prompt = "你是一个金融分析师。请严格返回JSON，不加额外文字。"

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": msg}
        ],
        temperature=0
    )

    text = resp.choices[0].message.content
    tokens = resp.usage.total_tokens

    print(f"\n--- {mode}（消耗 {tokens} tokens）---")
    print(text[:150])

# =============================================
# 小练习 —— 你自己试试
# =============================================
print("\n" + "=" * 60)
print("小练习：写一个自己的 Pydantic 模型")
print("=" * 60)
print("")
print("用下面的 StockRecommendation 模型来分析一只股票：")
print("")
print("class StockRecommendation(BaseModel):")
print("    stock_name: str")
print("    current_price: float")
print("    pe_ratio: float           # 市盈率")
print("    recommendation: str        # 买入/持有/卖出")
print("    reasons: list[str]         # 理由列表")
print("")
print("参考上面的代码，把 FinancialAnalysis 改成 StockRecommendation")
print("让模型分析茅台（600519），看看结果如何。")
