"""Quản lý thời gian"""
import json, os, time, datetime, asyncio, discord, random
from discord.ext import tasks
from utils.reply import reply_id

# Circle task
@tasks.loop(seconds=1)
async def sec_check():
    from utils.bot import bot, val
    if val.CD == 0 and val.now_chat:
        await reply_id()
        
    if val.CD > 0:
        val.update('CD', -1)
    if val.CD_idle == 300:
        val.set('CD', 300)
    if val.CD_idle < 301:
        val.update('CD_idle', 1)
        if val.CD == 0:
            val.set('CD', 5)
