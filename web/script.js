function rotateArm() {
    const degreesX = document.getElementById('degreesX').value;
    const degreesY = document.getElementById('degreesY').value;
    const degreesZ = document.getElementById('degreesZ').value;
    fetch('/rotate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ degreesX, degreesY, degreesZ })
    }).then(response => response.json())
      .then(data => alert(JSON.stringify(data)))
      .catch(error => alert('Error: ' + error));
}

function translateArm() {
    const x = document.getElementById('translateX').value;
    const y = document.getElementById('translateY').value;
    const z = document.getElementById('translateZ').value;
    fetch('/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ x, y, z })
    }).then(response => response.json())
      .then(data => alert(JSON.stringify(data)))
      .catch(error => alert('Error: ' + error));
}

function controlGripper() {
    const action = document.getElementById('gripperAction').value;
    const force = document.getElementById('gripperForce').value;
    fetch('/gripper', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action, force })
    }).then(response => response.json())
      .then(data => alert(JSON.stringify(data)))
      .catch(error => alert('Error: ' + error));
}

document.addEventListener('DOMContentLoaded', (event) => {
    let mediaRecorder;
    let audioChunks = [];

    const startRecordingButton = document.getElementById('startRecording');
    const stopRecordingButton = document.getElementById('stopRecording');
    const transcriptionDiv = document.getElementById('transcription');

    startRecordingButton.addEventListener('click', function() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();

                audioChunks = [];
                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                startRecordingButton.disabled = true;
                stopRecordingButton.disabled = false;
            })
            .catch(error => console.error('Error accessing microphone:', error));
    });

    stopRecordingButton.addEventListener('click', function() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'audio.wav');

                fetch('/upload-audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Server response:', data);
                    transcriptionDiv.textContent = data.transcript || 'No transcription available';
                })
                .catch(error => console.error('Error:', error));

                startRecordingButton.disabled = false;
                stopRecordingButton.disabled = true;
            });
        }
    });

    console.log('Audio recording script loaded');
});
