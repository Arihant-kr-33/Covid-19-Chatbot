# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"  ada92477f59a9aabe54d3dde5cd8e0ff

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import enchant
import sys
import os
import requests
from rasa_sdk.events import SlotSet, UserUtteranceReverted, ConversationPaused
from newsapi.newsapi_client import NewsApiClient
import geocoder
from bs4 import BeautifulSoup
import re
import json


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ActionIntroduction(Action):

    def name(self) -> Text:
        return "action_introduction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello! I am COVID-19 Bot")
        myloc = geocoder.ip('me')
        coords = (myloc.latlng)
        lat = coords[0]
        longi = coords[1]
        appid= "21faada899afe449b3187027bf3b0d0d"
        request_weather_url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}".format(lat,longi,appid)
        respose_weather = requests.get(request_weather_url)
        respose_weather = respose_weather.json()
        temp = round(float(respose_weather['main']['temp'] - 273.15),3)
        pressure = respose_weather['main']['pressure']
        humidity = respose_weather['main']['humidity']
        weather_desc = respose_weather['weather'][0]['description']
        response_message = "Temparature around you is {} °C with Pressure {} hPa and Humidity {}%. The weather looks like {}.How may i help you?".format(temp,pressure,humidity,weather_desc)
        dispatcher.utter_message(text=response_message)
        title = ["COVID India Cases","Latest News","Covid Testing Centre's Near Me","Emergency Number"]
        payload = ['/mood_cases','/mood_news','/mood_testing_centre','/mood_emergency']
        buttons_show = []
        for i2 in range(0,len(title)):
            x_2 = {"title":title[i2]}
            buttons_show.append(x_2)
        dispatcher.utter_button_message(text= "", buttons=buttons_show)
        return []

class ActionStateResponse(Action):

    def name(self) -> Text:
        return "action_state_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        response = requests.get("https://api.covid19india.org/data.json").json()

        state_name = str((tracker.latest_message)['text'])
        state_name = state_name.lower()
        print(state_name)
        states_dict = enchant.PyPWL("states.txt")
        word_exists = states_dict.check(state_name)
        print("word exists: ", word_exists)
        if not word_exists:
            #get suggestions for the input word
            suggestions = states_dict.suggest(state_name)
            print ("input:", state_name)
            print("suggestions:", suggestions)
            if(len(suggestions)!= 0):
                state_name = suggestions[0]

        #state = None
        entities = tracker.latest_message['entities']
        print(entities)

        #for e in entities:
        #    if(e['entity'] == "state"):
        #        state = e['value']
        #message = "Enter proper state name"
        for data in response["statewise"]:
            if data["state"].lower() == state_name.lower():
                print("1.Active = " + data["active"] + "\n2.Confirmed = "+ data["confirmed"] + "\n3.Deaths = "+ data["deaths"] + "\n4.Recovered = "+ data["recovered"] )
                message = "1.Active = " + data["active"] + "\n2.Confirmed = "+ data["confirmed"] + "\n3.Deaths = "+ data["deaths"] + "\n4.Recovered = "+ data["recovered"] 
                active = int(data["active"])
                confirmed = int(data["confirmed"])
                deaths = int(data["deaths"])
                recovered = int(data["recovered"])
                print(active)

        labels = ['Active','Confirmed','Deaths','Recovered']
        backgroundColor = ["#36a2eb","#ffcd56","#ff6384","#009688","#c45850"]
        #chartsData = [555,242,145,23]
        chartsData = []
        chartsData.extend((active,confirmed,deaths,recovered))
        data = {"title":state_name.upper(),"labels":labels,"backgroundColor":backgroundColor,"chartsData": chartsData,"chartType":"pie","displayLegend":"true"}
        dispatcher.utter_message(state_name.title())
        dispatcher.utter_message(message)
        #dispatcher.utter_custom_json({"payload":"chart","data":data})

        return []

class ActionShowNewsIndia(Action):

    def name(self) -> Text:
        return "action_show_news_india"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        newsapi = NewsApiClient(api_key='50f272bcae1f4491b90864cad6f20628')
        top_headlines = newsapi.get_top_headlines(q='COVID-19 India',language='en',)
        ans=""
        for i,article in enumerate(top_headlines['articles']):
            ans+=str(i+1)+". " + article['title'].title() +'\n'
            #dispatcher.utter_message(str(article['title']))
            print("Title : ", article['title'])
            ans+=str(article['description'])+"\n"+"For more info click here: "+article['url']+"\n\n\n"
            #dispatcher.utter_message(str(article['description']))
            print("Description : ",article['description'])
        dispatcher.utter_message(ans)
        hyperlink_format = '<a href = "{link}" target="_blank">{text}</a>'
 
        # list1 = []
        # for article in top_headlines['articles']:
        #     description = str(article['description'])
        #     hyperlink_format = '<a href = "{link}" target="_blank">{text}</a>'
        #     hyperlink_format = hyperlink_format.format(link = article['url'],text = 'here')
        #     hyperlink_message = ". Click " + hyperlink_format + " to read enitre article"
        #     description = description + hyperlink_message
        #     #print(description)
        #     x = {"title":article['title'],"description":description}
        #     list1.append(x)
        # dispatcher.utter_custom_json({"payload":"collapsible","data":list1})

        return []


class ActionShowNewsWorld(Action):

    def name(self) -> Text:
        return "action_show_news_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        newsapi = NewsApiClient(api_key='50f272bcae1f4491b90864cad6f20628')
        top_headlines = newsapi.get_top_headlines(q='COVID-19',language='en',)
        ans=""
        for i,article in enumerate(top_headlines['articles']):
            #dispatcher.utter_message(str(article['title']))
            ans+=str(i+1)+". " + article['title'].title() +'\n'
            print("Title : ", article['title'])
            ans+=str(article['description'])+"\n"+"For more info click here: "+article['url']+"\n\n\n"
            #dispatcher.utter_message(str(article['description']))
            print("Description : ",article['description'])
        dispatcher.utter_message(ans)
        hyperlink_format = '<a href = "{link}" target="_blank">{text}</a>'
 
        # list1 = []
        # for article in top_headlines['articles']:
        #     description = str(article['description'])
        #     hyperlink_format = '<a href = "{link}" target="_blank">{text}</a>'
        #     hyperlink_format = hyperlink_format.format(link = article['url'],text = 'here')
        #     hyperlink_message = ". Click " + hyperlink_format + " to read enitre article"
        #     description = description + hyperlink_message
        #     #print(description)
        #     x = {"title":article['title'],"description":description}
        #     list1.append(x)
        # dispatcher.utter_custom_json({"payload":"collapsible","data":list1})

        return []

class ActionShowTestingCentre(Action):

    def name(self) -> Text:
        return "action_show_testing_centre"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # myloc = geocoder.ip('me')
        # print(myloc.city)
        # url = "https://www.google.com/maps/search/{}+covid+testing+centres/".format(myloc.city)
        # r = requests.get(url)
        # string_1 = re.findall(r"null,\\(.*?)Owner",r.text)
        
        # print(r.text)

        # covid_list_name = []
        # for i in string_1:
        #     string_2 = i.rsplit("\\",1)
        #     string_3 = string_2[1]
        #     string_3 = string_3[1:]
        #     string_3 = string_3[:-1]
        #     string_3 = string_3.strip()
        #     covid_list_name.append(string_3)
        # covid_list_directions = []
        # for name in covid_list_name:
        #     replaced = name.replace(" ","+")
        #     url_directions = "https://www.google.co.in/maps/dir//{}".format(replaced)
        #     covid_list_directions.append(url_directions)
        
        # final_hospital_address = []
        # for i1 in string_1:
        #     string_2_dir = i1.rsplit("\\n,null,\\",1)
        #     # print(f"Length of string_2_dir: {len(string_2_dir)}")
        #     #print("OK")
        #     string_3_dir = string_2_dir[1]
        #     string_4_dir = string_3_dir.split("\\")[0]
        #     string_4_dir = string_4_dir[1:]
        #     final_hospital_address.append(string_4_dir)
                

        # final_list_hospitals = []
        # i=1
        # x=""
        # for k in range(0, min(len(final_hospital_address), len(covid_list_directions))):
        #     hyperlink_format = 'For directions click here: '+covid_list_directions[k]+'\n'
        #     #hyperlink_format = hyperlink_format.format(link = covid_list_directions[k])
        #     #hyperlink_message = ". Click " + hyperlink_format + " for directions"
        #     desc = final_hospital_address[k] +"\n"+ hyperlink_format
        #     desc = " Address : " +desc
        #     x += "\n"+str(i)+". "+covid_list_name[k].upper()+"\n"+desc+"\n\n"
        #     final_list_hospitals.append(x)
        #     i=i+1
        # dispatcher.utter_message(x+'\n'+'\n')
        myloc = geocoder.ip('me')
        data = requests.get("http://api.serpstack.com/search?access_key=08796fb783fb4c02b39e329585e06f12&query=covid+test+centre+{}".format(myloc.city))
        json_data = data.json()

        test_centres=""
        print("NEAREST TESTING CENTRES\n")
        x = "NEAREST TESTING CENTRES\n\n"
        dispatcher.utter_message(x)
        for result in json_data["local_results"]:
            test_centres += "\n"+(str)(result["position"])+". "+result["title"] + "\nAddress: "+result["type"]+"\nLocation: "+(str)(result["coordinates"]["latitude"])+", "+(str)(result["coordinates"]["longitude"])+"\n\n"
        print(test_centres)
        dispatcher.utter_message(test_centres)

        other_sites=""
        print("\nOTHER USEFUL RESOURCES\n\n")
        y = "\nOTHER USEFUL RESOURCES\n\n"
        dispatcher.utter_message("\n")
        dispatcher.utter_message(y)
        for result in json_data["organic_results"]:
            other_sites += "\n"+(str)(result["position"])+". "+result["title"] + "\nFor More Information click here: "+result["url"]+"\n\n"
        print(other_sites)
        dispatcher.utter_message(other_sites)
        #dispatcher.utter_custom_json({"payload":"collapsible","data":json_data})

        return []