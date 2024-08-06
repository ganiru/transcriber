document.addEventListener('DOMContentLoaded', () => {
    //const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
/* 
    themeToggle.addEventListener('change', () => {
        if (themeToggle.checked) {
            html.classList.remove('light');
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
            html.classList.add('light');
        }
    }); */

    const recordButton = document.getElementById('recordButton');
    const micIcon = document.getElementById('micIcon');
    const buttonText = document.getElementById('buttonText');
    const transcriptionOutput = document.getElementById('transcriptionOutput');
    transcriptionOutput.setAttribute('style', 'white-space: pre-wrap;');
    const recordingStatus = document.getElementById('recordingStatus');
    let mediaRecorder;
    let audioChunks = [];
    let allStreams;

    recordButton.addEventListener('click', toggleRecording);

    async function toggleRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            stopRecording();
        } else {
            try {
                await startRecording();
            } catch (error) {
                console.error('Error starting recording:', error);
                alert('Failed to start recording. Please check your microphone permissions.');
            }
        }
    }

    async function startRecording() {
        console.log('Attempting to start recording...');
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        allStreams = stream;
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = sendAudioToServer;
        mediaRecorder.start();
        console.log('Recording started');
        recordButton.classList.remove('bg-blue-500', 'hover:bg-blue-600');
        recordButton.classList.add('bg-red-500', 'hover:bg-red-600');
        buttonText.textContent = 'Stop';
        micIcon.classList.add('animate-pulse');
        recordingStatus.classList.remove('hidden');
    }

    function stopRecording() {
        console.log('Stopping recording...');
        mediaRecorder.stop();
        // clear the streams
        allStreams.getTracks().forEach(track => track.stop());
        recordButton.classList.remove('bg-red-500', 'hover:bg-red-600');
        recordButton.classList.add('bg-blue-500', 'hover:bg-blue-600');
        buttonText.textContent = 'Record';
        micIcon.classList.remove('animate-pulse');
        recordingStatus.classList.add('hidden');
    }

    function sendAudioToServer() {
        console.log('Sending audio to server...');
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioChunks = [];

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        fetch('/transcribe', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Received response:', data);
            transcriptionOutput.textContent += data.transcription + '\r\n';
        })
        .catch(error => {
            console.error('Error:', error);
            transcriptionOutput.textContent = 'An error occurred during transcription.';
        });
    }

    const copyButton = document.getElementById('copyButton');
    const downloadButton = document.getElementById('downloadButton');
    const clearButton = document.getElementById('clearButton');

    copyButton.addEventListener('click', copyToClipboard);
    downloadButton.addEventListener('click', downloadAsText);
    clearButton.addEventListener('click', clearTranscription);

    function copyToClipboard() {
        const text = transcriptionOutput.textContent;
        navigator.clipboard.writeText(text).then(() => {
            alert('Transcription copied to clipboard!');
        }).catch(err => {
            console.error('Error copying text: ', err);
        });
    }

    function downloadAsText() {
        const text = transcriptionOutput.textContent;
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transcription.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function clearTranscription() {
        transcriptionOutput.textContent = '';
    }
});