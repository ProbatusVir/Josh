import time
import discord
from dotenv import dotenv_values
from discord.ext import commands

config = dotenv_values(".env")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="~", intents=intents)

start_time = None

