from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="test"
)

messages = [{"role" : "user", "content" : "Whats the current weather in sibiu ? What is the current weather in new york ? "},

]



def get_current_weather(lat,lon):

    try:

        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={os.getenv("WEATHER_API")}')

        if response.status_code != 200:
            raise Exception(f"Endpoind responded with an error : {response.status_code}")
        else:
            data = response.json()
            return f'Current weather of the city {data["name"]}: {data['weather'][0]['description']}  temperature : {data["main"]['temp']} other info : {data["wind"]}'

    except Exception as ex:
        return f'There was an error {ex}'




tools = [{
    "type" : "function",
    "function" : {
        "name" : "get_current_weather",
        "description" : "Get the current weather of a city",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "lat" : {
                    "type" : "string",
                    "description" : "The latitude of the prompted city i.e 40.7128, 48.8566 "
                },
                "lon" :{
                    "type" : "string",
                    "description" : "The longitude of the prompted city i.e 2.3522,139.6503 "
                }
            },
            "required": ["lat","lon"]
            
        },

        
                
    }
}]

response = client.chat.completions.create(
    model="qwen3:8b",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)




response_message = response.choices[0].message


print("\nFirst response",response_message)

tool_calls = response_message.tool_calls

messages.append(response_message)

current_functions = {
    "get_current_weather" : get_current_weather,
}



for tool in tool_calls:
    function_name = current_functions[tool.function.name]
    function_args = json.loads(tool.function.arguments)
    function_response = function_name(function_args["lat"],function_args["lon"])
    tool_message = {

    "tool_call_id" : tool.id,
    "role" : "tool",
    "name" : "get_current_weather",
    "content" : function_response

}
    messages.append(tool_message)











second_response = client.chat.completions.create(
    model="qwen3:8b",
    messages=messages
)

print("\nFinal Response",second_response.choices[0].message.content)









