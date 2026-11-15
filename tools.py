import os
import json
from datetime import datetime
import requests
from tavily import TavilyClient
from dotenv import load_dotenv
from Utilities.utilities import log

load_dotenv()

def get_current_time():
    return datetime.now().strftime("%d/%m/%Y,%H:%M:%S")

def get_weather_city(city):
    weather_url = f"https://wttr.in/{city}?format=3"
    res = requests.get(weather_url)
    return res.text

def websearch(query):
    tavily_client = TavilyClient(api_key=os.getenv("WEBSEARCH_API_KEY"))
    res = tavily_client.search(query=query,max_results=5)
    return res.get('results')

def get_user_city():
    return "kozhikode"

# Details of our tool in Tools array.
Tools = [
    {
      "type":"function",
      "function":{
          "name":"get_current_time",
          "description":"Returns the current date and time as a formatted string",
          "parameters":{"type":"object","properties":{}}
      }
    },
    {
        "type":"function",
        "function":{
            "name":"get_weather_city",
            "description":"Returns the current weather for a given city",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"The City to get the weather for"
                    }
                }
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"websearch",
            "description":"Search the internet for up-to-date information using Tavily. Use this tool whenever you need to find current information, verify facts, research a topic, discover websites, retrieve recent news, or answer questions that require information beyond your existing knowledge."
            "When searching for 'latest', 'recent', or 'current' events, always include the explicit year in the search query rather than relative words to avoid retrieving outdated or historical cycles."
            " Provide a clear and specific search query describing exactly what information you need. The tool returns relevant web search results that you can analyze, summarize, and use to formulate an accurate response. Do not use this tool for simple questions that can be answered reliably from your existing knowledge.",
             "parameters":{
                 "type":"object",
                 "properties":{
                     "query":{
                        "type":"string",
                        "description":"A clear, specific search query describing the information you want to find on the internet. Include relevant names, topics, dates, or keywords to improve search relevance.The search keywords. Replace relative words like 'latest' or 'current' with the specific calendar year."
                     }
                 },
                 "required":["query"]
             }
        }
    },
    {
          "type":"function",
          "function":{
              "name":"get_user_city",
              "description":"Returns the city of the user. Use it when the user asks 'my city' or 'my home', or 'where i live'.",
              "parameters":{"type":"object","properties":{}}
          }
        }
]

# Create a Map fn_name ->  fn
fn_name_to_fn = {
    "get_current_time":get_current_time,
    "get_weather_city":get_weather_city,
    "websearch":websearch,
    "get_user_city":get_user_city
}


# Tool calling logic for a single tool.
def run_tool(tool):
    fn_name = tool.function.name
    # Put the tool call inside Try Block to Handle exceptions
    try:
        # Get the arguments and convert it to dictionary.
        fn_args = json.loads(tool.function.arguments or "{}")
        log(f"🔧 {fn_name}({fn_args})")
        # Get the function from name.
        fn = fn_name_to_fn.get(fn_name)
        # Call the fn with the arguments unpacked
        result = fn(**fn_args)
        
    except Exception as e:
            result = f"Error while running {fn_name}:{e}"

    log(f"   ↳ {result}")
    return result