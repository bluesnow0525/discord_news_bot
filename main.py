import discord
import json
from discord.ext import commands, tasks
from datetime import datetime
import os
from craw import craw
from dotenv import load_dotenv
import pytz
# 设置目标时区：例如台北时间
target_tz = pytz.timezone('Asia/Taipei')

# 获取当前的 UTC 时间
now_utc = datetime.now(pytz.utc)

# 转换为目标时区时间
now_local = now_utc.astimezone(target_tz)
load_dotenv()
def get_emoji(pair):
    if pair == "USD":
        return "🇺🇸"
    elif pair == "EUR":
        return "🇪🇺"
    elif pair == "GBP":
        return "🇬🇧"
    elif pair == "CAD":
        return "🇨🇦"
    elif pair == "CNY":
        return "🇨🇳"
    elif pair == "JPY":
        return "🇯🇵"
    elif pair == "CHF":
        return "🇨🇭"
    elif pair == "AUD":
        return "🇦🇺"
    elif pair == "NZD":
        return "🇳🇿"

def get_impacticon(impacticon):
    if impacticon == "icon--ff-impact-red":
        return "exclamation"
    else:
        return "white_medium_small_square"
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_IDS = os.getenv('DISCORD_CHANNEL_IDS')
channel_ids = [int(id.strip()) for id in CHANNEL_IDS.split(',')]

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    timed_message.start()  # 啟動定時任務

@tasks.loop(minutes=60)  # 設定定時任務的間隔（這裡設為每分鐘）
async def timed_message():
    now = datetime.now(pytz.utc).astimezone(target_tz)
    today_str = now.strftime('%Y-%m-%d')
    json_path = 'date_record.json'
    try:
        # 嘗試讀取已存在的JSON檔案
        with open(json_path, 'r') as file:
            date_record = json.load(file)
    except FileNotFoundError:
        # 如果檔案不存在，創建一個新的字典
        date_record = {}
    except json.JSONDecodeError:
        # 文件是空的或內容不是有效的JSON，返回一個空字典
        date_record = {}
    if today_str in date_record:
        print("今天的日期已處理過。")
    else:
        # 如果今日日期未記錄，則添加到字典並更新JSON檔案
        print("處理今天的日期。")
        date_record[today_str] = True
        with open(json_path, 'w') as file:
            json.dump(date_record, file)
        if (now.weekday() == 6 and now.hour == 15):  # 檢查是否為周日15點
            for channel_id in channel_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    events = craw()
                    events_grouped = events.groupby(by="Date")
                    events_by_date = {date: group.to_dict('records') for date, group in events_grouped}
                    for date in events_by_date.keys():
                        events = events_by_date[date]
                        # datetime.strptime(date,'%a%b %d').strftime("%a %m/%d")
                        embed = discord.Embed(title=f"**{date.strftime("%a %m/%d")}**", color=0x800000)
                        for event in events:
                            event_details = (
                                f"{get_emoji(event['Currency'])} "
                                f" {event['Time'].strftime("%H:%M")} "
                                f":{get_impacticon(event['Impact'])}: **{event['Event']} **"                  
                            )
                            
                            embed.add_field(name="\u200B", value=event_details, inline=False)  # \u200B is a zero-width space

                        await channel.send(embed=embed)
bot.run(TOKEN)  # 替換成你的機器人 Token