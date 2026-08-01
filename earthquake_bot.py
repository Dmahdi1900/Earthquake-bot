import requests
import time
import json
import os
from datetime import datetime, timedelta
from telegram import Bot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
print("❌ توکن پیدا نشد! متغیر TELEGRAM_BOT_TOKEN را تنظیم کنید.")
exit()

BOT = Bot(token=TOKEN)

SENT_EVENTS = {}
IRAN_MIN_MAG = 3.0
WORLD_MIN_MAG = 4.5
CHECK_INTERVAL = 300

CHAT_ID = None

def send_message(text):
if CHAT_ID:
try:
BOT.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
except Exception as e:
print(f"خطا در ارسال: {e}")

def get_iran_earthquakes():
try:
url = "http://irsc.ut.ac.ir/api/events"
params = {"start": "0", "count": "20"}
r = requests.get(url, params=params, timeout=15)
if r.status_code == 200:
data = r.json()
events = []
for item in data.get("events", []):
try:
mag = float(item.get("magnitude", 0))
if mag >= IRAN_MIN_MAG:
events.append(item)
except:
continue
return events
return []
except Exception as e:
print(f"خطا در دریافت زلزله ایران: {e}")
return []

def get_world_earthquakes():
try:
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
r = requests.get(url, timeout=15)
if r.status_code == 200:
data = r.json()
events = []
for feature in data.get("features", []):
mag = feature["properties"].get("mag", 0)
if mag and mag >= WORLD_MIN_MAG:
events.append(feature)
return events
return []
except Exception as e:
print(f"خطا در دریافت زلزله جهانی: {e}")
return []

def create_message_iran(event):
try:
mag = event.get("magnitude", "نامشخص")
place = event.get("place", "نامشخص")
time_str = event.get("time", "")
depth = event.get("depth", "نامشخص")
lat = event.get("lat")
lon = event.get("lon")

if time_str:
try:
dt = datetime.fromtimestamp(int(time_str)/1000)
time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
except:
pass

map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "ندارد"

msg = f"<b>🇮🇷 زلزله در ایران</b>\n"
msg += f"<b>بزرگا:</b> {mag}\n"
msg += f"<b>مکان:</b> {place}\n"
msg += f"<b>زمان:</b> {time_str}\n"
msg += f"<b>عمق:</b> {depth} کیلومتر\n"
msg += f"<b>نقشه:</b> {map_link}"
return msg
except Exception as e:
return f"⚠️ خطا: {e}"

def create_message_world(event):
try:
mag = event["properties"].get("mag", "نامشخص")
place = event["properties"].get("place", "نامشخص")
time_str = event["properties"].get("time", "")
depth = event["properties"].get("depth", "نامشخص")
coords = event["geometry"].get("coordinates", [])
lat = coords[1] if len(coords) > 1 else None
lon = coords[0] if len(coords) > 0 else None

if time_str:
try:
dt = datetime.fromtimestamp(int(time_str)/1000)
time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
except:
pass

map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "ندارد"

msg = f"<b>🌍 زلزله در جهان</b>\n"
msg += f"<b>بزرگا:</b> {mag}\n"
msg += f"<b>مکان:</b> {place}\n"
msg += f"<b>زمان:</b> {time_str}\n"
msg += f"<b>عمق:</b> {depth} کیلومتر\n"
msg += f"<b>نقشه:</b> {map_link}"
return msg
except Exception as e:
return f"⚠️ خطا: {e}"

def get_event_id_iran(event):
return f"iran_{event.get('id', event.get('time', ''))}"

def get_event_id_world(event):
return f"world_{event['properties'].get('id', event['properties'].get('time', ''))}"

def check_earthquakes():
global SENT_EVENTS
print("🔍 در حال بررسی زلزله‌ها...")

iran_events = get_iran_earthquakes()
for event in iran_events:
event_id = get_event_id_iran(event)
if event_id not in SENT_EVENTS:
msg = create_message_iran(event)
if msg:
send_message(msg)
SENT_EVENTS[event_id] = True
print(f"✅ ارسال زلزله ایران: {event.get('magnitude')} در {event.get('place')}")

world_events = get_world_earthquakes()
for event in world_events:
event_id = get_event_id_world(event)
if event_id not in SENT_EVENTS:
msg = create_message_world(event)
if msg:
send_message(msg)
SENT_EVENTS[event_id] = True
print(f"✅ ارسال زلزله جهانی: {event['properties'].get('mag')} در {event['properties'].get('place')}")

if len(SENT_EVENTS) > 1000:
SENT_EVENTS.clear()

def main():
global CHAT_ID
print("🤖 ربات زلزله شروع به کار کرد...")
print("⏳ برای دریافت شناسه چت، یک پیام به ربات بفرستید.")

last_check = datetime.now()

while True:
try:
updates = BOT.get_updates()
if updates:
for update in updates:
if update.message and update.message.text:
chat_id = update.message.chat.id
if CHAT_ID is None:
CHAT_ID = chat_id
print(f"✅ شناسه چت ذخیره شد: {CHAT_ID}")
send_message("✅ ربات فعال شد! هر ۵ دقیقه زلزله‌ها را بررسی می‌کند.")
else:
send_message("ربات در حال اجراست...")

now = datetime.now()
if (now - last_check).total_seconds() >= CHECK_INTERVAL:
check_earthquakes()
last_check = now

time.sleep(10)

except Exception as e:
print(f"❌ خطا: {e}")
time.sleep(30)

if name == "main":
main()
