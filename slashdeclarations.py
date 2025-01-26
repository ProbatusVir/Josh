import asyncio
import collections
import time

import discord
from discord import app_commands
import yt

import discord.opus

import declarations
import slashclasses
bot = declarations.bot
config = declarations.config

# I'm realizing now that I need a bot class to extend the base.
start_time = declarations.start_time

@bot.tree.command(
	name="uptime",
	description="Find out how long the bot's been running!",
)
async def runtime(interaction : discord.Interaction):
	command = slashclasses.RunTime(start_time, interaction)
	await command.execute()

@bot.tree.command(name="say", description="Make me say something!")
@app_commands.describe(thing_to_say="What should I say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
	command = slashclasses.Say(thing_to_say, interaction)
	await command.execute()

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


@bot.tree.command(name="sync", description=f'Only for {config["DEVELOPER_USERNAME"]}! Synchronizes slash commands with your server.')
async def sync(interaction : discord.Interaction):
	command = slashclasses.Sync(bot, interaction)
	await command.execute()

@bot.tree.command(name="search", description="Get the top result of YouTube search")
@app_commands.describe(query="Text to search YouTube for")
async def search(interaction : discord.Interaction, query : str):
	command = slashclasses.Search(query, interaction)
	await command.execute()

@bot.tree.command(name="play-file", description="Play a file! WIP")
async def play_file(interaction : discord.Interaction, file: discord.Attachment):
	joined = await slashclasses.join_voice(interaction)
	if not joined:
		await interaction.response.send_message(f"There was no channel to join.")
		return
	await interaction.response.send_message(f"Joined {vc.channel.name}")
	temp = await file.to_file()
	source = discord.FFmpegOpusAudio(f"{config["YT_SAVE_PATH"]}/viva la taper fade (I USED TO RULE THE WORLD FORTNITE PARODY).mp4")
	vc.play(source)
	await interaction.edit_original_response(content=f"Playing {temp.filename}")

@bot.tree.command(name="play", description="Play.")
@app_commands.describe(yt_query="Accepts a YT link or a search")
async def play(interaction: discord.Interaction, yt_query : str):
	command = slashclasses.Play(yt_query, bot, interaction)
	await command.execute()


@bot.tree.command(name="queue", description="Get the queue.")
async def queue(interaction: discord.Interaction):
	command = slashclasses.Queue(interaction)
	await command.execute()

@bot.tree.command(name="stop", description="Stop something???.")
async def stop(interaction: discord.Interaction):
	command = slashclasses.Stop(interaction)
	await command.execute()

@bot.tree.command(name="pause", description="Pause.")
async def pause(interaction: discord.Interaction):
	command = slashclasses.Pause(interaction)
	await command.execute()

@bot.tree.command(name="resume", description="Resume.")
async def resume(interaction: discord.Interaction):
	command = slashclasses.Resume(interaction)
	await command.execute()

@bot.tree.command(name="clear-queue", description="Clear the queue.")
async def clear(interaction: discord.Interaction):
	await interaction.response.send_message("Deleting queue...")
	slashclasses.Q.clear()

@bot.tree.command(name="skip", description="Skip the current song.")
async def skip(interaction: discord.Interaction):
	command = slashclasses.Skip(interaction)
	await command.execute()

