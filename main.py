import os
import openai
from pytube import YouTube
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

video_url = "https://www.youtube.com/watch?v=cdiD-9MMpb0&t=10378s"
yt = YouTube(video_url)
audio_stream = yt.streams.filter(only_audio=True).first()
audio_stream.download(filename="audio")

with open("audio", "rb") as audio_file:
    transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)
transcribed_text = transcript['data']['text']

print("Transcibed Text:", transcribed_text)
with open("transcript.txt", "w") as text_file:
    text_file.write(transcribed_text)