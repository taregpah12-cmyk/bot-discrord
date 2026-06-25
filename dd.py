import discord
from discord.ext import commands
import json
import random
import time
import os

TOKEN = "MTUxNzExNzE1NjA5NjIxMzA0Mw.GHT-KE.YHUZGjvT3KaYtUdP9k0WZP0ao-p623BDmQBMWc"  

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"





# ================== DATA ==================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"companies": {}}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {"companies": {}}
            return json.loads(content)

    except:
        return {"companies": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


data = load_data()

# ================== BOT DATA ==================

BOT_NAMES = [
    "Alpha Bot","Beta Bot","Gamma Bot","Delta Bot",
    "Sigma Bot","Omega Bot","X1 Bot","X2 Bot","X3 Bot"
]

# ================== READY ==================

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("Bot Ready 🚀 (Synced)")
    except Exception as e:
        print("Sync Error:", e)

# ================== CREATE COMPANY ==================

@bot.tree.command(name="انشاء-شركة")
async def create_company(interaction: discord.Interaction, name: str):

    user = str(interaction.user.id)

    if user in data["companies"]:
        return await interaction.response.send_message("❌ عندك شركة بالفعل")

    data["companies"][user] = {
        "name": name,
        "balance": 10000,
        "income": 100,
        "employees": [],
        "lastWork": 0,
        "lastHire": 0,
        "loan": 0
    }

    save_data(data)

    await interaction.response.send_message(f"🏢 تم إنشاء شركة {name}")

# ================== INFO ==================

@bot.tree.command(name="معلومات-شركتك")
async def company_info(interaction: discord.Interaction):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    c = data["companies"][user]

    embed = discord.Embed(title=f"🏢 {c['name']}")
    embed.add_field(name="💰 الرصيد", value=c["balance"])
    embed.add_field(name="👥 الموظفين", value=len(c["employees"]))
    embed.add_field(name="💵 الدخل", value=c["income"])

    await interaction.response.send_message(embed=embed)

# ================== WORK ==================

@bot.tree.command(name="العمل")
async def work(interaction: discord.Interaction):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    c = data["companies"][user]

    now = int(time.time())

    if now - c["lastWork"] < 3600:
        return await interaction.response.send_message("⏳ انتظر ساعة")

    power = sum(e.get("level", 1) for e in c["employees"])

    profit = random.randint(500, 2000) + c["income"] + (power * 20)

    c["balance"] += profit
    c["lastWork"] = now

    save_data(data)

    await interaction.response.send_message(f"💵 ربحت {profit}$")

# ================== HIRE ==================

@bot.tree.command(name="توظيف")
async def hire(interaction: discord.Interaction, عدد: int):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    if عدد <= 0 or عدد > 2:
        return await interaction.response.send_message("❌ عدد غير صالح")

    c = data["companies"][user]
    now = int(time.time())

    if now - c["lastHire"] < 7200:
        remaining = 7200 - (now - c["lastHire"])
        return await interaction.response.send_message(f"⏳ انتظر {remaining//60} دقيقة")

    cost_per_employee = 2000
    total_cost = cost_per_employee * عدد

    if c["balance"] < total_cost:
        return await interaction.response.send_message("❌ رصيدك لا يكفي")

    c["balance"] -= total_cost
    c["lastHire"] = now

    for _ in range(عدد):
        c["employees"].append({
            "name": random.choice(BOT_NAMES),
            "level": 1,
            "salary": random.randint(300, 800)
        })

    save_data(data)

    await interaction.response.send_message(f"🤖 تم توظيف {عدد}")

# ================== EMPLOYEES ==================

@bot.tree.command(name="موظفيك")
async def employees(interaction: discord.Interaction):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    c = data["companies"][user]

    if not c["employees"]:
        return await interaction.response.send_message("❌ ما عندك موظفين")

    text = "🤖 موظفيك:\n\n"

    for i, e in enumerate(c["employees"], 1):
        text += f"{i}. {e['name']} (Lv {e.get('level',1)})\n"

    await interaction.response.send_message(text)

# ================== UPGRADE ==================

@bot.tree.command(name="ترقية-موظف")
async def upgrade(interaction: discord.Interaction, رقم: int):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    c = data["companies"][user]

    if رقم <= 0 or رقم > len(c["employees"]):
        return await interaction.response.send_message("❌ رقم غير صحيح")

    emp = c["employees"][رقم - 1]

    emp.setdefault("level", 1)
    emp.setdefault("salary", 500)

    if emp["level"] >= 5:
        return await interaction.response.send_message("❌ وصل أعلى مستوى")

    cost = emp["level"] * 3000

    if c["balance"] < cost:
        return await interaction.response.send_message("❌ ما عندك فلوس")

    c["balance"] -= cost
    emp["level"] += 1
    emp["salary"] += 200

    save_data(data)

    await interaction.response.send_message(f"⬆️ تم ترقية {emp['name']}")

# ================== SALARY ==================

@bot.tree.command(name="صرف-رواتب")
async def salaries(interaction: discord.Interaction):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    c = data["companies"][user]

    if not c["employees"]:
        return await interaction.response.send_message("❌ ما عندك موظفين")

    total = sum(e.get("salary", 500) for e in c["employees"])

    if c["balance"] < total:
        return await interaction.response.send_message("❌ ما عندك فلوس")

    c["balance"] -= total
    save_data(data)

    await interaction.response.send_message(f"💰 تم صرف {total}$")

# ================== LEADERBOARD ==================

@bot.tree.command(name="leaderboard")
async def leaderboard(interaction: discord.Interaction):

    sorted_data = sorted(
        data["companies"].items(),
        key=lambda x: x[1]["balance"],
        reverse=True
    )

    if not sorted_data:
        return await interaction.response.send_message("❌ ما فيه شركات")

    text = "🏆 الترتيب:\n\n"

    for i, (uid, c) in enumerate(sorted_data, 1):
        text += f"{i}. {c['name']} - 💰 {c['balance']}$\n"

    await interaction.response.send_message(text)

# ================== LOAN ==================

@bot.tree.command(name="قرض")
async def loan(interaction: discord.Interaction, مبلغ: int):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    c = data["companies"][user]

    if c["loan"] > 0:
        return await interaction.response.send_message("❌ عندك قرض")

    c["balance"] += مبلغ
    c["loan"] = int(مبلغ * 1.2)

    save_data(data)

    await interaction.response.send_message(f"🏦 قرض: {مبلغ}$")

# ================== REPAY ==================

@bot.tree.command(name="سداد-القرض")
async def repay(interaction: discord.Interaction):

    user = str(interaction.user.id)

    if user not in data["companies"]:
        return await interaction.response.send_message("❌ ما عندك شركة")

    c = data["companies"][user]

    if c["loan"] <= 0:
        return await interaction.response.send_message("❌ ما عندك قرض")

    if c["balance"] < c["loan"]:
        return await interaction.response.send_message("❌ ما عندك فلوس")

    c["balance"] -= c["loan"]
    c["loan"] = 0

    save_data(data)

    await interaction.response.send_message("💳 تم السداد")

# ================== RUN ==================

bot.run(TOKEN)