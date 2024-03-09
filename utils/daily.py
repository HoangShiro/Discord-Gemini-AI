"""Quản lý thời gian"""
import json, os, time, datetime, asyncio, discord, random, pytz
from discord.ext import tasks
from utils.reply import reply_id
from utils.funcs import remmid_edit
from utils.status import status_busy_set, status_chat_set

# Secs tasks
@tasks.loop(seconds=1)
async def sec_check():
    from utils.bot import bot, val
    
    # Rep khi bot rảnh
    if val.CD == 0 and val.now_chat:
        await reply_id()
        
    # Trời lại làm việc nếu không có chat mới
    elif val.CD == 0 and not val.now_chat:
        if val.CD_idle == val.to_worktime:
            val.set('CD', val.to_breaktime)
            await status_busy_set()
    
    # Đếm ngược tới thời gian check tin nhắn
    if val.CD > 0:
        val.update('CD', -1)
    
    # Đếm ngược tới thời gian work trở lại
    if val.CD_idle < val.to_worktime:
        val.update('CD_idle', 1)

    # Work trở lại
    if val.CD_idle == (val.to_worktime - 1):
        val.set('CD', val.to_breaktime)
        # Set lại status
        await status_busy_set()

# Daily tasks
@tasks.loop(seconds=1800)
async def h_check():
    from utils.bot import bot, val
    # Có phải là ngày nghỉ?
    wcheck = is_weekend()
    if wcheck:
        val.set('weekend', True)
    else:
        val.set('weekend', False)
    # Load các biến tương ứng khoảng thời gian
    period = get_current_period()
    val.set('now_period', period)
    val.load_val_char('saves/char.json', val.ai_char, period)
    if val.CD_idle == val.to_worktime:
        await status_busy_set()

# Lấy khoảng thời gian và xử lý các tác vụ
def get_current_period(timezone_name="Asia/Bangkok"):
    from utils.bot import bot, val
    my_timezone = pytz.timezone(timezone_name)
    now = datetime.datetime.now(my_timezone)

    # Define time ranges here (adjust based on your preferences):
    morning_start = datetime.time(hour=7)
    morning_end = datetime.time(hour=11, minute=59)  # Adjust end time as needed

    noon_start = datetime.time(hour=12)
    noon_end = datetime.time(hour=13, minute=59)

    afternoon_start = datetime.time(hour=14)
    afternoon_end = datetime.time(hour=17, minute=59)

    evening_start = datetime.time(hour=18)
    evening_end = datetime.time(hour=22, minute=59)

    night_start = datetime.time(hour=23)
    night_end = datetime.time(hour=6, minute=59)  # Covers midnight to morning

    act = val.normal_act
    if val.weekend:
        act = val.breakday_act

    if morning_start <= now.time() <= morning_end:
        remmid_edit(val.now_chat, "Your Phone: ", f"Your Phone: morning - {now.time}. Bạn đang '{act}'.")
        return "morning"
    elif noon_start <= now.time() <= noon_end:
        remmid_edit(val.now_chat, "Your Phone: ", f"Your Phone: noon - {now.time}. Bạn đang '{act}'.")
        return "noon"
    elif afternoon_start <= now.time() <= afternoon_end:
        remmid_edit(val.now_chat, "Your Phone: ", f"Your Phone: afternoon - {now.time}. Bạn đang '{act}'.")
        return "afternoon"
    elif evening_start <= now.time() <= evening_end:
        remmid_edit(val.now_chat, "Your Phone: ", f"Your Phone: night - {now.time}. Bạn đang '{act}'.")
        return "night"
    else:
        remmid_edit(val.now_chat, "Your Phone: ", f"Your Phone: sleep - {now.time}. Bạn đang '{act}'.")
        return "sleep"

# Ngày nghỉ?  
def is_weekend(timezone_name="Asia/Bangkok"):
  # Lấy ngày hiện tại với múi giờ "Asia/Bangkok"
  today = datetime.datetime.now(pytz.timezone(timezone_name))

  # Kiểm tra xem ngày hôm nay có phải là Thứ 7 hoặc CN hay không
  return today.weekday() in [5, 6]

# Lấy thời gian thực HH:MM:SS
def get_real_time(timezone_name="Asia/Bangkok"):
    my_timezone = pytz.timezone(timezone_name)
    now = datetime.datetime.now(my_timezone)

    return f"{now.hour}:{now.minute}:{now.second}"