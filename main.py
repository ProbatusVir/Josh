# This example requires the 'message_content' intent.
import time

import discord
from dotenv import dotenv_values
from discord import app_commands
from discord.ext import commands

config = dotenv_values(".env")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="~", intents=intents)

start_time = time.time() #my foolishness

@bot.event
async def on_ready():
	try:
		synced = await bot.tree.sync()
		print(f'Synced: {len(synced)} commands')
	except Exception as e:
		print(f'[ERROR]\t{e}')

	await bot.change_presence(activity=discord.Activity(name='Shinji whine', type=discord.ActivityType.listening))
	print(f'We have logged in as {bot.user}')



@bot.tree.command(
	name="runtime",
	description="Find out how long the bot's been running!",
)
async def runtime(interaction : discord.Interaction):
	ct = time.localtime(start_time) # current time
	await interaction.response.send_message(f"I came online at {ct.tm_mon}/{ct.tm_mday}/{ct.tm_year} {ct.tm_hour}:{ct.tm_min}:{ct.tm_sec}, and have been running for {int(time.time() - start_time)} seconds!!!") #noqa

@bot.tree.command(name="say")
@app_commands.describe(thing_to_say="What should I say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
	await interaction.response.send_message(f"{interaction.user.name} said: '{thing_to_say}'") # noqa

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return


	if message.content.startswith(f'{bot.command_prefix}hello'):
		await message.channel.send(f"Hello! I came online at {start_time}!!!")


bot.run(config["DISCORD_TOKEN"])