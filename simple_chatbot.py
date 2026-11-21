# Standard Library Imports
import os
import time
from datetime import datetime
from types import SimpleNamespace
# Third-party imports
from openai import OpenAI
from dotenv import load_dotenv # To load variables in .env file
# Local modules
from tools import Tools,run_tool
from Utilities.utilities import log

load_dotenv() # Loads variables in .env file to environment variables

# OpenAI API Format is the Industry standard, that is why we use that API To call our model.
client = OpenAI(
    # Define the url to the local model
    base_url=os.environ["BASE_URL"],
    # openAI models need api key, but we are running ollama, so not needed.
    api_key=os.environ["API_KEY"]
)
# Store our conversation history in messages - Context for LLM 
# Context - User Query + Assistant Reply.
messages = []
MAX_STEPS = 5 # To Put a limit on the number of times tool calls the LLM requests.

# role : system - Sets the persona of the model.
current_date = datetime.now().strftime("%B %d, %Y")
messages.append({ # Set the behaviour of the model.
    "role":"system", 
    "content":f"""
You are a helpful AI assistant with access to web search.
Current date: {current_date}.
RULES:
1. For questions about latest, current, recent, or real-time
   information, ALWAYS use the websearch tool.
2."For questions about 'latest' events, include the current year in the search query (e.g., '2026 US midterm Senate results') to avoid retrieving prior election cycles."
3. For news, elections, weather, current events, and recent
   developments, NEVER rely solely on your training knowledge.
4. Do not invent search results or pretend you searched.
5. After receiving search results, analyze them before answering.
6. If search results are insufficient, clearly mention that.
7. For simple general knowledge questions, answer directly.
8. Keep answers concise and under 100 words.
"""
},
)

def stream_chat(history):
    stream = client.chat.completions.create(
            model=os.environ["MODEL"],
            messages=history,
            tools=Tools,
            stream=True
        )

    calls = {}
    full_response = ""
    label_printed = False

    # Streaming Started
    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Do we have content in the chunk
            if delta.content:
                content = delta.content
                if not label_printed:
                        print("🤖 Assistant: ",end="",flush=True)
                        label_printed = True
                print(content,end="",flush=True) # Response from the LLM Model : qwen3:4b
                full_response += content

            # Do we need tool calls?.
            for tc in (delta.tool_calls or []):
                obj = calls.setdefault(
                        tc.index,
                        SimpleNamespace(
                            id=None,
                            function = SimpleNamespace(
                                name="",arguments=""
                            )
                        )
                )

                if tc.id:
                        obj.id = tc.id
                if tc.function and tc.function.name:
                        obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                        obj.function.arguments += tc.function.arguments
    except KeyboardInterrupt:
         print("\n {Stopped by you}")
         calls = {}

    if label_printed:
         print() # Move to the next line after the assistants response.
    call_list = []
    for key in sorted(calls):
         call_list.append(calls.get(key))

    return full_response,call_list
def build_tool_calls_payload(tool_calls):
        """
        Converts our collected tool calls into the dict format that the 
        API expects inside an assistant message.
        """

        payload = []
        for tool in tool_calls:
                tool_call_dict = {
                "id":tool.id,
                    "type":"function",
                    "function":{
                        "name":tool.function.name,
                        "arguments":tool.arguments,
                    }
                }
                payload.append(tool_call_dict)
        return payload
# For conversation, we need a Chat Loop.
while True:
    user_query = input("👤 You: ")
    messages.append({
        "role":"user",
        "content":user_query,
    })
    # Chat stop condition.
    if user_query.lower() in ["exit","quit","bye"]:
        break
    
    # Calculate the response time in seconds
    start_time = time.monotonic()

    for step in range(MAX_STEPS):
            full_response,tool_calls = stream_chat(messages)

            #If not tool call is needed, exit the loop.
            if not tool_calls:
                break

            # Logs
            log(f" Step {step+1}: model requested {len(tool_calls)} tool call(s)")
                
            messages.append({
                 "role":"assistant",
                 "content":full_response,
                 "tool_calls":build_tool_calls_payload(tool_calls)
            })
            # Loop through the list of tools to call
            for tool in tool_calls:
                result = run_tool(tool)
                # Append the result to the history
                messages.append({
                    "role":"tool",
                    "content":str(result),
                    "tool_call_id":tool.id
                })
                
    else:
        # Ran out of steps : The model never gave the final answer.
        fallback = "Sorry, i could not finish within the step limit."  
        messages.append({
                "role":"assistant",
                "content":fallback
        })
        print(f"Assistant: {fallback}")
        continue
    
    elapsed_time = round((time.monotonic() - start_time),2)
    messages.append({
        "role":"assistant",
        "content":full_response
    })

    log(f"⏱️  Time taken :{elapsed_time} s")


