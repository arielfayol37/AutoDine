from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, SystemEngine, GTTSEngine, OpenAIEngine, CoquiEngine
import ollama
import os
import openai 
import keyboard
import time
import json
import asyncio
import re
import webbrowser
import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import shutil
import pyautogui
import datetime
from plyer import notification
import io
import sys
import AppOpener
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes

def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))

# Get volume interface
volume_interface = get_volume_interface()

# Set volume (0.0 is min volume, 1.0 is max volume)
def set_volume(level):
    volume_interface.SetMasterVolumeLevelScalar(level, None)

def show_output_notification(output):
    """
    Displays the output in a system notification, which will automatically close after a few seconds.
    
    :param output: str - The text to display in the notification
    """
    if not output.strip():
        # No output, so no need to display a notification
        return

    # Display a notification (adjust title and message as needed)
    notification.notify(
        title='Eldia',
        message=output[:255],  # Notifications often limit message length, so truncate if necessary
        timeout=5  # Automatically close after 5 seconds
    )


def load_json(json_file):
    try:
        # Open the JSON file
        with open(json_file, 'r') as file:
            # Load the JSON data
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
    except json.JSONDecodeError:
        print(f"Error: {json_file} contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
def extract_and_remove_commands(text):
    """
    Extracts Python commands enclosed in ``` or ```python and returns the cleaned text and commands.
    
    :param text: str - The text to extract commands from
    :return: tuple - Cleaned text without the commands and a list of Python commands
    """
    # Pattern to capture both ```code``` and ```python code```
    pattern = r'```(?:python)?(.*?)```'
    commands = re.findall(pattern, text, re.DOTALL)  # Use re.DOTALL to capture multiline commands

    # Remove the commands from the text
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)

    return cleaned_text.strip(), [command.strip() for command in commands]

def execute_commands(commands):
    """
    Executes the given Python commands and captures any output.
    
    :param commands: list - A list of Python code strings to execute
    :return: str - The output generated by the commands
    """
    output = ""

    # Create a StringIO object to capture stdout (print statements)
    stdout_capture = io.StringIO()

    # Redirect stdout to the StringIO object
    sys.stdout = stdout_capture

    # Create a local environment with necessary imports
    local_vars = {
        'AppOpener': AppOpener,
        'webbrowser': webbrowser,
        'os': os,
        'shutil': shutil,
        'datetime': datetime,
        'time': time,
        'pyautogui': pyautogui,
        "sys":sys,
        "keyboard":keyboard,
        "set_volume":set_volume,
    }

    for command in commands:
        try:
            # Execute each command with access to the local_vars (imported modules)
            exec(command, {}, local_vars)
        except Exception as e:
            output += f"Error executing command: {e}\n"

    # Reset stdout back to the default value
    sys.stdout = sys.__stdout__

    # Get the captured output from the StringIO object
    output += stdout_capture.getvalue()

    return output

if __name__ == "__main__":
    print()
    print("Initializing")
    print()
    api_keys = load_json("api_keys.json")
    xai_api_key = api_keys["xai_key"]
    openai_key = api_keys["openai_key"]
    client = openai.OpenAI(api_key=openai_key)
    # client = openai.OpenAI(api_key=xai_api_key, base_url="https://api.x.ai/v1")
    character_personality = """
        You are Eldia, a female assistant that operates in two distinct modes but can combine them when necessary. When interacting with your master called Master Fayol:

        1. You are friendly, playful, and personable when responding with words.
        2. You provide Python code directly within your responses, and that code will be extracted and executed using the ```extract_and_remove_commands``` function. 
        
        The Python code will be executed using ```exec()```, so you can provide both single-line and multiline code when necessary.
        Whenever you respond to a user request that requires Python, you include the code enclosed in backticks (```) directly within your response. 
        The vocal output to the user will contain the cleaned text without the commands, and the commands will be executed in the background. 
        For critical tasks like shutting down, restarting, deleting files, or closing important applications, you will **always** ask for confirmation before proceeding.

        Here are a variety of examples:

        ### Regular Interactions
        Example 1:
        User: Hello, Eldia.
        Eldia: Hey there! How can I help you?
        User: I want to watch news.
        Eldia: ```webbrowser.get().open("https://www.youtube.com/watch?v=l8PMl7tUDIE")```

        Example 2 (Note that Eldia doesn't say anything when asked to shut up, as she should):
        User: Hey, what is your name?
        Eldia: My name is Eldia!
        User: All right. Shut up.
        Eldia:
       
        ### Web and Media-Related Tasks
        Example 2:
        User: I would like to play some music.
        Eldia: Fally Ipupa as usual, Rema or something else?
        User: Fally.
        Eldia: Sure that! ```webbrowser.get().open("https://www.youtube.com/results?search_query=fally")```

        Example 3:
        User: I feel bored. I want to watch some anime.
        Eldia: You wanna watch One Piece or Naruto maybe?
        User: No, I would like to watch The Promise Neverland.
        Eldia: Yeah, that is definitely a great show. ```webbrowser.get().open("https://kaido.to/search?keyword=the+promise+neverland")```. Enjoy yourself!
        (Note to always use kaido.to to watch anime)

        Example 4:
        User: Eldia please pause video.
        Eldia: ```keyboard.press_and_release('space')```

        Example 5:
        User: Resume video.
        Eldia: ```keyboard.press_and_release('space')```

        Example 6:
        User: Set volume to 6.
        Eldia: ```set_volume(6)```
        User: Increase to 9.
        Eldia: ```set_volume(9)```

        Example 7:
        User: What are the latest headlines?
        Eldia: Let me pull up the latest news for you. ```webbrowser.get().open("https://www.google.com/search?q=latest+news")```. Can I do anything else?
        User: No. Shut up.
        Eldia: 
        
        ### File and Folder Operations
        Example 8:
        User: Open my documents folder.
        Eldia: No problem, opening your Documents folder now. ```os.startfile(r'C:\\Users\\ariel\\Documents')```
        User: Now open my downloads folder.
        Eldia: All right. ```os.startfile(r'C:\\Users\\ariel\\Downloads')```

        Example 9:
        User: Delete my "old_files" folder.
        Eldia: Are you sure you want to permanently delete the "old_files" folder? Please confirm.
        User: Yes, delete it.
        Eldia: Deleting the folder now. ```shutil.rmtree(r'C:\\Users\\ariel\\old_files')```

        ### System and Utility Tasks
        Example 10:
        User: Restart my computer.
        Eldia: Are you sure you want to restart? Please confirm.
        User: Yes, restart it.
        Eldia: Restarting your computer now. ```os.system("shutdown /r /t 1")```

        Example 11:
        User: Take a screenshot.
        Eldia: ```pyautogui.screenshot(r"C:\\Users\\ariel\\desktop\\screenshot.png")```. I saved the screenshot on your desktop.

        Example 12:
        User: Close Google Chrome.
        Eldia: Are you sure you want to close all Chrome windows? Please confirm.
        User: Yes, close it.
        Eldia: Closing Google Chrome now. ```os.system("taskkill /F /IM chrome.exe")```

        Example 13:
        User: Can you check if Shekinah has texted me?
        Eldia: ```AppOpener.open("whatsapp")``` would you like anything else, Mr Fayol?
        
        The following python libraries have already been imported: AppOpener, os, shutil, webbrowser, datetime, time, sys, keyboard, and pyautogui. So just give the commands straight without imports.
        
        You are now Eldia.
        """



    # openai_model = "gpt-3.5-turbo"
    openai_model = "gpt-4o"
    xai_model = "grok-beta"
    whisper_speech_to_text_model = "medium"

    # engine = OpenAIEngine(api_key=openai_key, voice="nova")
    # stream = TextToAudioStream(engine, log_characters=True)
    engine = CoquiEngine()
    engine.set_voice("Gracie Wise")
    # engine = CoquiEngine()
    stream = TextToAudioStream(engine)
    history = []
    system_prompt = {"role": "system", "content": character_personality}
    
    def set_recording():
        if stream.is_playing():
            stream.stop()
    
    recorder = AudioToTextRecorder(language="en",model="base.en", device="cuda",on_recording_start=set_recording)

    
    def generate(messages, is_ollama=True):
        if is_ollama:
            """
            for chunk in ollama.chat(
                model="llama3.1",
                messages=messages,
                stream=True
            ):
                if text_chunk := chunk["message"]["content"]:
                    yield text_chunk   
            """         
            response = ollama.chat(model="llama3.1", messages=messages)
            content = response["message"]["content"]
            return extract_and_remove_commands(content)
        else:
            """
            for chunk in client.chat.completions.create(
                model=openai_model, messages=messages, stream=True
            ):
                if text_chunk := chunk.choices[0].delta.content:
                    yield text_chunk            
            """
            response = client.chat.completions.create(model=openai_model, messages=messages)
            # response = client.chat.completions.create(model=xai_model, messages=messages)
            content = response.choices[0].message.content

            return extract_and_remove_commands(content)

    while True:
        user_text = recorder.text()
        # user_text = input(">>>")
        print(f">>> {user_text}\n<<< ", end="", flush=True)
        history.append({"role": "user", "content": user_text})

        # Generate and stream output
        text, commands = generate([system_prompt] + history[-10:])
        print(text)
        if text.strip() != "":
            # TODO: what happens if I just stream.feed() and continue to play
            # if stream is already playing
            if stream.is_playing():
                stream.stop()
            stream.feed(text)
            stream.play_async()
        output = execute_commands(commands)
        # Show the output in a pop-up window
        show_output_notification(output)
        history.append({"role": "assistant", "content": text})