"""
Day 18 — Function Calling（让模型调你的代码）

学习目标：
1. 什么是 Function Calling — 不是"模型直接调函数"，是三步走流程
2. 定义 tool schema（告诉模型有什么函数可以用）
3. 三步走：模型判断 → 你执行 → 结果回传 → 模型回答
4. 真实金融场景：股价查询、财报查询、计算器

前提：你需要理解这个图——

  你问"茅台今天多少钱"
       ↓
  模型看了 tools，说"我要调 get_stock_price(600519)"
       ↓
  ★ 你的代码执行 get_stock_price
       ↓
  ★ 把结果返回给模型
       ↓
  模型看了结果，回答你"茅台今天股价 1800.50 元"

注意：模型不是真的去查了股价！
模型只是说"我建议调这个函数"，真正执行的是你的代码。
"""

from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# =============================================
# 第一步：定义 tool（函数）的 schema
# =============================================
print("=" * 60)
print("第一步：定义 Tool Schema")
print("=" * 60)
print()

# Tool Schema 就是告诉模型：
# "我有这些函数可以用，它们的参数分别是..."
# 格式是 JSON Schema（和 Day 17 学的 JSON 结构类似）

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "查询 A 股实时股价（模拟数据）",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "股票代码，6位数字，如 600519"
                    },
                    "market": {
                        "type": "string",
                        "enum": ["sh", "sz", "bj"],
                        "description": "交易所：sh=上交所, sz=深交所, bj=北交所"
                    }
                },
                "required": ["stock_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_info",
            "description": "查询公司基本信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "公司全称或股票名称"
                    }
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_pe_ratio",
            "description": "计算市盈率（PE）= 股价 / 每股收益",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "number",
                        "description": "当前股价（元）"
                    },
                    "eps": {
                        "type": "number",
                        "description": "每股收益（元）"
                    }
                },
                "required": ["price", "eps"]
            }
        }
    }
]

print("已定义 3 个工具：")
for t in tools:
    fn = t["function"]
    print(f"  📌 {fn['name']}: {fn['description']}")
    params = fn["parameters"]["properties"]
    print(f"     参数: {', '.join(params.keys())}")
    print()


# =============================================
# 第二步：实现真正的 Python 函数
# =============================================
print("=" * 60)
print("第二步：实现 Python 函数")
print("=" * 60)
print()

# 这些是真正会执行的代码！
# 模型只是说"我建议调这个"，你的代码真正跑

def get_stock_price(stock_code: str, market: str = "sh") -> dict:
    """模拟查询股价的函数。
    
    真实场景：这里会调一个股票数据 API（如新浪财经、tushare）
    我们现在用模拟数据训练流程，懂了再换真实 API。
    """
    # 模拟数据库
    prices = {
        "600519": 1800.50,   # 贵州茅台
        "300750": 220.30,    # 宁德时代
        "000858": 150.80,    # 五粮液
        "601318": 45.60,     # 中国平安
        "000333": 68.90,     # 美的集团
        "600036": 38.20,     # 招商银行
    }
    
    price = prices.get(stock_code)
    if price is None:
        return {
            "code": stock_code,
            "market": market,
            "price": None,
            "error": f"未找到股票 {stock_code} 的数据"
        }
    
    return {
        "code": stock_code,
        "market": market,
        "price": price,
        "currency": "CNY",
        "change_percent": round((price - 1700) / 1700 * 100, 2),  # 模拟涨跌幅
    }


def get_company_info(company_name: str) -> dict:
    """模拟查询公司基本信息"""
    database = {
        "贵州茅台": {
            "full_name": "贵州茅台酒股份有限公司",
            "stock_code": "600519",
            "industry": "白酒",
            "market_cap": "2.3万亿",
            "description": "中国高端白酒龙头企业，主打产品飞天茅台"
        },
        "宁德时代": {
            "full_name": "宁德时代新能源科技股份有限公司",
            "stock_code": "300750",
            "industry": "新能源电池",
            "market_cap": "1.1万亿",
            "description": "全球最大的动力电池制造商"
        },
        "中国平安": {
            "full_name": "中国平安保险(集团)股份有限公司",
            "stock_code": "601318",
            "industry": "金融保险",
            "market_cap": "8000亿",
            "description": "综合金融保险集团"
        }
    }
    
    # 支持模糊匹配（输入"茅台"也能匹配到"贵州茅台"）
    for key, info in database.items():
        if company_name in key or key in company_name:
            return info
    
    return {"error": f"未找到公司: {company_name}"}


def calculate_pe_ratio(price: float, eps: float) -> dict:
    """计算市盈率"""
    if eps == 0:
        return {"error": "每股收益不能为零"}
    
    pe = price / eps
    return {
        "price": price,
        "eps": eps,
        "pe_ratio": round(pe, 2),
        "evaluation": "高估" if pe > 50 else "合理偏高" if pe > 30 else "合理" if pe > 15 else "低估" if pe > 0 else "亏损"
    }


# 把所有函数放进一个字典，方便按名字调用
available_functions = {
    "get_stock_price": get_stock_price,
    "get_company_info": get_company_info,
    "calculate_pe_ratio": calculate_pe_ratio,
}

print("已实现 3 个 Python 函数")
print(f"  ✅ get_stock_price('600519') → {get_stock_price('600519')}")
print(f"  ✅ get_company_info('茅台') → {get_company_info('茅台')['full_name']}")
print(f"  ✅ calculate_pe_ratio(1800.5, 42.0) → {calculate_pe_ratio(1800.5, 42.0)}")
print()


# =============================================
# 第三步：完整的 Function Calling 流程
# =============================================
print("=" * 60)
print("第三步：完整 Function Calling 流程")
print("=" * 60)
print()
print("流程：用户提问 → 模型判断是否要调工具 → 你执行 → 结果回传 → 模型回答")
print()

# --- 第 1 轮：用户提问 ---
messages = [
    {"role": "system", "content": "你是一个金融助手。当用户查询股票或公司信息时，使用 available tools 获取数据。"},
    {"role": "user", "content": "贵州茅台今天股价多少？顺便帮我算一下如果每股收益是42元，市盈率是多少？"}
]

print("▶ 用户提问：贵州茅台今天股价多少？顺便算一下市盈率")
print()

# 第一步：调模型，传入 tools
print("📤 第 1 步：调模型，传入 tools 参数...")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="auto",  # auto = 模型自己决定要不要调
    temperature=0
)

msg = response.choices[0].message

# 第二步：看模型是否要求调工具
if msg.tool_calls:
    print(f"📥 模型决定调 {len(msg.tool_calls)} 个工具：")
    print()
    
    # 把模型的回复添加到消息历史（很重要！不然模型不知道它刚才说了什么）
    messages.append(msg)
    
    for tool_call in msg.tool_calls:
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)
        
        print(f"  🛠 调 {fn_name}({json.dumps(fn_args, ensure_ascii=False)})")
        
        # ★ 关键：你的代码执行函数
        fn_to_call = available_functions[fn_name]
        fn_result = fn_to_call(**fn_args)
        
        print(f"  📊 结果: {json.dumps(fn_result, ensure_ascii=False)}")
        print()
        
        # ★ 关键：把结果返回给模型
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(fn_result, ensure_ascii=False)
        })
    
    # 第三步：把工具结果还给模型，让模型生成最终回答
    print("📤 第 3 步：把结果返回给模型，让它生成最终回答...")
    final = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0
    )
    
    print(f"\n💬 模型最终回答：")
    print(final.choices[0].message.content)
else:
    print("📥 模型没有要求调工具，直接回答：")
    print(msg.content)

print()


# =============================================
# 核心理解：三步走
# =============================================
print("=" * 60)
print("⭐ 核心理解：Function Calling 的三步走")
print("=" * 60)
print()
print("  第 1 步：模型选择调 XX 函数，决定参数 YY")
print("    → response.choices[0].message.tool_calls 不为空")
print("    → tool_call.function.name = 函数名")
print("    → tool_call.function.arguments = JSON 参数")
print("    （模型自己根据用户的问题来判断用什么工具、传什么参数）")
print()
print("  ★ 第 2 步：你的代码执行函数")
print("    → 你在 Python 里调 available_functions[name](**args)")
print("    → 这是真正的代码在跑，不是模型在跑")
print("    → 真实场景：查数据库、调外部 API、做计算")
print()
print("  ★ 第 3 步：把结果还给模型")
print("    → 用 role='tool' 的消息把结果塞回去")
print("    → 模型看了结果再生成自然语言回答")
print()
print("  面试常考：Function Calling 的三步走流程")
print("  模型选择工具 → 你执行工具 → 结果回传 → 模型回答")
print()


# =============================================
# 更复杂的例子：多轮对话 + 多次工具调用
# =============================================
print("=" * 60)
print("拓展例子：多轮对话 + 连续工具调用")
print("=" * 60)
print()

def function_calling_chat(user_input):
    """封装好的 Function Calling 对话函数"""
    
    chat_messages = [
        {"role": "system", "content": "你是一个金融助手。查询数据时必须使用提供的工具。"},
        {"role": "user", "content": user_input}
    ]
    
    # 最多允许 5 轮工具调用（防止死循环）
    max_rounds = 5
    round_count = 0
    
    while round_count < max_rounds:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_messages,
            tools=tools,
            tool_choice="auto",
            temperature=0
        )
        
        msg = response.choices[0].message
        
        # 如果模型不需要调工具了，直接返回
        if not msg.tool_calls:
            return msg.content
        
        # 模型要求调工具
        chat_messages.append(msg)
        
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            fn_to_call = available_functions[fn_name]
            fn_result = fn_to_call(**fn_args)
            
            chat_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(fn_result, ensure_ascii=False)
            })
        
        round_count += 1
    
    return "工具调用次数过多，已终止。"


# 测试
print("▶ 用户：宁德时代这家公司怎么样？查一下信息，再查一下股价")
print()
result = function_calling_chat("宁德时代这家公司怎么样？查一下信息，再查一下股价")
print(f"💬 {result}")
print()


# =============================================
# 小练习
# =============================================
print("=" * 60)
print("🎯 小练习")
print("=" * 60)
print()
print("给你的任务：")
print()
print("1. 运行这个脚本，看看能不能跑通")
print("2. 加一个新的 tool — get_news_sentiment(company_name)")
print("   让它接收公司名，返回模拟的新闻情绪分析结果")
print("3. 试试问模型「中国平安的股价和公司信息」")
print("   看模型会不会连续调两个工具")
print()
print("完成后告诉我，我给你看看你的代码对不对 💪")
