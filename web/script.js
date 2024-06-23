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

let mediaRecorder;
let audioChunks = [];

document.getElementById('startRecording').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            audioChunks = [];
            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            document.getElementById('startRecording').disabled = true;
            document.getElementById('stopRecording').disabled = false;
        })
        .catch(error => console.error('Error accessing microphone:', error));
});

document.getElementById('stopRecording').addEventListener('click', function() {
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
                document.getElementById('transcription').textContent = data.transcript || 'No transcription available';
            })
            .catch(error => console.error('Error:', error));

            document.getElementById('startRecording').disabled = false;
            document.getElementById('stopRecording').disabled = true;
        });
    }
});
