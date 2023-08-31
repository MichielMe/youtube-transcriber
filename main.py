import os
import openai
from pytube import YouTube
from dotenv import load_dotenv
from pydub import AudioSegment
import subprocess

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

video_url = "https://www.youtube.com/watch?v=5xbADDvciko"
yt = YouTube(video_url)
audio_stream = yt.streams.filter(only_audio=True).first()
audio_stream.download(filename="audio.webm")

# Convert the audio to WAV format using FFmpeg
subprocess.run(["ffmpeg", "-i", "audio.webm", "audio.wav"])

# Step 2: Check and Split Audio if Necessary
audio = AudioSegment.from_file("audio.wav", format="wav")


chunk_length = 2 * 60 * 1000  # 10 minutes in milliseconds
# Step 4: Initialize Transcript
full_transcript = ""

for i in range(0, len(audio), chunk_length):
    chunk = audio[i:i+chunk_length]
    chunk.export("audio_chunk.wav", format="wav")
    
    with open("audio_chunk.wav", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
    # Using the actual structure of the transcript object based on OpenAI's API response
    transcribed_text = transcript['text']
    
    full_transcript += transcribed_text + " "

# Optional: Save the full transcript to a text file
with open("full_transcript.txt", "w") as f:
    f.write(full_transcript)

# Done!
print("Transcription Complete. The full transcript has been saved to 'full_transcript.txt'.")