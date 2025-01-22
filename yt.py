from pytubefix import YouTube
from dotenv import dotenv_values
import pytubefix

config = dotenv_values()

async def yt_download(link : str, file_format : str ='mp4'):
	try:
		yt = YouTube(link, use_oauth=True)
	except Exception as e:
		print(f"Uh oh. Something went wrong Opening YouTube link!\t{e}")
		return False

	mp4_streams = yt.streams.filter(file_extension=file_format)
	d_video: pytubefix.streams.Stream = mp4_streams[-1] # The last one is the highest resolution

	try:
		d_video.download(output_path=config["YT_SAVE_PATH"], filename=f'{yt.title}.{file_format}', skip_existing=True)
		print(f"Successfully downloaded {yt.title}")
	except Exception as e:
		print(f"Uh oh! Something went wrong downloading the video!\t{e}")
		return False
	return True




