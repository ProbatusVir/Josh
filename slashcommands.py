import asyncio
import time

import discord
from discord import app_commands, File
import yt

import discord.opus

import declarations
bot = declarations.bot
config = declarations.config

# I'm realizing now that I need a bot class to extend the base.
start_time = declarations.start_time
vc : discord.VoiceClient = None

async def join_voice(interaction : discord.Interaction) -> bool:
	global vc
	if interaction.user.voice is None:
		return False
	channel = interaction.user.voice.channel
	if channel is not None:
		vc = await channel.connect(self_deaf=True)
		return True
	else:
		return False


@bot.tree.command(
	name="uptime",
	description="Find out how long the bot's been running!",
)
async def runtime(interaction : discord.Interaction):
	ct = time.localtime(start_time) # current time
	await interaction.response.send_message(f"I came online at {ct.tm_mon}/{ct.tm_mday}/{ct.tm_year} {ct.tm_hour}:{ct.tm_min}:{ct.tm_sec}, and have been running for {int(time.time() - start_time)} seconds!!!") #noqa

@bot.tree.command(name="say", description="Make me say something!")
@app_commands.describe(thing_to_say="What should I say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
	await interaction.response.send_message(f"{thing_to_say}") # noqa

@bot.tree.command(name="pig-latin", description="Write Pig-Latin!")
@app_commands.describe(phrase="What to pig-latinize")
async def piggy(interaction: discord.Interaction, phrase: str):
	if len(phrase) < 1:
		return
	words = phrase.split()
	new_phrase : str = ""
	for word in words:
		word = word + word[0]
		word = word + ("yay" if "aeiou".find(word[0].lower()) > -1
						   else "ay")
		new_phrase = new_phrase + word[1:] + " "
	await interaction.response.send_message(new_phrase[:-1])




@bot.tree.command(name="download-to-host", description=f'Download a YouTube video to {config["DEVELOPER_USERNAME"]}\'s computer!')
@app_commands.describe(yt_query="Accepts a YT link or a search")
async def download_to_host(interaction: discord.Interaction, yt_link : str):
	if interaction.user.name == config["ANNOYING_FRIEND_USERNAME"]:
		await interaction.response.send_message(f"{config["ANNOYING_FRIEND_NAME"]}STOP!")
		return
	else:
		await interaction.response.send_message("Attempting download....")
		asyncio.create_task(yt.yt_download(yt_link, interaction))

@bot.tree.command(name="sync", description=f'Only for {config["DEVELOPER_USERNAME"]}! Synchronizes slash commands with your server.')
async def sync(interaction : discord.Interaction):
	if interaction.user.name != config["DEVELOPER_USERNAME"]:
		await interaction.response.send_message(f"You are not worthy to use this command {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name}")
		return

	await interaction.response.send_message(f"Attempting to sync slash commands to {interaction.guild}...")
	try:
		synced = await bot.tree.sync()
	except Exception as e:
		await interaction.edit_original_response(content="Failed to sync commands")
		print(f'[ERROR]:\tFailed to sync commands: {e}')
		return
	print(f"Just attempted to sync {len(synced)} commands")
	await interaction.edit_original_response(content=f"Synchronized {len(synced)} slash commands to {interaction.guild}...")

@bot.tree.command(name="search", description="Get the top result of YouTube search")
@app_commands.describe(query="Text to search YouTube for")
async def search(interaction : discord.Interaction, query : str):
	await interaction.response.send_message("Searching the tubes...")
	await yt.yt_search(query, interaction)

@bot.tree.command(name="hop-on", description="Get me in call!")
async def hop_on(interaction : discord.Interaction):
	joined = await join_voice(interaction)
	await interaction.response.send_message("Aight bro, I'm hopping on." if joined else "Bro... you tricked me... you're not even in call...")

@bot.tree.command(name="play-file", description="Play a file! WIP")
async def play_file(interaction : discord.Interaction, file: discord.Attachment):
	joined = await join_voice(interaction)
	if not joined:
		await interaction.response.send_message(f"There was no channel to join.")
		return

	await interaction.response.send_message(f"Playing {file.filename}")
	#vc.play()