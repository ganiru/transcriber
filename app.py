import random
import string
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime, timedelta
from flask_socketio import SocketIO, emit

load_dotenv()
app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)
LLM_MODEL = "whisper-large-v3-turbo"
LLM_TEMPERATURE = 0.2

# Groq client for audio
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('audio_data')
def handle_audio_data(data):
    if data is None:
       emit('transcription_result', {'transcription': "No file was provided"})

    # Assuming data is the audio content
    print("Attempting to transcribe with Groq Whisper...")
    filename = "recording.wav"
    transcription = groq_client.audio.transcriptions.create(
        file=(filename, data),
        model=LLM_MODEL,
        response_format="json",
        language="en",
        temperature=LLM_TEMPERATURE
    )
    print(transcription)
    emit('transcription_result', {'transcription': transcription.text.strip()})



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run(debug=True)