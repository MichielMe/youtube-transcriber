import os
import openai
from pytube import YouTube, Playlist
from dotenv import load_dotenv
from pydub import AudioSegment
import subprocess

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
FFMPEG_PATH = r"C:\Users\Michiel\Desktop\CODING\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"

openai.api_key = api_key

# Function to process each video
def process_video(video_url, index):
    print(f"Processing video {index}: {video_url}")

    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_filename = f"audio_{index}.webm"
    audio_stream.download(filename=audio_filename)

    # Convert the audio to WAV format using FFmpeg
    subprocess.run([FFMPEG_PATH, "-i", audio_filename, f"audio_{index}.wav"])

    # Load and split the audio if necessary
    AudioSegment.converter = FFMPEG_PATH
    audio = AudioSegment.from_file(f"audio_{index}.wav", format="wav")
    chunk_length = 2 * 60 * 1000  # 2 minutes in milliseconds

    # Initialize transcript
    full_transcript = ""

    for i in range(0, len(audio), chunk_length):
        chunk = audio[i:i + chunk_length]
        chunk.export(f"audio_chunk_{index}.wav", format="wav")

        with open(f"audio_chunk_{index}.wav", "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        # Using the actual structure of the transcript object based on OpenAI's API response
        transcribed_text = transcript['text']
        full_transcript += transcribed_text + " "

    # Save the full transcript to a text file
    with open(f"transcript_{index}.txt", "w") as f:
        f.write(full_transcript)

    print(f"Transcription for video {index} completed and saved.")
    
    # Delete audio files
    delete_file(f"audio_{index}.webm")
    delete_file(f"audio_{index}.wav")
    for i in range(0, len(audio), chunk_length):
        delete_file(f"audio_chunk_{index}.wav")

# Function to get video URLs from a playlist
def get_video_urls_from_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    return playlist.video_urls

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except OSError as e:
        print(f"Error deleting file {file_path}: {e.strerror}")
        
def combine_transcripts(file_pattern, combined_filename):
    with open(combined_filename, 'w') as outfile:
        # Iterate over the files in the directory
        for filename in os.listdir():
            if filename.startswith(file_pattern) and filename.endswith(".txt"):
                with open(filename, 'r') as infile:
                    outfile.write(infile.read() + "\n\n")
        print(f"All transcripts have been combined into {combined_filename}")


# Main process
def main():
    playlist_url = "https://www.youtube.com/playlist?list=PL4cUxeGkcC9haQlqdCQyYmL_27TesCGPC"  # Replace with the playlist URL
    video_urls = get_video_urls_from_playlist(playlist_url)

    for index, video_url in enumerate(video_urls):
        process_video(video_url, index)
        print(f"Completed video {index + 1} of {len(video_urls)}")
    
    combine_transcripts("transcript_", "combined_transcript.txt")

if __name__ == "__main__":
    main()