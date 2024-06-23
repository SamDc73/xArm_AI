from flask import Flask, render_template, jsonify, request
import subprocess
import action_grippers as actions
import speech_recognition as sr
import base64
import argparse
import os

app = Flask(__name__, static_folder="web/static", template_folder="web")


@app.route("/rotate", methods=["POST"])
def rotate():
    if request.method == "POST":
        data = request.get_json()
        degreesX = float(data.get("degreesX"))
        degreesY = float(data.get("degreesY"))
        degreesZ = float(data.get("degreesZ"))

        if degreesX is not None and degreesY is not None and degreesZ is not None:
            try:
                try:
                    actions.rotate_arm(degreesX, degreesY, degreesZ)
                    return jsonify({"message": "Arm rotated successfully"})
                except Exception as e:
                    return jsonify({"error": f"Failed to rotate arm: {str(e)}"}), 500
            except Exception as e:
                return jsonify({"error": f"Failed to rotate arm: {str(e)}"}), 500
        else:
            return (
                jsonify({"error": "Degrees of rotation not provided in the request"}),
                400,
            )


@app.route("/translate", methods=["POST"])
def translate():
    if request.method == "POST":
        data = request.get_json()
        x = float(data.get("x"))
        y = float(data.get("y"))
        z = float(data.get("z"))

        if x is not None and y is not None and z is not None:
            try:
                try:
                    actions.translate_arm(x, y, z)
                    return jsonify({"message": "Arm translated successfully"})
                except Exception as e:
                    return jsonify({"error": f"Failed to translate arm: {str(e)}"}), 500
            except Exception as e:
                return jsonify({"error": f"Failed to translate arm: {str(e)}"}), 500
        else:
            return (
                jsonify({"error": "Translation values not provided in the request"}),
                400,
            )


@app.route("/gripper", methods=["POST"])
def gripper():
    if request.method == "POST":
        data = request.get_json()
        action = data.get("action")
        force = float(data.get("force"))

        if action is not None and force is not None:
            try:
                try:
                    actions.gripper_arm(action, force)
                    return jsonify({"message": "Arm gripper action completed successfully"})
                except Exception as e:
                    return jsonify({"error": f"Failed to perform gripper action: {str(e)}"}), 500
            except Exception as e:
                return (
                    jsonify({"error": f"Failed to perform gripper action: {str(e)}"}),
                    500,
                )
        else:
            return (
                jsonify(
                    {"error": "Gripper action or force not provided in the request"}
                ),
                400,
            )




@app.route("/")
def index():
    return render_template(
        "index.html"
    )  # Ensure this file exists in the 'web' directory


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    try:
        audio_file = request.files['audio']
        audio_data = audio_file.read()

        try:
            result = actions.get_utterance(audio_data=audio_data)
            return jsonify({"status": "success", "message": "Audio processed successfully", "transcript": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to read audio file"}), 400

def start_recording():
    # Dummy return to test the web app functionality
    return jsonify({"status": "success", "message": "Recording would start"})


# @app.route('/start-recording', methods=['POST'])
# def start_recording():
#     result = get_utterance()
#     if "Error" in result:
#         return jsonify({'status': 'error', 'message': result}), 500
#     return jsonify({'status': 'success', 'message': 'Recording started successfully', 'transcript': result}), 200


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description="Start the Flask web server for the Robotic Arm Controller."
    )
    parser.add_argument("-W", "--web", action="store_true", help="Start the web server")
    parser.add_argument("-A", "--audio", action="store_true", help="Start audio recording from the terminal")

    args = parser.parse_args()

    if args.web:
        port = 5000
        os.system("clear")
        print("\n===============================================================")
        print("  Robotic Arm Controller Server is running...")
        print(f"  Please open your browser and visit http://localhost:{port}")
        print("===============================================================\n")
        print("################## Press Ctrl + C to exit #####################\n")

        app.run(debug=True, host="0.0.0.0", port=port)
    elif args.audio:
        os.system("clear")
        print("\n===============================================================")
        print("  Starting audio recording...")
        print("===============================================================\n")
        print("################## Press Ctrl + C to exit #####################\n")
        try:
            result = actions.get_utterance()
            print(f"Transcript: {result}")
        except Exception as e:
            print(f"Error during audio recording: {str(e)}")
        port = 5000
        os.system("clear")
        print("\n===============================================================")
        print("  Robotic Arm Controller Server is running...")
        print(f"  Please open your browser and visit http://localhost:{port}")
        print("===============================================================\n")
        print("################## Press Ctrl + C to exit #####################\n")

        app.run(debug=True, host="0.0.0.0", port=port)
        print("Web server not started. Use '--web' or '-W' to start the server.")
