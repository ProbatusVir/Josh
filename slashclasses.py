from abc import ABC, abstractmethod
from discord import Interaction, VoiceClient
from collections import deque
import time

from discord.ext.commands import Bot

import declarations
import yt

paused = False
vc : VoiceClient | None = None
Q : deque[str] = deque()

#The base class
class SlashCommand(ABC):
	@abstractmethod
	async def execute(self):
		pass

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

class Search(SlashCommand):
	def __init__(self, query : str, interaction : Interaction):
		self.interaction = interaction
		self.query = query

	async def execute(self):
		await self.interaction.response.send_message("Searching the tubes...") #noqa
		await yt.yt_search(self.query, self.interaction)

class Sync(SlashCommand):
	def __init__(self, bot : Bot,interaction : Interaction):
		self.interaction = interaction
		self.bot = bot

	async def execute(self):
		if self.interaction.user.name != declarations.config["DEVELOPER_USERNAME"]:
			await self.interaction.response.send_message(
				f"You are not worthy to use this command {self.interaction.user.nick if self.interaction.user.nick is not None else self.interaction.user.global_name}")
			return

		await self.interaction.response.send_message(f"Attempting to sync slash commands to {self.interaction.guild}...")
		try:
			synced = await self.bot.tree.sync()
		except Exception as e:
			await self.interaction.edit_original_response(content="Failed to sync commands")
			print(f'[ERROR]:\tFailed to sync commands: {e}')
			return
		print(f"Just attempted to sync {len(synced)} commands")
		await self.interaction.edit_original_response(
			content=f"Synchronized {len(synced)} slash commands to {self.interaction.guild}...")
