import json
import os
import pyttsx3 as py
import speech_recognition as sr
import pywhatkit
import requests
import randfacts
import spacy
from datetime import date, datetime
import pygame
import pyaudio
from flask import Flask, request, jsonify


script_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(script_dir, 'respones.json')


if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file '{file_path}' does not exist.")


with open(file_path, 'r') as file:
    responses = json.load(file)

nlp = spacy.load("en_core_web_sm")
engine = py.init()
engine.setProperty('rate', 190)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

today = str(date.today())

pygame.mixer.init()

def generate_response(prompt):
    doc = nlp(prompt)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    if entities:
        response = "I found the following entities: " + ", ".join([f"{text} ({label})" for text, label in entities])
    else:
        response = "I'm not sure what you mean. Can you please clarify?"
    return response

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a") as f:
        f.write(text + "\n")

def get_chat_log():
    global today
    fname = 'chatlog-' + today + '.txt'
    if os.path.exists(fname):
        with open(fname, "r") as f:
            return f.read()
    else:
        return "No chat log found for today."

def wishme():
    hour = int(datetime.now().hour)
    if 1 < hour < 12:
        return responses["greetings"]["morning"]
    elif 12 <= hour < 16:
        return responses["greetings"]["afternoon"]
    else:
        return responses["greetings"]["evening"]
    
def get_joke():
    url = 'https://official-joke-api.appspot.com/random_joke'
    json_data = requests.get(url).json()
    setup = json_data["setup"]
    punchline = json_data["punchline"]
    return setup, punchline


def get_weather():
    try:
        api_address = 'https://api.openweathermap.org/data/2.5/weather?q=Vishakhapatnam&appid=33b2b85b934773c225dfde666c9ed0b7'
        json_data = requests.get(api_address).json()
        temperature = round(json_data["main"]["temp"] - 273.15, 1)
        description = json_data["weather"][0]["description"]
        return responses["weather"].format(temp=temperature, description=description)
    except Exception as e:
        return f"An error occurred: {e}"

def get_news():
    try:
        api_key = "c3de44ca3efa473f8ee154228a0f1c91"
        url = f'https://newsapi.org/v2/top-headlines?country=in&apiKey={"c3de44ca3efa473f8ee154228a0f1c91"}'
        response = requests.get(url)
        news_data = response.json()
        articles = news_data['articles']
        headlines = [article['title'] for article in articles[:5]]
        return headlines
    except Exception as e:
        return [f"Error retrieving news: {e}"]

def process_text(text):
    doc = nlp(text)
    return doc

def main():
    global today

    rec = sr.Recognizer()
    mic = sr.Microphone()
    rec.dynamic_energy_threshold = False
    rec.energy_threshold = 400    

    sleeping = True 

    while True:     
        with mic as source1:            
            rec.adjust_for_ambient_noise(source1, duration=0.5)
            print("Listening ...")

            try: 
                audio = rec.listen(source1, timeout=10, phrase_time_limit=15)
                text = rec.recognize_google(audio)

                if sleeping:
                    if "nova" in text.lower():
                        request = text.lower().split("nova")[1].strip()
                        sleeping = False
                        append2log(f"_"*40)
                        today = str(date.today()) 

                        if len(request) < 5:
                            speak_text("Hello I am nova, " + wishme() + ", I am your voice assistant.")
                            today_date = datetime.now()
                            hour_minute = today_date.strftime("%I:%M %p")
                            speak_text(f"Today is {today_date.strftime('%d')} of {today_date.strftime('%b')}. And it's currently {hour_minute}. {today_date.strftime('%a')}.")
                            speak_text(" how can I help you ?")
                            append2log(" how can I help?\n")
                            continue                      
                else: 
                    request = text.lower().strip()
                    if "that's all" in request or "that's it" in request:
                        append2log(f"You: {request}\n")
                        speak_text("Bye now")
                        append2log("AI: Bye now.\n")                        
                        print('Bye now')
                        sleeping = True
                        continue
                    if "nova" in request:
                        request = request.split("nova")[1].strip()

                append2log(f"You: {request}\n")
                print(f"You: {request}\nAI: ")

                doc = process_text(request)

                if "chat log" in request:
                    chat_log = get_chat_log()
                    speak_text("Here is the chat log for today.")
                    speak_text(chat_log)
                    append2log("AI: Provided chat log.\n")
                elif "temperature" in request or "weather" in request:
                    weather_response = get_weather()
                    speak_text(weather_response)
                elif "news" in request:
                    headlines = get_news()
                    speak_text(responses["news"])
                    for i, headline in enumerate(headlines, 1):
                        speak_text(f"Headline {i}: {headline}")
                elif "call" in request:
                    speak_text("Who would you like to call?")
                    person = rec.recognize_google(rec.listen(source1))
                    append2log(f"Call: {person}")
                    speak_text(f"Calling {person} is not supported currently.")
                elif "play song" in request or "play music" in request:
                    speak_text("Which song or video would you like to play?")
                    media = rec.recognize_google(rec.listen(source1))
                    append2log(f"Play song or video: {media}")
                    pywhatkit.playonyt(media)
                    speak_text(responses["songs"].format(media=media))
                elif "play video" in request or "play a video" in request:
                    speak_text("Which video would you like to play?")
                    media = rec.recognize_google(rec.listen(source1))
                    append2log(f"Play video: {media}")
                    pywhatkit.playonyt(media)
                    speak_text(responses["videos"].format(media=media))
                elif "information" in request or "who is" in request:
                    speak_text("You want information related to which topic?")
                    topic = rec.recognize_google(rec.listen(source1))
                    append2log(f"Information: {topic}")
                    response = generate_response(topic)
                    speak_text(response)
                elif "search" in request:
                    speak_text("What do you want me to search for?")
                    query = rec.recognize_google(rec.listen(source1))
                    append2log(f"Search: {query}")
                    pywhatkit.search(query)
                    speak_text(responses["searching"].format(query=query))
                elif "fact" in request:
                    fact = randfacts.get_fact()
                    append2log("Random fact request")
                    speak_text(f"Did you know that {fact}")
                elif "joke" in request:
                    jokes = get_joke()
                    for joke_item in jokes:
                        setup, punchline = joke_item['setup'], joke_item['punchline']
                        speak_text("Okay get ready for some chuckles")
                        append2log("Joke request")
                        speak_text(setup)
                        speak_text(punchline)
                else:
                    speak_text(responses["default"])

            except Exception as e:
                continue

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = process_message(user_message)
    return jsonify({'response': response})

def process_message(message):
    doc = process_text(message)
    return "This is a placeholder response."

if __name__ == '__main__':
    main()
    app.run(debug=True)
