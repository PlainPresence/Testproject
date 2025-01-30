import os
import requests
import pyttsx3
import speech_recognition as sr
import numpy as np
import pyaudio
import threading
import time
import openai

# Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize the TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 145)  # Speed of the speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to analyze sentiment using OpenAI API
def analyze_sentiment(command):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Analyze the sentiment of this text: '{command}'"}]
    )
    sentiment = response['choices'][0]['message']['content']
    return sentiment

# Function to generate an image using OpenAI's DALL-E
def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url

# Function for listening to voice commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"Command: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Could not request results from the speech recognition service.")
            return ""

# Clap detection
def detect_clap():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    print("Waiting for clap detection...")
    while True:
        audio_data = np.frombuffer(stream.read(1024), dtype=np.int16)
        energy = np.sum(np.abs(audio_data))

        if energy > 5000:  # Adjust this threshold based on testing
            print("Clap detected! Activating assistant...")
            speak("Clap detected, activating ARIA!")
            break

# Main function to run the assistant
def run_assistant():
    detect_clap()  # Detect clap to activate

    while True:
        command = listen()
        if command:
            sentiment = analyze_sentiment(command)
            speak(f"I detected that you are feeling {sentiment.lower()}.")
            
            if "generate image" in command:
                prompt = command.replace("generate image", "").strip()
                image_url = generate_image(prompt)
                if image_url:
                    speak(f"Here is the image generated for {prompt}.")
                    print(f"Image URL: {image_url}")
                else:
                    speak("Sorry, I couldn't generate the image.")

# Start the assistant in a separate thread
assistant_thread = threading.Thread(target=run_assistant, daemon=True)
assistant_thread.start()

# Keep the script running
while True:
    time.sleep(1)  # Keeps the script running
