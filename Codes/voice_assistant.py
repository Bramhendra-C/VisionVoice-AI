import speech_recognition as sr
import pygame
import datetime
import webbrowser
import random
import pyttsx3
import wikipedia
import pyjokes
import requests
import os

# --- SAFE IMPORT FOR PYWHATKIT (SKIPS INTERNET CHECK IF OFFLINE) ---
try:
    import pywhatkit as kit
except Exception:
    kit = None
    print("⚠️ pywhatkit disabled (no internet connection).")

# --- CONFIGURATION (Uses API Key as requested) ---
OPENWEATHERMAP_API_KEY = " YOUR OPENWEATHERMAP KEY "
MUSIC_DIR = "C:/projects/Vision/music"  # change path to your music folder

# --- DATA ---
FUN_FACTS = [
    "Bananas are berries, but strawberries are not.",
    "Honey never spoils. Archaeologists have found edible honey in ancient tombs.",
    "Octopuses have three hearts.",
    "Sharks existed before trees.",
    "A day on Venus is longer than a year on Venus."
]

QUOTES = [
    "The best way to get started is to quit talking and begin doing. – Walt Disney",
    "Don't let yesterday take up too much of today. – Will Rogers",
    "It’s not whether you get knocked down, it’s whether you get up. – Vince Lombardi",
    "Success is not in what you have, but who you are, – Bo Bennett",
    "Do something today that your future self will thank you for."
]

# --- INITIALIZATION ---
try:
    engine = pyttsx3.init()
    wikipedia.set_lang("en")
    pygame.mixer.init()
except Exception as e:
    print(f"Initialization error: {e}")
    exit()

# --- CORE FUNCTIONS ---
def speak(text):
    """Converts text to speech."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listens for a command and returns it as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you please repeat?")
        return "none"
    except sr.RequestError:
        speak("Could not request results from the speech service.")
        return "none"
    except Exception as e:
        speak("An unexpected error occurred while capturing your command.")
        print(f"Error: {e}")
        return "none"

# --- NLP Intent Classification (Simplified) ---
def classify_intent(query):
    """Classifies the user's intent based on keywords."""
    if 'exit' in query or 'stop' in query or 'bye' in query:
        return 'exit'
    if 'time' in query:
        return 'get_time'
    if 'joke' in query:
        return 'tell_joke'
    if 'fun fact' in query:
        return 'tell_fact'
    if 'quote' in query:
        return 'tell_quote'
    if 'wikipedia' in query or 'wiki' in query:
        return 'search_wikipedia'
    if 'youtube' in query or 'play' in query and ('song' in query or 'video' in query):
        return 'play_youtube'
    if 'search' in query or 'google' in query or 'look up' in query:
        return 'search_google'
    if 'weather' in query:
        return 'get_weather'
    if 'pause' in query or 'resume' in query or 'volume' in query:
        return 'control_music'
    if 'switch to face detection' in query or 'face detection' in query:
        return 'switch_to_vision'
    return 'unknown'

# --- WEATHER ---
def get_weather(city):
    
    """Fetches and speaks the weather for a given city using API Key."""
    if not OPENWEATHERMAP_API_KEY:
        speak("Weather check failed. Please set your OpenWeatherMap API key.")
        return
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp}°C with {desc}.")
        else:
            speak(f"I couldn't find weather information for {city}.")
    except Exception as e:
        speak("Sorry, I could not fetch weather data right now.")

# --- GREETING ---
def wish_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Good Morning!"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"
    speak(f"{greeting} I am your assistant. How can I help you today?")

# --- MAIN LOGIC ---
def run_assistant():
    wish_user()
    is_music_playing = False
    volume = 0.5
    pygame.mixer.music.set_volume(volume)

    while True:
        query = take_command()
        if query == "none":
            continue

        intent = classify_intent(query)
        
        # --- Execute Intent ---
        if intent == 'get_time':
            speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")

        elif intent == 'tell_joke':
            speak(pyjokes.get_joke())

        elif intent == 'tell_fact':
            speak(random.choice(FUN_FACTS))
            
        elif intent == 'tell_quote':
            speak(random.choice(QUOTES))

        elif intent == 'search_wikipedia':
            speak('Searching Wikipedia...')
            search_term = query.replace("wikipedia", "").replace("wiki", "").strip()
            try:
                summary = wikipedia.summary(search_term, sentences=random.randint(2, 4))
                speak(summary)
            except Exception:
                speak("Sorry, I couldn’t find information on that.")

        elif intent == 'play_youtube':
            if kit is None:
                speak("You are offline. Cannot access YouTube.")
                continue
            search_term = query.replace('youtube', '').replace('play', '').strip()
            if not search_term:
                speak("What should I play on YouTube?")
                search_term = take_command()
            if search_term != "none":
                speak(f"Playing {search_term} on YouTube.")
                kit.playonyt(search_term)

        elif intent == 'search_google':
            search_term = query.replace("search", "").replace("google", "").replace("look up", "").strip()
            speak(f"Searching Google for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")

        elif intent == 'get_weather':
            city = query.replace("weather in", "").replace("what's the weather in", "").strip()
            if city in ['near me', 'my location', 'here']:
                city = 'Angallu'  # Placeholder for location-based weather fetching
            if city:
                get_weather(city)
            else:
                speak("Please tell me the city name.")

        elif intent == 'switch_to_vision':
            speak("Switching to Face Detection Mode.")
            try:
                import face
                face.run_face_detection()
            except Exception:
                speak("Face detection module not found.")

        elif intent == 'control_music':
            if 'pause' in query and is_music_playing:
                pygame.mixer.music.pause()
                speak("Music paused.")
            elif 'resume' in query and is_music_playing:
                pygame.mixer.music.unpause()
                speak("Resuming music.")
            elif 'volume up' in query:
                volume = min(1.0, volume + 0.1)
                pygame.mixer.music.set_volume(volume)
                speak(f"Volume set to {int(volume * 100)} percent.")
            elif 'volume down' in query:
                volume = max(0.0, volume - 0.1)
                pygame.mixer.music.set_volume(volume)
                speak(f"Volume set to {int(volume * 100)} percent.")

        elif intent == 'exit':
            speak("Goodbye! Have a great day.")
            break
            
        elif intent == 'unknown':
            speak("I'm sorry, I don't know how to handle that command yet.")
        
        else:
            speak('Searching Online...')
            search_term = query.replace("wikipedia", "").replace("wiki", "").strip()
            try:
                summary = wikipedia.summary(search_term, sentences=random.randint(2, 4))
                speak(summary)
            except Exception:
                speak("Sorry, I couldn’t find information on that.")

# --- RUN DIRECTLY ---
if __name__ == "__main__":

    run_assistant()
