from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# =============================================
# 实验 1：无结构 vs 有结构
# =============================================
print("=" * 55)
print("实验 1：无结构 Prompt vs 结构化 Prompt")
print("=" * 55)

prompts = [
    # 简单问法（无结构）
    "分析一下茅台的财报",

    # 结构化问法（给了角色 + 任务 + 输出格式）
    """你是一个财务分析师。请分析贵州茅台的2024年财报。

请按以下格式输出：
1. 营收：金额 + 同比增长率
2. 净利润：金额 + 同比增长率
3. 毛利率：百分比
4. 净利率：百分比
5. 核心风险：2-3点
6. 综合评级：看好/中性/谨慎"""
]

for i, p in enumerate(prompts):
    print(f"\n--- 实验 1-{i+1} ---")
    print(f"[输入]: {p[:40]}...")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": p}]
    )
    
    reply = response.choices[0].message.content
    print(f"[输出前 300 字]:\n{reply[:300]}")
    print(f"[token 消耗]: {response.usage.total_tokens}")
    print()

# =============================================
# 实验 2：Few-shot（给例子）vs 不给例子
# =============================================
print("=" * 55)
print("实验 2：不给例子 vs 给例子（Few-shot）")
print("=" * 55)

prompts_2 = [
    # 不给例子
    """请判断以下新闻对股市的情绪影响（positive/negative/neutral）：
新闻：央行宣布降准0.5个百分点，释放长期资金约1万亿元。""",

    # 给例子（Few-shot）
    """请判断以下新闻对股市的情绪影响（positive/negative/neutral）。

例子1：
新闻：贵州茅台三季度净利润同比增长15%。
情绪：positive

例子2：
新闻：美国对中国半导体出口管制进一步升级。
情绪：negative

例子3：
新闻：央行开展500亿元逆回购操作。
情绪：neutral

现在请判断：
新闻：央行宣布降准0.5个百分点，释放长期资金约1万亿元。"""
]

for i, p in enumerate(prompts_2):
    print(f"\n--- 实验 2-{i+1} ---")
    print(f"[输入]: 给例子={i==1}")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": p}]
    )
    
    reply = response.choices[0].message.content
    print(f"[输出]:\n{reply[:200]}")
    print(f"[token 消耗]: {response.usage.total_tokens}")
    print()

# =============================================
# 实验 3：调 temperature
# =============================================
print("=" * 55)
print("实验 3：不同 temperature 的效果")
print("=" * 55)

question = "请用一句话预测明天茅台股价的走势。"

for temp in [0, 0.5, 1.0, 1.5]:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": question}],
        temperature=temp
    )
    reply = response.choices[0].message.content
    print(f"\n[temperature={temp}]: {reply[:120]}")

print("\n" + "=" * 55)
print("思考题")
print("=" * 55)
print("1. 实验 1 中，无结构和有结构的输出，哪个更容易让程序处理？")
print("2. 实验 2 中，给例子后模型输出格式更规范了吗？额外花了多少 token？")
print("3. 实验 3 中，temperature 调高后回答有什么变化？")
