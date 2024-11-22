import random
import string
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime, timedelta
import requests

load_dotenv()
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
    transcription = groq_client.audio.transcriptions.create(
        file=(filename, audio_content),
        model="whisper-large-v3",
    #    prompt="Specify context or spelling",  # Optional
        response_format="json",  # Optional
        language="en",  # Optional
        temperature=0.2  # Optional
    )
    print(transcription)
    # print("ChatGroq processing successful")

    return jsonify({"transcription": transcription.text.strip()})

@app.route('/request-code')
def request_code_page():
    return render_template('request-code.html')

@app.route('/request-code', methods=['POST'])
def request_code():
    data = request.json
    email = data.get('email')
    name = data.get('name', '')
    notify = data.get('notify', False)

    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400

    code = ''.join(random.choices(string.digits, k=6))
    # set the variable 'expires' to the current date + 24 hours in the format 'MM/DD/YYYY'
    expires = (datetime.now() + timedelta(hours=24)).strftime('%m/%d/%Y')

    payload = {
        "app_name": "transcribex",
        "name": name,
        "email": email,
        "code": code,
        "expires": expires,
        "notify_release": notify
    }

    try:
        url = os.getenv('N8N_SEND_CODE_URL')
        response = requests.post(
            url,
            json=payload
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending data to Make.com: {e}")
        return jsonify({"success": False, "message": "An error occurred while processing your request."}), 500

    return jsonify({
        "success": True,
        "message": "Your access code has been sent. Please check your email."
    })

@app.route('/login', methods=['POST'])
def login():
    # This route should be updated to validate the code against the Make.com endpoint
    # For now, we'll return a placeholder response
    data = request.json
    code = data.get('accessCode')
    if not code:
        return jsonify({"success": False, "message": "Code is required."}), 400
    # Add code validation logic here
    payload = {
        "code": code
    }
    try:
        url = os.getenv('N8N_GET_CODES_URL')
        response = requests.post(
            url,
            json=payload
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending data to Make.com: {e}")
        return jsonify({"success": False, "message": "An error occurred while processing your request."}), 500
    
    if response.status_code == 200:
        response_data = response.json()
        expiration_date = response_data[0].get('expires')
        print("Data returned", response_data)
        print("Expiration date", expiration_date)
        # Check if the expiration date is in the past, bearing in mind that the date is in the format 'YYYY-MM-DD'
        # and the datetime.now() returns the current date in the format 'YYYY-MM-DD'
        # so we need to convert the expiration date to a datetime object and compare it to the current date
        # and if the expiration date is in the past, return an error

        if expiration_date and datetime.strptime(expiration_date, '%Y-%m-%d') < datetime.now():
            return jsonify({"success": False, "message": "Code has expired"}), 400
        print(">>> TIme left", datetime.strptime(expiration_date, '%Y-%d-%m') - datetime.now())

        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid code"}), 400
    # Add code validation logic here


@app.route('/login')
def login_page():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)