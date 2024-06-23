from flask import Flask, request, jsonify
import subprocess
import action_grippers.py as actions
import argparse

app = Flask(__name__, static_folder='web/static', template_folder='web')



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
        
        
@app.route('/gripper', methods=['POST'])
def gripper():
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')
        force = float(data.get('force'))

        if action is not None and force is not None:
            try:
                actions.gripper_arm(action, force)
                return jsonify({'message': 'Arm gripper action completed successfully'})
            except Exception as e:
                return jsonify({'error': f'Failed to perform gripper action: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Gripper action or force not provided in the request'}), 400

def get_utterance():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            # Adjust for ambient noise and set a higher threshold
            print("Adjusting for ambient noise. Please wait...")
            r.adjust_for_ambient_noise(source, duration=3)
            print("Say something!")
            audio = r.listen(source, timeout=60, phrase_time_limit=5)
            print("Processing...")
            # Simulate processing here
        except Exception as e:
            print(f"Error: {str(e)}")  # Customize or handle logging
            return "Device not connected or audio setup issue."

@app.route('/start-recording', methods=['POST'])
def start_recording():
    result = get_utterance()
    if "Error" in result:
        return jsonify({'status': 'error', 'message': result}), 500
    return jsonify({'status': 'success', 'message': 'Recording started successfully', 'transcript': result}), 200


if __name__ == '__main__':
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Start the Flask web server for the Robotic Arm Controller.")
    parser.add_argument('-W', '--web', action='store_true', help='Start the web server')
    
    args = parser.parse_args()

    if args.web:
        port = 5000
        os.system('clear')
        print("\n===============================================================")
        print("  Robotic Arm Controller Server is running...")
        print(f"  Please open your browser and visit http://localhost:5000/:{port}")
        print("===============================================================\n")
        print("################## Press Ctrl + C to exit #####################\n")
        
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        print("Web server not started. Use '--web' or '-W' to start the server.")

