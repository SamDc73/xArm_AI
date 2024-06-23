from flask import Flask, request, jsonify
import subprocess
import action_grippers.py as actions

app = Flask(__name__)

@app.route('/rotate', methods=['POST'])
def rotate():
    if request.method == 'POST':
        data = request.get_json()
        degreesX = float(data.get('degreesX'))
        degreesY = float(data.get('degreesY'))
        degreesZ = float(data.get('degreesZ'))

       
        if degreesX is not None and degreesY is not None and degreesZ is not None:
            try:
                actions.rotate_arm(degreesX, degreesY, degreesZ)
                return jsonify({'message': 'Arm rotated successfully'})
            except Exception as e:
                return jsonify({'error': f'Failed to rotate arm: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Degrees of rotation not provided in the request'}), 400

@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        data = request.get_json()
        x = float(data.get('x'))
        y = float(data.get('y'))
        z = float(data.get('z'))

      
        if x is not None and y is not None and z is not None:
            try:
                actions.translate_arm(x, y, z)
                return jsonify({'message': 'Arm translated successfully'})
            except Exception as e:
                return jsonify({'error': f'Failed to translate arm: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Translation values not provided in the request'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
