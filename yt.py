from pytubefix import YouTube
from dotenv import dotenv_values
import pytubefix
from discord import Interaction

config = dotenv_values()



#TODO: Make this return codes to be handled for decoupling.
async def yt_download(link : str, interaction : Interaction, file_format : str ='mp4'):
	try:
		yt = YouTube(link, use_oauth=True)
	except Exception as e:
		await interaction.edit_original_response(content="It appears the link is invalid.")
		print(f"Uh oh. Something went wrong Opening YouTube link!\t{e}")
		return False

	mp4_streams = yt.streams.filter(file_extension=file_format)
	d_video: pytubefix.streams.Stream = mp4_streams[-1] # The last one is the highest resolution

	try:
		d_video.download(output_path=config["YT_SAVE_PATH"], filename=f'{yt.title}.{file_format}', skip_existing=True)
		print(f"Successfully downloaded {yt.title}")
	except Exception as e:
		await interaction.edit_original_response(content="Something went wrong downloading video!")
		print(f"Uh oh! Something went wrong downloading the video!\t{e}")
		return False

	await interaction.edit_original_response(content=f'Successfully downloaded {link} ! We"re testing this message right now.')
	return True




