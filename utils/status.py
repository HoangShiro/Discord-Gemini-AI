import discord

idle_status = discord.Status.idle
onl_status = discord.Status.online
dnd_status = discord.Status.dnd
invisible = discord.Status.invisible

watching = discord.ActivityType.watching
playing = discord.ActivityType.playing
Astreaming = discord.ActivityType.streaming
listening = discord.ActivityType.listening
custom = discord.ActivityType.custom
competing = discord.ActivityType.competing
unknown = discord.ActivityType.unknown


async def atv_change():
    from utils.bot import val
    atype = unknown
    stt = idle_status
    if val.now_period == "morning":
        atype = listening
        stt = dnd_status
    elif val.now_period == "noon":
        atype = playing
        stt = idle_status
    elif val.now_period == "afternoon":
        atype = watching
        stt = dnd_status
    elif val.now_period == "night":
        atype = Astreaming
        stt = idle_status
    else:
        atype = watching
        stt = invisible
    return atype, stt

# Set status khi không chat
async def status_busy_set():
    from utils.bot import bot, val
    from saves.moods import angry, sad, normal, happy, excited
    
    atype, stt = await atv_change()
    
    mood = ""
    if val.mood_name == "angry":
        mood = angry
    elif val.mood_name == "sad":
        mood = sad
    elif val.mood_name == "normal":
        mood = normal
    elif val.mood_name == "happy":
        mood = happy
    elif val.mood_name == "excited":
        mood = excited
    
    act = f"{val.normal_act} {mood}"

    if val.weekend:
        act = f"{val.breakday_act} {mood}"

    now_act = discord.Activity(
        type=atype,
        name=act
    )

    await bot.change_presence(activity=now_act, status=stt)

# Set status khi chat
async def status_chat_set():
    from utils.bot import bot, val
    atype, stt = await atv_change()

    now_act = discord.Activity(
        type=atype,
        name=f"Chatting with {val.last_uname} 💬"
    )

    await bot.change_presence(activity=now_act, status=onl_status)