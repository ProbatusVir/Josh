from pytubefix import YouTube, Search
import pytubefix

from dotenv import dotenv_values
from discord import Interaction

import pytubefix.innertube

config = dotenv_values()

#TODO: Make this return codes to be handled for decoupling.
async def yt_download(link : str, interaction : Interaction, file_format : str ='mp4') -> str | None:
	try:
		yt = YouTube(link, use_oauth=True)
	except Exception as e:
		print(f"[ERROR]: Probably malformed link. Attempting to query: {e}")
		yt = await yt_search(link, interaction, command=False)

	mp4_streams = yt.streams.filter(file_extension=file_format)
	d_video: pytubefix.streams.Stream = mp4_streams[-1] # The last one is the highest resolution

	try:
		path = d_video.download(output_path=config["YT_SAVE_PATH"], filename=f'{yt.title}.{file_format}', skip_existing=True)
		print(f"Successfully downloaded {yt.title}")
	except Exception as e:
		await interaction.edit_original_response(content="Something went wrong downloading video!")
		print(f"Uh oh! Something went wrong downloading the video!\t{e}")
		return None

	await interaction.edit_original_response(content=f'Successfully downloaded {yt.title} !')
	return path

async def yt_search(query : str, interaction : Interaction, command : bool = True) -> YouTube:
	search = pytubefix.Search(query=query, client='WEB')
	results : dict = search.fetch_and_parse()[0]
	first_value : YouTube = next(iter(results.values()))[0]

	if command:
		await interaction.edit_original_response(content=f'Found: {first_value.title}')
	return first_value




