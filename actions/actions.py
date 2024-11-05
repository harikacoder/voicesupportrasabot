import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionGetWeather(Action):

    def name(self) -> str:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        location = tracker.get_slot('location')
        if not location:
            dispatcher.utter_message(text="Please provide a location.")
            return []
        
        try:
            api_address = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid=33b2b85b934773c225dfde666c9ed0b7'
            json_data = requests.get(api_address).json()
            temperature = round(json_data["main"]["temp"] - 273.15, 1)
            description = json_data["weather"][0]["description"]
            weather_info = f"The current weather in {location} is {description} with a temperature of {temperature}°C."
        except Exception as e:
            weather_info = f"Could not fetch weather information. Error: {e}"
        
        dispatcher.utter_message(text=weather_info)
        return []


class ActionGetNews(Action):

    def name(self) -> str:
        return "action_get_news"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
       
        try:
            api_key = "c3de44ca3efa473f8ee154228a0f1c91"
            url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={ "c3de44ca3efa473f8ee154228a0f1c91"}'
            response = requests.get(url)
            news_data = response.json()
            articles = news_data['articles']
            headlines = [article['title'] for article in articles[:5]]
            news_info = "Here are the latest headlines:\n" + "\n".join(headlines)
        except Exception as e:
            news_info = f"Could not fetch news information. Error: {e}"
        
        dispatcher.utter_message(text=news_info)
        return []


class ActionGetJokes(Action):

    def name(self) -> str:
        return "action_get_jokes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        url = 'https://official-joke-api.appspot.com/random_joke'
        json_data = requests.get(url).json()
        setup = json_data["setup"]
        punchline = json_data["punchline"]
        
        joke_info = f"Here's a joke for you:\n{setup}\n{punchline}"
        dispatcher.utter_message(text=joke_info)
        return []
