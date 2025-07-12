# ========== IMPORTS ==========
import webbrowser
import pyjokes
import datetime
from gtts import gTTS
import tempfile
import playsound
from urllib.parse import quote
import requests
import os
import time
import wikipedia
import sys

# ========== CORE FUNCTIONS ==========play
def speak(text):
    """Convert text to speech with reliable fallback"""
    print("Assistant:", text)
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as fp:
            temp_file = f"{fp.name}.mp3"
            tts.save(temp_file)
            playsound.playsound(temp_file)
            os.remove(temp_file)
    except Exception as e:
        print("Audio error:", e)
        # Simple fallback for systems without audio
        import sys
        if sys.platform == 'darwin':
            os.system(f'say "{text}"')

def get_wikipedia_answer(query):
    """Get simple Wikipedia summary with error handling"""
    try:
        wikipedia.set_lang("en")
        result = wikipedia.summary(query, sentences=2)
        return result
    except wikipedia.DisambiguationError as e:
        return f"There are multiple meanings. Try being more specific."
    except:
        return "I couldn't find information about that."

# ========== FEATURE FUNCTIONS ==========
def play_youtube(query):
    """Play YouTube video directly"""
    url = f"https://www.youtube.com/results?search_query={quote(query)}"
    webbrowser.open(url)
    return f"Playing {query} on YouTube"

def get_current_time():
    """Get formatted time"""
    return datetime.datetime.now().strftime("%I:%M %p")

def get_current_date():
    """Get formatted date"""
    return datetime.datetime.now().strftime("%B %d, %Y")

def tell_joke():
    """Tell a programming joke"""
    return pyjokes.get_joke()

def search_web(query):
    """Perform a web search"""
    url = f"https://www.google.com/search?q={quote(query)}"
    webbrowser.open(url)
    return f"Searching for {query}"

# ========== MAIN ASSISTANT ==========
def main():
    speak("Hello! I'm your personal assistant. How can I help?")
    
    while True:
        try:
            # Get text input (replace with voice input later if needed)
            user_input = input("You: ").strip().lower()
            
            if not user_input:
                continue
                
            # Process commands
            if "play" in user_input:
                query = user_input.replace("play", "").strip()
                response = play_youtube(query)
                
            elif "time" in user_input:
                response = get_current_time()
                
            elif "date" in user_input:
                response = get_current_date()
                
            elif "joke" in user_input:
                response = tell_joke()
                
            elif "search" in user_input:
                query = user_input.replace("search", "").strip()
                response = search_web(query)
                
            elif "who is" in user_input or "what is" in user_input:
                query = user_input.replace("who is", "").replace("what is", "").strip()
                response = get_wikipedia_answer(query)
                
            elif "exit" in user_input or "quit" in user_input:
                speak("Goodbye! Have a great day!")
                break
                
            else:
                response = "I can: play videos, tell time/date, tell jokes, search web, or look up facts. Try again!"
            
            speak(response)
            
        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as e:
            print("Error:", e)
            speak("Sorry, I had trouble with that request")

# ========== RUN THE ASSISTANT ==========
if __name__ == "__main__":
    # Install required packages if missing
    try:
        import gtts
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "gTTS", "playsound", "pyjokes", "wikipedia", "requests"])
    
    main()