import os
import time
import threading
import json
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, vfx
import yt_dlp
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Загружаем переменные из .env
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DOWNLOAD_FOLDER = "downloads"
EDITED_FOLDER = "edited"

# Создание папок
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(EDITED_FOLDER, exist_ok=True)

def get_youtube_trending(api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode="US",
        maxResults=5
    )
    response = request.execute()
    return [f"https://www.youtube.com/watch?v={item['id']}" for item in response['items']]

def download_video(url):
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ Видео скачано: {url}")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")

def edit_video(video_path):
    try:
        clip = VideoFileClip(video_path)
        clip = clip.fx(vfx.mirror_x)
        new_path = f"{EDITED_FOLDER}/edited_{os.path.basename(video_path)}"
        clip.write_videofile(new_path, codec='libx264', audio_codec='aac')
        print(f"✅ Видео отредактировано: {new_path}")
        return new_path
    except Exception as e:
        print(f"❌ Ошибка редактирования: {e}")
        return None

def run_bot():
    print("🔍 Поиск трендовых видео...")
    trending_videos = get_youtube_trending(YOUTUBE_API_KEY)
    for video_url in trending_videos:
        download_video(video_url)
    for file in os.listdir(DOWNLOAD_FOLDER):
        video_path = os.path.join(DOWNLOAD_FOLDER, file)
        edit_video(video_path)
    print("✅ Все задачи выполнены!")

def start_bot_thread():
    thread = threading.Thread(target=run_bot)
    thread.start()

if __name__ == "__main__":
    start_bot_thread()
