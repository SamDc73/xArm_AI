import speech_recognition as sr
from openai import OpenAI
import asyncio
import io
from dotenv import load_dotenv
import os
import json

load_dotenv()
from xarm import XArmAPI

OPENAI_API_KEY='sk-proj-HXihlH8IxavHlhs52gDST3BlbkFJlSn7YNSDSPQuYZVca5dU'
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def arm_setup(enable_motion=True):
    ip = "192.168.1.213"
    arm = XArmAPI(ip, is_radian=True)
    arm.motion_enable(enable=True)
    arm.set_mode(0 if enable_motion else 2)
    arm.set_state(state=0)
    return arm


def arm_translate(x, y, z):
    arm = arm_setup()
    _, [currentX, currentY, currentZ, roll, pitch, yaw] = arm.get_position(
        is_radian=True
    )
    arm.set_position(
        x=currentX + (x * 10), y=currentY + (y * 10), z=currentZ + (z * 10), roll=roll, pitch=pitch, yaw=yaw
    )


def arm_rotate(roll, pitch, yaw):
    arm = arm_setup()
    _, [_, _, _, currentRoll, currentPitch, currentYaw] = arm.get_position(
        is_radian=True
    )
    arm.set_position(
        roll=currentRoll + roll, pitch=currentPitch + pitch, yaw=currentYaw + yaw
    )

def arm_gripper(action, force=None):
    arm = arm_setup()
    if action == 'open':
        # Open the gripper fully without applying any force parameter
        arm.set_gripper_position(arm.gripper.get_open_position())
    elif action == 'close':
        if force is not None:
            # Close the gripper with specified force to hold objects gently
            arm.set_gripper_force(force)
        # Move the gripper to the close position or to a position that applies the set force
        arm.set_gripper_position(arm.gripper.get_close_position())
        

def get_utterance(audio_data=None):
    r = sr.Recognizer()
    if audio_data:
        audio = sr.AudioFile(io.BytesIO(audio_data))
        with audio as source:
            audio = r.record(source)
    else:
        with sr.Microphone() as source:
            try:
                # Adjust for ambient noise and set a higher threshold
                print("Adjusting for ambient noise. Please wait...")
                r.adjust_for_ambient_noise(source, duration=3)
                r.dynamic_energy_threshold = True
                r.energy_threshold = 4000  # Increase this value for noisier environments

                print("Say something!")

                # Increase timeout and phrase time limit
                audio = r.listen(source, timeout=10, phrase_time_limit=5)
            except Exception as e:
                print(f"Error: {str(e)}")  # Customize or handle logging
                return "Device not connected or audio setup issue."

    print("Processing...")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    audio_data = io.BytesIO(audio.get_wav_data())
    audio_data.name = "audio.wav"

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_data,
        response_format="text",
    )
    print(transcript)
    return transcript


client = OpenAI()


def rotate_arm(degreesX, degreesY, degreesZ):
    print(
        "Rotating arm "
        + str(degreesX)
        + " degrees on the X axis, "
        + str(degreesY)
        + " degrees on the Y axis, and "
        + str(degreesZ)
        + " degrees on the Z axis"
    )
    arm_rotate(degreesX, degreesY, degreesZ)


def translate_arm(x, y, z):
    print(
        "Translated arm "
        + str(x)
        + " units on the X axis, "
        + str(y)
        + " units on the Y axis, and "
        + str(z)
        + " units on the Z axis"
    )
    arm_translate(x, y, z)
    
    
def grippper_arm(action, force):
    print(
        "Action arm "
        + str(action)
        + " with force "
        + str(force)
    )
    arm_gripper(action, force)


def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [
        {
            "role": "system",
            "content": """
         You are controlling a robotic arm. Think carefully about how to turn instructions and statements into various movements
         """,
        },
        {"role": "user", "content": get_utterance()},
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "rotate_arm",
                "description": "Rotate a robotic arm X, Y, Z degrees",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "degreesX": {
                            "type": "number",
                            "description": "How many degress to rotate the arm on the X axis",
                        },
                        "degreesY": {
                            "type": "number",
                            "description": "How many degress to rotate the arm on the Y axis",
                        },
                        "degreesZ": {
                            "type": "number",
                            "description": "How many degress to rotate the arm on the Z axis",
                        },
                    },
                    "required": ["degreesX", "degreesY", "degreesZ"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "translate_arm",
                "description": "Translate a robotic arm X, Y, Z relative degrees",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "How many units to move on the X axis, max 20, min -20",
                        },
                        "y": {
                            "type": "number",
                            "description": "How many units to move on the Y axis, max 20, min -20",
                        },
                        "z": {
                            "type": "number",
                            "description": "How many units to move on the Z axis, max 20, min -20",
                        },
                    },
                    "required": ["x", "y", "z"],
                },
            },
        },
                {
            "type": "function",
            "function": {
                "name": "grippper_arm",
                "description": "Open or close the gripper of the robotic arm",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform on the gripper, either 'open' or 'close'",
                        },
                        "y": {
                            "type": "number",
                            "description": "How much force to apply to the gripper, max 100, min 0",
                        },
                    },
                    "required": ["action", "force"],
                },
            },
        },
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        available_functions = {
            "rotate_arm": rotate_arm,
            "translate_arm": translate_arm,
            "grippper_arm": grippper_arm,
        }
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": (
                        function_response
                        if function_response is not None
                        else "Was Successful"
                    ),
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
    else:
        return response_message


print(run_conversation())
