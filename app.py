from flask import Flask, render_template, request, send_file
import os
from gtts import gTTS
import requests
from moviepy.editor import *

app = Flask(__name__)
PEXELS_API_KEY = "BYJhC4q8NcyBQPVYjYuZP8faFbOwPV1MPiUmPy1eI69LJfS5oXZfZ1r1"
PEXELS_URL = "https://api.pexels.com/videos/search"
HEADERS = {"Authorization": PEXELS_API_KEY}

def search_pexels_video(query):
    params = {"query": query, "per_page": 1}
    res = requests.get(PEXELS_URL, headers=HEADERS, params=params)
    data = res.json()
    if data['videos']:
        return data['videos'][0]['video_files'][0]['link']
    return None

def download_file(url, path):
    r = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

def generate_audio(text, path):
    tts = gTTS(text)
    tts.save(path)

def merge_video_audio(video_path, audio_path, output_path):
    video = VideoFileClip(video_path).subclip(0, 10)
    audio = AudioFileClip(audio_path)
    final = video.set_audio(audio)
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        keyword = request.form['keyword']

        video_url = search_pexels_video(keyword)
        if not video_url:
            return "لم يتم العثور على فيديو مناسب."

        video_path = 'static/output/video.mp4'
        audio_path = 'static/output/audio.mp3'
        output_path = 'static/output/final_video.mp4'

        download_file(video_url, video_path)
        generate_audio(text, audio_path)
        merge_video_audio(video_path, audio_path, output_path)

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')