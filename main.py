# This example requires the 'message_content' intent.
import importlib
import os

import discord

import declarations
import slashcommands

bot = declarations.bot
config = declarations.config

@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Activity(name='Shinji whine', type=discord.ActivityType.listening))
	print(f'We have logged in as {bot.user}')





@bot.event
async def on_message(message : discord.Message):
	if message.author == bot.user:
		return

	if message.content.startswith(f'{bot.command_prefix}hello'):
		await message.channel.send(f"Hello! I came online at {declarations.start_time}!!!")
		return

	if message.content.startswith(f'{bot.command_prefix}reload'):
		await message.channel.send(f"Reloading...")
		commands = bot.tree.get_commands()
		print(f"Removing {len(commands)} commands")
		for i in range(len(commands)):
			bot.tree.remove_command(commands[i].name)

		importlib.reload(slashcommands)
		return

	if message.content.startswith(f'{bot.command_prefix}clear') and message.author.name:
		await message.channel.send(f"Clearing logs...")
		os.system('clear')
		return



bot.run(config["DISCORD_TOKEN"])