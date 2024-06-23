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
        console.log('Start recording button clicked');
        
        // Request microphone permission
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                console.log('Microphone permission granted');
                startRecordingButton.textContent = 'Start Recording';
                startRecordingButton.disabled = false;
                
                // Add a new click event listener for actual recording
                startRecordingButton.onclick = function() {
                    console.log('Starting recording');
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();

                    audioChunks = [];
                    mediaRecorder.addEventListener("dataavailable", event => {
                        audioChunks.push(event.data);
                        console.log('Audio chunk added');
                    });

                    startRecordingButton.disabled = true;
                    stopRecordingButton.disabled = false;
                    console.log('Recording started');
                };
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                let errorMessage = 'Error accessing microphone: ';
                if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                    errorMessage += 'No microphone found. Please ensure a microphone is connected and granted permission.';
                } else if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                    errorMessage += 'Permission to access the microphone was denied. Please grant permission and try again.';
                } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                    errorMessage += 'Unable to access the microphone. It may be in use by another application.';
                } else {
                    errorMessage += error.message || 'Unknown error occurred.';
                }
                alert(errorMessage);
                transcriptionDiv.textContent = errorMessage;
            });
    });

    // Change the initial text of the start button
    startRecordingButton.textContent = 'Request Microphone Permission';

    stopRecordingButton.addEventListener('click', function() {
        console.log('Stop recording button clicked');
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.addEventListener("stop", () => {
                console.log('MediaRecorder stopped');
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'audio.wav');

                console.log('Sending audio to server');
                fetch('/upload-audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Server response:', data);
                    if (data.status === 'success') {
                        transcriptionDiv.textContent = data.transcript || 'No transcription available';
                    } else {
                        transcriptionDiv.textContent = 'Error: ' + data.message;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    transcriptionDiv.textContent = 'Error: ' + error.message;
                });

                startRecordingButton.disabled = false;
                stopRecordingButton.disabled = true;
            });
        } else {
            console.log('MediaRecorder is not active');
        }
    });

    console.log('Audio recording script loaded');
});
