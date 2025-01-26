import asyncio
from abc import ABC, abstractmethod
from discord import Interaction, VoiceClient, FFmpegOpusAudio, Attachment, Message
from collections import deque
import time
from enum import Enum

from discord.ext.commands import Bot

import declarations
import yt

#TODO: I'm sensing another rewrite...

paused = False
def vc(bot : Bot) -> VoiceClient | None:
	if len(bot.voice_clients) > 0:
		return bot.voice_clients[0]

Q : deque[str] = deque()

config = declarations.config

#TODO: Make an enum file??
class PlayingState(Enum):
	Playing = 1
	NotPlaying = 2
	Absent = 3


#The base class
class SlashCommand(ABC):
	@abstractmethod
	async def execute(self):
		pass

def in_call(bot : Bot) -> PlayingState:
	voice = vc(bot)
	if voice is not None:
		if voice.is_playing():
			return PlayingState.Playing
		else:
			return PlayingState.NotPlaying
	else:
		return PlayingState.Absent

def get_vid_name(video : str) -> str:
	return video.split('/')[-1][:-4]

async def join_voice(bot : Bot, interaction : Interaction) -> bool:
	if len(bot.voice_clients): # This doesn't scale, btw. I could make a thing that looks for the guild and then sees what channel he's in, if there's a hit.
		if __debug__:
			print("Bot's already in call.")
		return True
	if interaction.user.voice is None:
		return False
	channel = interaction.user.voice.channel
	if channel is not None:		#Already mentioned once, but this is pretty bad. I need a reference to the bot.voice_clients[index] for this to be good.
		bot.voice_clients[0] = await channel.connect(self_deaf=True)
		return True
	else:
		return False

#Play the music
async def play_music(bot : Bot, interaction : Interaction) -> None:
	voice = vc(bot)
	global Q
	while voice.is_playing():
		await asyncio.sleep(1)

	def after(e : Exception | None) ->  None:
		if e is not None:
			print(f'[ERROR] Unexpected: {e}')

	while len(Q) > 0:
		song = Q[0]
		await interaction.edit_original_response(content=f'Now playing {get_vid_name(song)}')
		source = FFmpegOpusAudio(song)
		voice.play(source, signal_type='music', after=after )
		Q.popleft()
		while voice.is_playing() or paused:
			await asyncio.sleep(1)
		await interaction.edit_original_response(content=f"Finished {get_vid_name(song)}")
	await interaction.edit_original_response(content="Finished queue!")
	await voice.disconnect()


# noinspection PyUnresolvedReferences
class RunTime(SlashCommand):
	def __init__(self, start_time, interaction : Interaction):
		self.interaction = interaction
		self.start_time = start_time

	async def execute(self):
		ct = time.localtime(self.start_time)  # current time
		await self.interaction.response.send_message(
			f"I came online at {ct.tm_mon}/{ct.tm_mday}/{ct.tm_year} {ct.tm_hour}:{ct.tm_min}:{ct.tm_sec}, and have been running for {int(time.time() - self.start_time)} seconds!!!")  # noqa

class Say(SlashCommand):
	def __init__(self, thing_to_say : str,interaction : Interaction):
		self.interaction = interaction
		self.thing_to_say = thing_to_say

	async def execute(self):
		await self.interaction.response.send_message(f"{self.thing_to_say}")  # noqa


# noinspection PyUnresolvedReferences
class Search(SlashCommand):
	def __init__(self, query : str, interaction : Interaction):
		self.interaction = interaction
		self.query = query

	async def execute(self):
		await self.interaction.response.send_message("Searching the tubes...") #noqa
		await yt.yt_search(self.query, self.interaction)


# noinspection PyUnresolvedReferences
class Sync(SlashCommand):
	def __init__(self, bot : Bot,interaction : Interaction | Message):
		self.interaction = interaction
		self.bot = bot

	async def execute(self):
		username = self.interaction.user.name if self.interaction is Interaction else self.interaction.author.name
		if username != config["DEVELOPER_USERNAME"]:
			display_name = self.interaction.user.nick if self.interaction is Interaction else self.interaction.author.nick
			fallback_name = self.interaction.user.global_name if self.interaction is Interaction else self.interaction.author.global_name
			message = f"You are not worthy to use this command {display_name if display_name is not None else fallback_name}"
			await self.interaction.channel.send(message)
			return

		attempt_message = f"Attempting to sync slash commands to {self.interaction.guild}..."
		if self.interaction is Interaction:
			await self.interaction.response.send_message(attempt_message)
		else:
			pass #await self.interaction.reply(attempt_message) # we don't really need to reply twice to a message
		try:
			synced = await self.bot.tree.sync()
		except Exception as e:
			message : str = "Failed to sync commands"
			if self.interaction is Interaction:
				await self.interaction.edit_original_response(content=message)
			else:
				await self.interaction.reply(content=message)
			print(f'[ERROR]:\tFailed to sync commands: {e}')
			return
		print(f"Just attempted to sync {len(synced)} commands")
		message = f"Synchronized {len(synced)} slash commands to {self.interaction.guild}..."
		if self.interaction is Interaction:
			await self.interaction.edit_original_response(content=message)
		else:
			await self.interaction.reply(content=message)


# noinspection PyUnresolvedReferences
class Skip(SlashCommand):
	def __init__(self, bot : Bot, interaction : Interaction):
		self.interaction = interaction
		self.bot = bot

	async def execute(self):
		voice = vc(self.bot)
		await self.interaction.response.send_message("Skipping current song.")
		if voice is not None:
			if voice.is_playing():
				voice.stop()
			else:
				await self.interaction.edit_original_response(content="Bruh, literally nothing is playing.")
		else:
			await self.interaction.edit_original_response(content="Bruh, I'm not even in call???")


# noinspection PyUnresolvedReferences
class Play(SlashCommand):
	def __init__(self, query, bot : Bot, interaction : Interaction):
		self.interaction = interaction
		self.bot = bot
		self.query = query

	async def execute(self):
		global Q
		voice = vc(self.bot)
		# join logic
		joined = await join_voice(self.bot, self.interaction)
		if not joined:
			await self.interaction.response.send_message("There was no channel to join.")
			return
		#look for video B)
		await self.interaction.response.send_message("Looking for the video...")
		Q.append(await yt.yt_download(self.query, self.interaction))
		# since this runs in a loop later down, only the original function call must persist so as to not interrupt
		if voice.is_playing():
			await self.interaction.edit_original_response(content=f'"{get_vid_name(Q[len(Q) - 1])}" queued!')
			return
		asyncio.create_task(play_music(self.bot, self.interaction))


# noinspection PyUnresolvedReferences
class Queue(SlashCommand):
	def __init__(self, interaction : Interaction):
		self.interaction = interaction

	async def execute(self):
		global Q
		if len(Q) == 0:
			await self.interaction.response.send_message("Nothing's queued!")
			return
		capture = Q.copy()
		qrep = ""
		for i, e in enumerate(capture):
			qrep += f"{i + 1}. {get_vid_name(e)}\n"
		await self.interaction.response.send_message(qrep)


# noinspection PyUnresolvedReferences
class Stop(SlashCommand):
	def __init__(self, bot : Bot, interaction : Interaction):
		self.interaction = interaction
		self.bot = bot

	async def execute(self):
		voice = vc(self.bot)
		global paused
		global Q
		if voice is not None:
			if vc.is_playing():
				await self.interaction.response.send_message("Stopping.")
				Q.clear()
				voice.stop()
			else:
				await self.interaction.response.send_message("Bruh, literally nothing is playing.")
				return
		else:
			await self.interaction.response.send_message("Bruh, I'm not even in call???")


# noinspection PyUnresolvedReferences
class Pause(SlashCommand):
	def __init__(self, bot : Bot, interaction : Interaction):
		self.interaction = interaction
		self.bot = bot

	async def execute(self):
		global paused
		voice = vc(self.bot)
		if voice is not None:
			if vc.is_playing():
				await self.interaction.response.send_message("Pausing.")
				paused = True
				voice.pause()
			else:
				await self.interaction.response.send_message("Bruh, literally nothing is playing.")
				return
		else:
			await self.interaction.response.send_message("Bruh, I'm not even in call???")


# noinspection PyUnresolvedReferences
class Resume(SlashCommand):
	def __init__(self, bot : Bot, interaction : Interaction):
		self.interaction = interaction
		self.bot = bot

	async def execute(self):
		global paused
		voice = vc(self.bot)
		if voice is not None:
			await self.interaction.response.send_message("Resuming...")
			paused = False
			voice.resume()
		else:
			await self.interaction.response.send_message("Bruh, I'm not even in call???")


# noinspection PyUnresolvedReferences
class PigLatin(SlashCommand):
	def __init__(self, phrase : str, interaction : Interaction):
		self.interaction = interaction
		self.phrase = phrase

	async def execute(self):
		if len(self.phrase) < 1:
			return
		words = self.phrase.split()
		new_phrase: str = ""
		for word in words:
			word = word + word[0]
			word = word + ("yay" if "aeiou".find(word[0].lower()) > -1
						   else "ay")
			new_phrase = new_phrase + word[1:] + " "
		await self.interaction.response.send_message(new_phrase[:-1])


# noinspection PyUnresolvedReferences
class PlayFile(SlashCommand):
	def __init__(self, attachment : Attachment, bot : Bot, interaction : Interaction):
		self.interaction = interaction
		self.attachment = attachment
		self.bot = bot

	async def execute(self):
		joined = await join_voice(self.bot, self.interaction)
		voice = vc(self.bot)
		if not joined:
			await self.interaction.response.send_message(f"There was no channel to join.")
			return
		await self.interaction.response.send_message(f"Joined {vc.channel.name}")
		temp = await self.attachment.to_file()
		source = FFmpegOpusAudio(f"{config["YT_SAVE_PATH"]}/viva la taper fade (I USED TO RULE THE WORLD FORTNITE PARODY).mp4")
		voice.play(source)
		await self.interaction.edit_original_response(content=f"Playing {temp.filename}")


# noinspection PyUnresolvedReferences
class ClearQueue(SlashCommand):
	def __init__(self, interaction : Interaction):
		self.interaction = interaction

	async def execute(self):
		global Q
		if len(Q) == 0:
			await self.interaction.response.send_message("Nothing's queued!")
			return
		Q.clear()
		await self.interaction.response.send_message("Queue cleared.")

