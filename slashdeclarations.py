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


def get_vid_name(video : str) -> str:
	return video.split('\\')[-1][:-4]

async def join_voice(interaction : discord.Interaction) -> bool:
	if len(bot.voice_clients): # This doesn't scale, btw. I could make a thing that looks for the guild and then sees what channel he's in, if there's a hit.
		declarations.vc = bot.voice_clients[0]
		if __debug__:
			print("Bot's already in call.")
		return True
	if interaction.user.voice is None:
		return False
	channel = interaction.user.voice.channel
	if channel is not None:
		declarations.vc = await channel.connect(self_deaf=True)
		return True
	else:
		return False

#Play the music
async def play_music(interaction : discord.Interaction) -> None:
	while slashclasses.vc.is_playing():
		await asyncio.sleep(1)



	def after(e : Exception | None) ->  None:
		if e is not None:
			print(f'[ERROR] Unexpected: {e}')
		slashclasses.Q.popleft()

	while len(slashclasses.Q) > 0:
		song = slashclasses.Q[0]
		await interaction.edit_original_response(content=f'Now playing {get_vid_name(song)}')
		source = discord.FFmpegOpusAudio(song)
		slashclasses.vc.play(source, signal_type='music', after=after )
		while slashclasses.vc.is_playing() or paused:
			await asyncio.sleep(1)
		await interaction.edit_original_response(content=f"Finished {get_vid_name(song)}")
	await interaction.edit_original_response(content="Finished queue!")
	await slashclasses.vc.disconnect()
	vc = None
	playing = None

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
	joined = await join_voice(interaction)
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
	# join logic
	joined = await join_voice(interaction)
	if not joined:
		await interaction.response.send_message("There was no channel to join.")
		return
	#look for video B)
	await interaction.response.send_message("Looking for the video...")
	slashclasses.Q.append(await yt.yt_download(yt_query, interaction))
	# since this runs in a loop later down, only the original function call must persist so as to not interrupt
	if len(slashclasses.Q) > 1:
		await interaction.edit_original_response(content=f'"{get_vid_name(Q[len(Q) - 1])}" queued!')
		return

	asyncio.create_task(play_music(interaction))


@bot.tree.command(name="queue", description="Get the queue.")
async def queue(interaction: discord.Interaction):
	if len(slashclasses.Q) == 0:
		await interaction.response.send_message("Nothing's playing!")
		return
	capture = slashclasses.Q.copy()
	qrep = ""
	for i, e in enumerate(capture):
		qrep += f"{i + 1}. {get_vid_name(e)}\n"
	await interaction.response.send_message(qrep)

@bot.tree.command(name="stop", description="Stop something???.")
async def stop(interaction: discord.Interaction):
	if slashclasses.vc is not None:
		if slashclasses.vc.is_playing():
			await interaction.response.send_message("Stopping.")
			slashclasses.vc.stop()
		else:
			await interaction.response.send_message("Bruh, literally nothing is playing.")
			return
	else:
		await interaction.response.send_message("Bruh, I'm not even in call???")

@bot.tree.command(name="pause", description="Pause.")
async def pause(interaction: discord.Interaction):
	global paused
	if slashclasses.vc is not None:
		if slashclasses.vc.is_playing():
			await interaction.response.send_message("Pausing.")
			paused = True
			slashclasses.vc.pause()
		else:
			await interaction.response.send_message("Bruh, literally nothing is playing.")
			return
	else:
		await interaction.response.send_message("Bruh, I'm not even in call???")

@bot.tree.command(name="resume", description="Resume.")
async def resume(interaction: discord.Interaction):
	global paused
	if slashclasses.vc is not None:
		await interaction.response.send_message("Resuming...")
		paused = False
		slashclasses.vc.resume()
	else:
		await interaction.response.send_message("Bruh, I'm not even in call???")

@bot.tree.command(name="clear-queue", description="Clear the queue.")
async def clear(interaction: discord.Interaction):
	await interaction.response.send_message("Deleting queue...")
	slashclasses.Q.clear()

@bot.tree.command(name="skip", description="Skip the current song.")
async def skip(interaction: discord.Interaction):
	await interaction.response.send_message("Skipping current song.")
	if slashclasses.vc is not None:
		if slashclasses.vc.is_playing():
			slashclasses.vc.stop()
		else:
			await interaction.edit_original_response(content="Bruh, literally nothing is playing.")
	else:
		await interaction.edit_original_response(content="Bruh, I'm not even in call???")

