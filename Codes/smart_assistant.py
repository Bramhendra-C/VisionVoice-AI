import cv2
import time
import datetime
import speech_recognition as sr
import pyttsx3
import pyjokes
import requests
import random
import webbrowser
import threading # Recommended for true parallelism (listening while seeing)

# --- Configuration (from voice_assistant.py) ---
OPENWEATHERMAP_API_KEY = " YOUR OPENWEATHERMAP KEY "
UNFOCUS_TIMEOUT = 10 # Seconds until exit in focus mode (from face1.py)

# --- Data (from voice_assistant.py) ---
FUN_FACTS = [
    "Bananas are berries, but strawberries are not.",
    "Honey never spoils. Archaeologists have found edible honey in ancient tombs.",
    "Octopuses have three hearts.",
    "A day on Venus is longer than a year on Venus."
]

# --- CV/AI Initialization (from face.py and face1.py) ---
try:
    face_data = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    webcam = cv2.VideoCapture(0)
except Exception as e:
    print(f"CV Initialization Error: {e}")
    webcam = None
    face_data = None

# --- Voice Initialization (from voice_assistant.py) ---
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"Voice Initialization Error: {e}")
    engine = None

# --- CORE VOICE FUNCTIONS (Simplified from voice_assistant.py) ---
def speak(text):
    """Converts text to speech."""
    print(f"Assistant: {text}")
    if engine:
        engine.say(text)
        engine.runAndWait()

def take_command():
    """Listens for a command and returns it as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=5)
            query = r.recognize_google(audio, language='en-in')
            print(f"You said: {query}")
            return query.lower()
        except sr.WaitTimeoutError:
            return "timeout" # User didn't speak
        except Exception:
            return "none" # Recognition failed

def classify_and_execute(query):
    """Classifies user intent and executes the command."""
    if 'exit' in query or 'stop' in query or 'bye' in query:
        speak("Exiting assistant. Goodbye!")
        return 'exit'
    
    if 'time' in query:
        speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")
    elif 'joke' in query:
        speak(pyjokes.get_joke())
    elif 'fun fact' in query:
        speak(random.choice(FUN_FACTS))
    elif 'weather' in query:
        city = query.replace("weather in", "").replace("what's the weather in", "").strip()
        if city and len(city) > 2:
            get_weather(city)
        else:
            speak("Please tell me the city name for the weather.")
    elif 'search' in query or 'google' in query:
        search_term = query.replace("search", "").replace("google", "").strip()
        speak(f"Searching Google for {search_term}")
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
    else:
        speak("I'm not sure how to handle that command yet.")
    return 'handled'

def get_weather(city):
    """Fetches and speaks the weather for a given city."""
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
    except Exception:
        speak("Sorry, I could not fetch weather data right now.")

# --- MAIN INTEGRATED LOOP ---
def run_smart_assistant():
    if not webcam or not face_data:
        speak("Critical components failed to load. Cannot run the assistant.")
        return

    speak("Welcome! I am your AI Focus Assistant. Starting monitoring mode.")
    
    # State tracking variables (from face1.py)
    focused = False # Initial state: assumed unfocused
    last_focus_time = time.time()
    unfocus_count = 0
    
    # State for speaking intervention
    focus_speech_done = True # Prevents speaking immediately on startup
    
    # Create a flag for voice thread to check
    global assistant_running
    assistant_running = True

    # --- Threaded Listening Function ---
    def voice_listener():
        global assistant_running
        while assistant_running:
            query = take_command()
            if query not in ["none", "timeout"]:
                action = classify_and_execute(query)
                if action == 'exit':
                    assistant_running = False

    # Start the voice listener thread
    voice_thread = threading.Thread(target=voice_listener)
    voice_thread.daemon = True # Allows program to exit even if thread is running
    voice_thread.start()

    # --- CV/Focus Loop ---
    while assistant_running:
        success, frame = webcam.read()
        if not success:
            break

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_co = face_data.detectMultiScale(gray_img, scaleFactor=1.5, minNeighbors=5)
        
        thumb_size = (300, 300)

        # --- FOCUS/UNFOCUS LOGIC ---
        face_detected = len(face_co) > 0
        
        if face_detected:
            # FOCUSED
            (x, y, w, h) = face_co[0]
            face_roi = frame[y:y+h, x:x+w]
            thumbnail = cv2.resize(face_roi, thumb_size)
            border_color = (0, 255, 0)
            
            last_focus_time = time.time()
            
            if not focused:
                focused = True
                # Trigger assistant to speak when returning to focus
                if not focus_speech_done:
                    current_time = datetime.datetime.now().strftime('%I:%M:%S')
                    speak(f"Welcome back! Focused. It is {current_time}.")
                    focus_speech_done = True
                
            label = "FOCUSED"
            label_color = (0, 255, 0)
            
        else:
            # UNFOCUSED
            blurred = cv2.GaussianBlur(frame, (45, 45), 0)
            thumbnail = cv2.resize(blurred, thumb_size)
            border_color = (0, 0, 255) 
            
            if focused:
                unfocus_count += 1
                focused = False
                focus_speech_done = False # Allow assistant to speak next time user focuses
                speak(f"Unfocused! This is lapse number {unfocus_count}.")

            unfocused_time = time.time() - last_focus_time
            
            label = f"UNFOCUSED - {int(unfocused_time)}s / {UNFOCUS_TIMEOUT}s"
            label_color = (0, 0, 255)
            
            # --- AUTOMATIC EXIT CONDITION ---
            if unfocused_time >= UNFOCUS_TIMEOUT:
                speak(f"Unfocused for {UNFOCUS_TIMEOUT} seconds. Exiting focus mode.")
                assistant_running = False # Stop the main loop and voice thread
                break
                
        # --- DISPLAY LOGIC (Same as face.py/face1.py) ---
        thumbnail_with_border = cv2.copyMakeBorder(
            thumbnail, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=border_color
        )
        cv2.putText(thumbnail_with_border, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

        h_thumb, w_thumb, _ = thumbnail_with_border.shape
        x_offset = frame.shape[1] - w_thumb - 10
        y_offset = 10
        frame[y_offset:y_offset+h_thumb, x_offset:x_offset+w_thumb] = thumbnail_with_border

        cv2.putText(frame, f"Unfocus Lapses: {unfocus_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imshow('AI Focus Assistant - Enhanced', frame)

        if cv2.waitKey(1) == 49: # Exit on '1' key press
            speak("Manual exit detected.")
            assistant_running = False
            break

    # --- CLEANUP ---
    webcam.release()
    cv2.destroyAllWindows()
    # Wait for the voice thread to finish its last task
    if voice_thread.is_alive():
        voice_thread.join(timeout=1)

# --- RUN THE ASSISTANT ---
if __name__ == "__main__":

    run_smart_assistant()
