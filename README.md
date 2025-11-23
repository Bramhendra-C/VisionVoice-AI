🧠 VisionVoice AI Assistant

A Real-Time Computer Vision + Voice Interaction Productivity Assistant

📌 Overview

VisionVoice AI Assistant is a hybrid Python-based artificial intelligence system that combines:

Computer Vision (Face Detection + Focus Tracking)

Voice Assistant (Speech Recognition + NLP + TTS)

Multi-threading for simultaneous operations

This assistant helps users stay productive by monitoring their focus in real-time and responding to voice commands for tasks like weather updates, jokes, searches, and more.

🔥 Features
🎯 1. Face Detection & Focus Tracking

Detects face using OpenCV Haar Cascade

Shows FOCUSED or UNFOCUSED state

Tracks unfocused duration

Alerts user when they are distracted

Provides live video feed with status overlay

🎤 2. Voice Assistant

Responds to voice commands for:

Weather information

Jokes & facts

Google search

YouTube search & play

Time updates

Wikipedia summaries

⚡ 3. Smart Assistant Mode

Face tracking + voice assistant running simultaneously

Powered by Python threading

Real-time alerts + voice automation

📦 4. Modular Architecture

face.py – Face detection module

face1.py – Focus tracking module

voice_assistant.py – Voice assistant module

smart_assistant.py – Integrated dual-mode assistant

start.py – Main launcher menu

🛠️ Technologies Used
Feature	Library
Computer Vision	OpenCV
Speech-to-Text	SpeechRecognition
Text-to-Speech	pyttsx3
Weather API	OpenWeatherMap
Web Automation	PyWhatKit
Fun Commands	pyjokes
Info Fetching	wikipedia
Concurrency	Python threading
📥 Installation
1. Clone the repository
git clone https://github.com/Bramhendra-C/VisionVoice-AI.git
cd VisionVoice-AI

2. Install dependencies
pip install -r requirements.txt

⚠ If PyAudio fails on Windows:
pip install pipwin
pipwin install pyaudio

▶️ How to Run
Launch the main menu:
python start.py

Choose from:

Vision Mode (Face Detection + Focus Tracking)

Voice Assistant Mode

Smart Assistant Mode (Both together)

📁 Project Folder Structure
VisionVoice-AI/
│── face.py
│── face1.py
│── voice_assistant.py
│── smart_assistant.py
│── start.py
│── requirements.txt
│── README.md
└── assets/ (optional)

🧪 Testing

Tested for:

Lighting variations

Background noise

Different accents

Multi-threading stability

Focus lapse detection

Voice recognition accuracy

🚀 Future Enhancements

Eye-tracking and advanced focus analytics

Emotion detection using deep learning

Full GUI dashboard

Cloud integration for productivity logs

Real-time speech sentiment analysis

Mobile / PWA support

Notification reminders

🤝 Contributing

Pull requests are welcome!
Submit issues for bugs, suggestions, or improvements.

📜 License

This project is free to use for educational and research purposes.