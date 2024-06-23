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

document.getElementById('recordButton').addEventListener('click', function() {
    fetch('/start-recording', { method: 'POST' })
        .then(response => response.json())
        .then(data => alert(JSON.stringify(data)))
        .catch(error => alert('Error: ' + error));
});
