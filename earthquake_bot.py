import requests
import time
import os
from datetime import datetime
from telegram import Bot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
print("❌ توکن پیدا نشد")
exit()

bot = Bot(token=TOKEN)
sent_events = {}
chat_id = None

def send_message(text):
global chat_id
if chat_id:
try:
bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
except Exception as e:
print(f"خطا: {e}")

def get_iran_quakes():
try:
url = "http://irsc.ut.ac.ir/api/events"
r = requests.get(url, params={"start": "0", "count": "20"}, timeout=15)
if r.status_code == 200:
data = r.json()
return [e for e in data.get("events", []) if float(e.get("magnitude", 0)) >= 3.0]
except:
pass
return []

def get_world_quakes():
try:
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
r = requests.get(url, timeout=15)
if r.status_code == 200:
data = r.json()
return [f for f in data.get("features", []) if f["properties"].get("mag", 0) >= 4.5]
except:
pass
return []

def make_iran_msg(e):
mag = e.get("magnitude", "?")
place = e.get("place", "?")
depth = e.get("depth", "?")
lat, lon = e.get("lat"), e.get("lon")
map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "ندارد"
return f"<b>🇮🇷 زلزله ایران</b>\nبزرگا: {mag}\nمکان: {place}\nعمق: {depth}km\nنقشه: {map_link}"

def make_world_msg(f):
p = f["properties"]
mag = p.get("mag", "?")
place = p.get("place", "?")
coords = f["geometry"].get("coordinates", [])
lat, lon = coords[1] if len(coords) > 1 else None, coords[0] if len(coords) > 0 else None
map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "ندارد"
return f"<b>🌍 زلزله جهان</b>\nبزرگا: {mag}\nمکان: {place}\nنقشه: {map_link}"

def check():
global sent_events
for e in get_iran_quakes():
uid = f"iran_{e.get('id', e.get('time', ''))}"
if uid not in sent_events:
send_message(make_iran_msg(e))
sent_events[uid] = True
print(f"✅ ایران: {e.get('magnitude')}")
for f in get_world_quakes():
uid = f"world_{f['properties'].get('id', f['properties'].get('time', ''))}"
if uid not in sent_events:
send_message(make_world_msg(f))
sent_events[uid] = True
print(f"✅ جهان: {f['properties'].get('mag')}")
if len(sent_events) > 1000:
sent_events.clear()

def main():
global chat_id
print("🤖 ربات شروع شد")
last_check = datetime.now()
while True:
try:
for u in bot.get_updates():
if u.message and u.message.text and not chat_id:
chat_id = u.message.chat.id
print(f"✅ چت ذخیره شد: {chat_id}")
send_message("✅ ربات فعال شد!")
if (datetime.now() - last_check).seconds >= 300:
check()
last_check = datetime.now()
time.sleep(10)
except Exception as e:
print(f"❌ خطا: {e}")
time.sleep(30)

if name == "main":
main()
