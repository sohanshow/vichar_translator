import pyaudio
import speech_recognition as sr
import openai
import threading
import queue
import os
from dotenv import load_dotenv
load_dotenv()


# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize the recognizer, microphone, and a queue to hold audio
recognizer = sr.Recognizer()
microphone = sr.Microphone()
audio_queue = queue.Queue()

# Function to translate text from Hindi to English using OpenAI
def translate_to_english(hindi_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translation model."},
                {"role": "user", "content": hindi_text}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error during translation: {e}")
        return ""

# Function to continuously capture audio
def capture_audio():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            audio = recognizer.listen(source)
            audio_queue.put(audio)

# Function to process and translate audio
def process_audio():
    while True:
        audio = audio_queue.get()
        if audio is None:
            break
        try:
            hindi_text = recognizer.recognize_google(audio, language="hi-IN")
            print(f"Hindi: {hindi_text}")
            english_translation = translate_to_english(hindi_text)
            print(f"English: {english_translation}")
        except sr.RequestError:
            print("API unavailable")
        except sr.UnknownValueError:
            print("Unable to recognize speech")

# Starting threads for capturing and processing audio
capture_thread = threading.Thread(target=capture_audio)
process_thread = threading.Thread(target=process_audio)

capture_thread.start()
process_thread.start()