"""Quản lý thời gian"""
import json, os, time, datetime, asyncio, discord, random, pytz
from discord.ext import tasks
from utils.reply import reply_id
from utils.funcs import remmid_edit
from utils.status import status_busy_set

morning_check = True
noon_check = True
afternoon_check = True
night_check = True
sleep_check = True
voice_leave = True

# Secs tasks
@tasks.loop(seconds=1)
async def sec_check():
    from utils.bot import bot, val
    from utils.funcs import update_ignore
    
    # Rep khi bot rảnh
    if val.CD == 0 and val.now_chat:
        asyncio.create_task(reply_id())
        
    # Trời lại làm việc nếu không có chat mới
    elif val.CD == 0 and not val.now_chat:
        if val.public: val.set('CD', val.chat_speed) # Chờ trước khi rep tiếp
        if val.CD_idle == val.to_worktime:
            val.set('CD', val.to_breaktime)
            await status_busy_set()
    
    # Đếm ngược tới thời gian check tin nhắn
    if val.CD > 0:
        val.update('CD', -1)
    
    # Đếm ngược tới thời gian work trở lại
    if val.CD_idle < val.to_worktime:
        val.update('CD_idle', 1)
    elif val.CD_idle > val.to_worktime:
        val.set('CD_idle', val.to_worktime)
    
    # Work trở lại
    if val.CD_idle == (val.to_worktime - 1):
        val.set('CD', val.to_breaktime)
        # Set lại status
        await status_busy_set()
        # Chat khi đổi mood

    update_ignore()
    update_mood()
    update_voice(val.mood_name)
    
# Daily tasks
@tasks.loop(seconds=60)
async def h_check():
    from utils.bot import bot, val
    
    # Có phải là ngày nghỉ?
    wcheck = is_weekend()
    if wcheck:
        val.set('weekend', True)
    else:
        val.set('weekend', False)
    # Load các biến tương ứng khoảng thời gian
    period = await get_current_period()
    
    val.set('now_period', period)
    val.load_val_char('saves/char.json', val.ai_char, period)
    if val.CD_idle == val.to_worktime:
        await status_busy_set()
        

# Lấy khoảng thời gian và xử lý các tác vụ
async def get_current_period(timezone_name="Asia/Bangkok"):
    global morning_check, noon_check, afternoon_check, night_check, sleep_check
    
    from utils.bot import bot, val
    from utils.funcs import v_leave_auto, voice_rcn
    
    my_timezone = pytz.timezone(timezone_name)
    now = datetime.datetime.now(my_timezone)
    
    act = val.normal_act
    if val.weekend:
        act = val.breakday_act
    
    char = val.ai_char
    
    # Define time ranges here (adjust based on your preferences):
    morning_start = datetime.time(hour=get_ctime(char, "morning", "start", t="h"), minute=get_ctime(char, "morning", "start", t="m"))
    morning_end = datetime.time(hour=get_ctime(char, "morning", "end", t="h"), minute=get_ctime(char, "morning", "end", t="m"))  # Adjust end time as needed

    noon_start = datetime.time(hour=get_ctime(char, "noon", "start", t="h"), minute=get_ctime(char, "noon", "start", t="m"))
    noon_end = datetime.time(hour=get_ctime(char, "noon", "end", t="h"), minute=get_ctime(char, "noon", "end", t="m"))

    afternoon_start = datetime.time(hour=get_ctime(char, "afternoon", "start", t="h"), minute=get_ctime(char, "afternoon", "start", t="m"))
    afternoon_end = datetime.time(hour=get_ctime(char, "afternoon", "end", t="h"), minute=get_ctime(char, "afternoon", "end", t="m"))

    evening_start = datetime.time(hour=get_ctime(char, "night", "start", t="h"), minute=get_ctime(char, "night", "start", t="m"))
    evening_end = datetime.time(hour=get_ctime(char, "night", "end", t="h"), minute=get_ctime(char, "night", "end", t="m"))

    night_start = datetime.time(hour=get_ctime(char, "sleep", "start", t="h"), minute=get_ctime(char, "sleep", "start", t="m"))
    night_end = datetime.time(hour=get_ctime(char, "sleep", "end", t="h"), minute=get_ctime(char, "sleep", "end", t="m"))  # Covers midnight to morning

    if morning_start <= now.time() <= morning_end:
        if morning_check:
            if random.random() < get_ctime(char, "morning", "voice"):
                await voice_rcn(val.last_vch_id)
            else:
                await v_leave_auto()
            morning_check = False
            
            rmd = remmid_edit(val.ignore_chat, "Your Phone: ", f"Your Phone: morning - {now.time}. Bạn đang '{act}'.")
            val.set('ignore_chat', rmd)
        
        sleep_check = True
        
        return "morning"
    elif noon_start <= now.time() <= noon_end:
        if noon_check:
            if random.random() < get_ctime(char, "noon", "voice"):
                await voice_rcn(val.last_vch_id)
            else:
                await v_leave_auto()
            noon_check = False

            rmd = remmid_edit(val.ignore_chat, "Your Phone: ", f"Your Phone: noon - {now.time}. Bạn đang '{act}'.")
            val.set('ignore_chat', rmd)
        
        morning_check = True
        
        return "noon"
    elif afternoon_start <= now.time() <= afternoon_end:
        if afternoon_check:
            if random.random() < get_ctime(char, "afternoon", "voice"):
                await voice_rcn(val.last_vch_id)
            else:
                await v_leave_auto()
            afternoon_check = False
            
            rmd = remmid_edit(val.ignore_chat, "Your Phone: ", f"Your Phone: afternoon - {now.time}. Bạn đang '{act}'.")
            val.set('ignore_chat', rmd)
        
        noon_check = True
        
        return "afternoon"
    elif evening_start <= now.time() <= evening_end:
        if night_check:
            if random.random() < get_ctime(char, "night", "voice"):
                await voice_rcn(val.last_vch_id)
            else:
                await v_leave_auto()
            night_check = False
        
            rmd = remmid_edit(val.ignore_chat, "Your Phone: ", f"Your Phone: night - {now.time}. Bạn đang '{act}'.")
            val.set('ignore_chat', rmd)
        
        afternoon_check = True
        
        return "night"
    else:
        if sleep_check:
            if random.random() < get_ctime(char, "sleep", "voice"):
                await voice_rcn(val.last_vch_id)
            else:
                await v_leave_auto()
            sleep_check = False
        
            rmd = remmid_edit(val.ignore_chat, "Your Phone: ", f"Your Phone: sleep - {now.time}. Bạn đang '{act}'.")
            val.set('ignore_chat', rmd)
        
        night_check = True
        
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

# Lấy thời gian dựa theo tính cách
def get_ctime(char, per, take, t="h"):
    with open('saves/char.json', "r", encoding="utf-8") as f:
        data = json.load(f)
        
    
    if take == "start":
        start_time = data[char][per]["start_time"]
        if t == "h":
            return start_time // 60
        elif t == "m":
            return start_time % 60

    elif take == "end":
        end_time = data[char][per]["end_time"]
        if t == "h":
            return end_time // 60
        elif t == "m":
            return end_time % 60

    elif take == "voice":
        voice = data[char][per]["voice"]
        return voice

# Cập nhật mood        
def update_mood():
    from utils.bot import val
    from utils.funcs import mood_restore
    
    chat = None
    
    # Quản lý mood cho bot
    mood_restore()
        
    # Lấy tên mood cho bot
    if -2000 < val.ai_mood < -1000:
        val.set('mood_name', "angry")
        chat = val.mood_angry
        
    elif -1000 < val.ai_mood < -500:
        val.set('mood_name', "sad")
        #chat = val.mood_sad
        val.set('mood_chat', True)
        
    elif -500 < val.ai_mood < 1000:
        val.set('mood_name', "normal")
        val.set('mood_chat', True)
        
    elif 1000 < val.ai_mood < 2000:
        val.set('mood_name', "happy")
        #chat = val.mood_happy
        val.set('mood_chat', True)
        
    elif 2000 < val.ai_mood < 4000:
        val.set('mood_name', "excited")
        chat = val.mood_excited
    
    if val.old_chat and val.mood_chat and chat:
        new_chat = val.now_chat
        new_chat.append(chat)
        val.set('now_chat', new_chat)
        val.set('mood_chat', False)

# Cập nhật voice
def update_voice(mood):
    from utils.bot import val
    
    if mood == "angry":
        if val.ai_char == "gentle":
            val.set('vv_pitch', -0.06)
            val.set('vv_iscale', 0.8)
            val.set('vv_speed', 0.7)
            
        elif val.ai_char == "cold":
            val.set('vv_pitch', -0.07)
            val.set('vv_iscale', 0.1)
            val.set('vv_speed', 0.7)
            
        elif val.ai_char == "extrovert":
            val.set('vv_pitch', -0.01)
            val.set('vv_iscale', 1)
            val.set('vv_speed', 0.9)
            
        elif val.ai_char == "introvert":
            val.set('vv_pitch', -0.06)
            val.set('vv_iscale', 0.5)
            val.set('vv_speed', 0.82)
            
        elif val.ai_char == "lazy":
            val.set('vv_pitch', -0.07)
            val.set('vv_iscale', 0.5)
            val.set('vv_speed', 0.6)
            
        elif val.ai_char == "tsundere":
            val.set('vv_pitch', -0.03)
            val.set('vv_iscale', 1.2)
            val.set('vv_speed', 0.8)
            
        elif val.ai_char == "yandere":
            val.set('vv_pitch', -0.08)
            val.set('vv_iscale', 2)
            val.set('vv_speed', 0.6)
            
        else:
            val.set('vv_pitch', -0.03)
            val.set('vv_iscale', 0.6)
            val.set('vv_speed', 0.8)
    
    if mood == "sad":
        if val.ai_char == "gentle":
            val.set('vv_pitch', -0.04)
            val.set('vv_iscale', 1)
            val.set('vv_speed', 0.8)
            
        elif val.ai_char == "cold":
            val.set('vv_pitch', -0.05)
            val.set('vv_iscale', 0.3)
            val.set('vv_speed', 0.8)
            
        elif val.ai_char == "extrovert":
            val.set('vv_pitch', 0.01)
            val.set('vv_iscale', 1.2)
            val.set('vv_speed', 1)
            
        elif val.ai_char == "introvert":
            val.set('vv_pitch', -0.04)
            val.set('vv_iscale', 0.7)
            val.set('vv_speed', 0.92)
            
        elif val.ai_char == "lazy":
            val.set('vv_pitch', -0.05)
            val.set('vv_iscale', 0.6)
            val.set('vv_speed', 0.7)
            
        elif val.ai_char == "tsundere":
            val.set('vv_pitch', -0.01)
            val.set('vv_iscale', 1.5)
            val.set('vv_speed', 0.9)
            
        elif val.ai_char == "yandere":
            val.set('vv_pitch', -0.06)
            val.set('vv_iscale', 1.9)
            val.set('vv_speed', 0.70)
            
        else:
            val.set('vv_pitch', -0.01)
            val.set('vv_iscale', 0.8)
            val.set('vv_speed', 0.9)
            
    if mood == "normal":
        if val.ai_char == "gentle":
            val.set('vv_pitch', -0.02)
            val.set('vv_iscale', 1.2)
            val.set('vv_speed', 0.9)
            
        elif val.ai_char == "cold":
            val.set('vv_pitch', -0.03)
            val.set('vv_iscale', 0.5)
            val.set('vv_speed', 0.9)
            
        elif val.ai_char == "extrovert":
            val.set('vv_pitch', 0.03)
            val.set('vv_iscale', 1.5)
            val.set('vv_speed', 1.1)
            
        elif val.ai_char == "introvert":
            val.set('vv_pitch', -0.02)
            val.set('vv_iscale', 0.9)
            val.set('vv_speed', 1.02)
            
        elif val.ai_char == "lazy":
            val.set('vv_pitch', -0.03)
            val.set('vv_iscale', 0.8)
            val.set('vv_speed', 0.8)
            
        elif val.ai_char == "tsundere":
            val.set('vv_pitch', 0.01)
            val.set('vv_iscale', 1.8)
            val.set('vv_speed', 1)
            
        elif val.ai_char == "yandere":
            val.set('vv_pitch', -0.04)
            val.set('vv_iscale', 1.8)
            val.set('vv_speed', 0.75)
            
        else:
            val.set('vv_pitch', 0)
            val.set('vv_iscale', 1)
            val.set('vv_speed', 1)
    
    if mood == "happy":
        if val.ai_char == "gentle":
            val.set('vv_pitch', 0)
            val.set('vv_iscale', 1.4)
            val.set('vv_speed', 1)
            
        elif val.ai_char == "cold":
            val.set('vv_pitch', -0.01)
            val.set('vv_iscale', 0.8)
            val.set('vv_speed', 1)
            
        elif val.ai_char == "extrovert":
            val.set('vv_pitch', 0.02)
            val.set('vv_iscale', 1.7)
            val.set('vv_speed', 1.15)
            
        elif val.ai_char == "introvert":
            val.set('vv_pitch', 0)
            val.set('vv_iscale', 1.1)
            val.set('vv_speed', 1.08)
            
        elif val.ai_char == "lazy":
            val.set('vv_pitch', -0.01)
            val.set('vv_iscale', 1)
            val.set('vv_speed', 0.9)
            
        elif val.ai_char == "tsundere":
            val.set('vv_pitch', 0.02)
            val.set('vv_iscale', 1.9)
            val.set('vv_speed', 1.05)
            
        elif val.ai_char == "yandere":
            val.set('vv_pitch', -0.02)
            val.set('vv_iscale', 1.9)
            val.set('vv_speed', 0.85)
            
        else:
            val.set('vv_pitch', 0.01)
            val.set('vv_iscale', 1.2)
            val.set('vv_speed', 1.1)
    
    if mood == "excited":
        if val.ai_char == "gentle":
            val.set('vv_pitch', 0.01)
            val.set('vv_iscale', 1.6)
            val.set('vv_speed', 1.1)
            
        elif val.ai_char == "cold":
            val.set('vv_pitch', 0.01)
            val.set('vv_iscale', 1)
            val.set('vv_speed', 1.05)
            
        elif val.ai_char == "extrovert":
            val.set('vv_pitch', 0.02)
            val.set('vv_iscale', 1.8)
            val.set('vv_speed', 1.2)
            
        elif val.ai_char == "introvert":
            val.set('vv_pitch', 0.01)
            val.set('vv_iscale', 1.3)
            val.set('vv_speed', 1.12)
            
        elif val.ai_char == "lazy":
            val.set('vv_pitch', 0.01)
            val.set('vv_iscale', 1.2)
            val.set('vv_speed', 1.09)
            
        elif val.ai_char == "tsundere":
            val.set('vv_pitch', 0.02)
            val.set('vv_iscale', 2)
            val.set('vv_speed', 1.15)
            
        elif val.ai_char == "yandere":
            val.set('vv_pitch', 0)
            val.set('vv_iscale', 2)
            val.set('vv_speed', 0.95)
            
        else:
            val.set('vv_pitch', 0.02)
            val.set('vv_iscale', 1.4)
            val.set('vv_speed', 1.15)


    