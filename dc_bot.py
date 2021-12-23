

import discord
from discord.ext import commands
from discord.ext.commands import bot
import datetime as dt
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()

TOKEN=os.getenv('discord_token')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# this main function is not working
# it should be called from telegram bot to send the downloaded file to discord
# any solution is welcome
# i am bad at discord bots as their API SUCKS ig
@bot.command()
async def send_file(file_name):
    channel = bot.get_channel()
    print(channel)
    await channel.send(file=discord.File(file_name))

# run the send_file function

bot.run(TOKEN)