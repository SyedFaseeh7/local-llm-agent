import os
from openai import OpenAI
from types import SimpleNamespace
from tools import Tools,run_tool

client = OpenAI(
    base_url = os.environ["BASE_URL"],
    api_key = os.environ["API_KEY"]
)

stream = client.chat.completions.create(
    model=os.environ["MODEL"],
    messages=[{
         "role":"user",
         "content":"Hi, can you get me the weather in Kerala and Delhi"
    }
    ],
    tools=Tools,
    stream=True
)

calls = {} # index - a tool object.

# Process Chunks.
for chunk in stream:
    if not chunk.choices:     # Some servers send chunks with no choices.
           continue

    delta = chunk.choices[0].delta

    for tool in (delta.tool_calls or []):
        # check if our dict already recieved a chunk of the tool with the curr tool index.
        obj = calls.setdefault(
             tool.index,
             SimpleNamespace(
                  id=None,
                  function= SimpleNamespace(
                       name="",arguments=""
                  )
             )
        )

        if tool.id:
             obj.id = tool.id
        if tool.function and tool.function.name:
             obj.function.name += tool.function.name
        if tool.function and tool.function.arguments:
             obj.function.arguments += tool.function.arguments

call_list = []
for key in sorted(calls):
     call_list.append(calls[key])

        