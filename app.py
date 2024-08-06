from flask import Flask, render_template, request, jsonify
import os
from groq import Groq

app = Flask(__name__, static_folder='static')

# Groq client for audio
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    # Get the audio file from the request
    audio_file = request.files['audio']
    # Read the file content
    audio_content = audio_file.read()

    # Transcribe audio using Whisper
    print("Attempting to transcribe with Groq Whisper...")
    filename = "recording.wav"
    print(">>>Audio file info:", audio_file)
    transcription = groq_client.audio.transcriptions.create(
        file=(filename, audio_content),
        model="whisper-large-v3",
    #    prompt="Specify context or spelling",  # Optional
        response_format="json",  # Optional
        language="en",  # Optional
        temperature=0.2  # Optional
    )
    print(transcription)
    print("ChatGroq processing successful")

    return jsonify({"transcription": transcription.text})


if __name__ == '__main__':
    app.run(debug=True)