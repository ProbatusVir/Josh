import io
import re

from pytubefix import YouTube
import pytubefix

from dotenv import dotenv_values
from discord import Interaction

import pytubefix.innertube

config = dotenv_values()

delim : str = '|'

def get_vid_name(video : str) -> str:
	return video.split('/')[-1][:-4]

def find_in_cache(query : str) -> str | None:
	if query.find(delim) != -1:
		return ""
	try:
		cache = io.open(f'{config["YT_SAVE_PATH"]}/cache.txt', 'rt')
	except Exception as e:
		print(e)
		return None #cache probably doesn't exist. Or is just plain inaccessible, either way, not that deep.

	for line in cache:
		if len(line) == 0: # would break parsing
			continue
		values = line.split(delim)
		if values[0] == query:
			return values[1][:-1]
	return None

def write_to_cache(query : str, filename : str):
	cache = io.open(f'{config["YT_SAVE_PATH"]}/cache.txt', 'a')
	cache.write(f'{query}{delim}{filename}\n')



#TODO: Make this return codes to be handled for decoupling.
async def yt_download(query : str, interaction : Interaction, file_format : str = 'mp4') -> str | None:
	query = query.lower().strip()
	cached = find_in_cache(query)
	if cached == "":
		await interaction.edit_original_response(content=f"Invalid character {delim} in query.")
	elif cached is not None:
		path = f"{config["YT_SAVE_PATH"]}/{cached}.{file_format}"
		#path = cached
		print(f"Found cached file: {path}")
		return path
	else:
		print("Did not find a cached file.")

	link_data = re.search("(?:v=|\\/)([0-9A-Za-z_-]{11}).*", query)
	if link_data is not None:
		try:
			yt = YouTube(query, use_oauth=True)
		except Exception as e:
			print(f"[ERROR]: {e}")
			return None
	else:
		yt = await yt_search(query, interaction, command=False)

	mp4_streams = yt.streams.filter(file_extension=file_format)
	d_video: pytubefix.streams.Stream = mp4_streams[-1] # The last one is the highest resolution

	try:
		path = d_video.download(output_path=config["YT_SAVE_PATH"], filename=f'{yt.title}.{file_format}', skip_existing=True).replace('\\', '/')
		print(f"Successfully downloaded {yt.title}")
	except Exception as e:
		print(f"Uh oh! Something went wrong downloading the video!\t{e}")
		return None

	write_to_cache(query, get_vid_name(path))
	return path

async def yt_search(query : str, interaction : Interaction, command : bool = True) -> YouTube:
	search = pytubefix.Search(query=query, client='WEB')
	results : dict = search.fetch_and_parse()[0]
	first_value : YouTube = next(iter(results.values()))[0]

	if command:
		await interaction.edit_original_response(content=f'Found: {first_value.title}')
	return first_value




