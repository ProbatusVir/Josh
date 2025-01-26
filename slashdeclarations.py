from discord import app_commands

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
	command = slashclasses.PigLatin(phrase, interaction)
	await command.execute()

@bot.tree.command(name="search", description="Get the top result of YouTube search")
@app_commands.describe(query="Text to search YouTube for")
async def search(interaction : discord.Interaction, query : str):
	command = slashclasses.Search(query, interaction)
	await command.execute()

@bot.tree.command(name="play-file", description="Play a file! WIP")
async def play_file(interaction : discord.Interaction, file: discord.Attachment):
	command = slashclasses.PlayFile(file, bot, interaction)
	await command.execute()

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
	command = slashclasses.Stop(bot, interaction)
	await command.execute()

@bot.tree.command(name="pause", description="Pause.")
async def pause(interaction: discord.Interaction):
	command = slashclasses.Pause(bot, interaction)
	await command.execute()

@bot.tree.command(name="resume", description="Resume.")
async def resume(interaction: discord.Interaction):
	command = slashclasses.Resume(bot, interaction)
	await command.execute()

@bot.tree.command(name="clear-queue", description="Clear the queue.")
async def clear(interaction: discord.Interaction):
	command = slashclasses.ClearQueue(interaction)
	await command.execute()

@bot.tree.command(name="skip", description="Skip the current song.")
async def skip(interaction: discord.Interaction):
	command = slashclasses.Skip(bot, interaction)
	await command.execute()

