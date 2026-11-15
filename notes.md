# This is my Learning Notes.

### Virtual Environment
#### A Virtual Environment (venv) is an isolated space for a Python project where you can install its own packages without affecting other projects.

### To create a venv
In your project folder, run:
py -3.14 -m venv .venv
### To activate it on Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

### OpenAI API Standard
#### We use the OpenAI Python SDK to make API calls to our local Ollama model. Ollama supports the OpenAI-compatible API format, allowing us to use the same SDK and API-call structure with different compatible models and providers.

### Role
#### Role helps to identify the speaker 
| Role | Identity|
|:------:|:----:|
| user  |we the  users|
|assistant|  the model own replies|
|system |Hidden instructions that set the AI model's behaviour|
<hr>

#### Conversation Loop
To make the chat feel like a conversation, add a Loop. Chat Loop.
<hr>

### Give LLM Context.
**LLM's are Stateless** - They don't have memory.

#### Then how do they remember our earlier conversations?
 Every API Call is a brand new for the LLM once the call ends, it's over. Then how it remembers earlier messages?

 <u>*<b>Every time you send a Query, internally along with it your entire conversation history(your query and model replies) also gets appended, and sometimes system instructions also and that becomes the full "Prompt"/"Context"</b></u>

**Prompt = Query + History + System instructions => "Conext" for the LLM**

There is a limit on the context it can read = 

**Context Window (Measured in tokens)**

Sometimes when the conversation becomes too long, it may loose some context because of the context window limit, so to tackle this models use these techniques
- Skip some chats
- Summarize the history and append (compact)
- Fetch context from external DB - Vector DB, when needed (RAG)
<hr>

#### Give LLM A Persona
To set **models Behaviour** we can **give prompt as  system (role:system)**. System instructions should be top level before any other messages.
<hr>

#### Make LLM Use Tools.
It is a feature of LLM APIs where <u>**we
describe our functions(tools) to the model**</u>, and the <u>**model**</u> instead of  answering, can <u>**reply with a request to call one of those fns with specific arguments.
Our code then runs the fn and gives the output of the fn call as request back to the model and the model gives the final output**.</u>

**LLM Does not run the fn. It only says which fn it wants the code to run**.

<u>**LLM gets to know about our tools(fns) because we send it along the query**</u>.

Tools = [{Tool1},{Tool2},...]

**Two API calls for one user query**

1. To get which tool to use.
2. To get final response after tool call finishes.

**Model Itself decides if tool call is needed, and which tool is needed**
(This is the Intelligent part where LLM is helping us with)

We can define the tools in a seperate file.

<u>**Model cannot see our code**</u><br>
We need to send details of our fn(tool) to the model

**Flow**
1. First we send messages + Tools.
2.  Fetch the message from response.
3. if message has tool_calls not None, then we need to make a tool call.
4. Append the msg to history
5. Go through the tool_calls list
6. Get each tool name and arguments
7. Convert arguments(JSON String '{}') to dictionary
8. Call the actual fn with the arguments
unpacked using ** operator.<br>
   **result = fn(args)**
9. Append the result to the message history with role:"tool"
10. Call the LLM again.
<hr>

#### Parallel Vs Sequential Tool Calling.
Parallel Tool calling - Calling multiple tools at a time.<br>

Sequential Tool Calling(**<u>Chained Tool</u>** calling) - When one tool call depends on the result of the other. Execute one tool call at a time.

### Agentic Loop
Add a loop to call tools as long as the model requests.
Before adding agentic loop - Chained tool call, our agent can only do parallel tool calling.

But if oone tool call depends on the result of the other, we have not added that capability.

So what happens is -:
1. Agent tells to call one tool and waits for its result.
2. Once it gets the result, it tells to make another call,but as there is no loop and we are only checking if the agent requests for tool call in 1st call, the dependant tool calls are not made and we get an empty response as the agent has not completed the process, but we are printing the response.
3. We print response, the response is " ".

So we need a loop to call tools as long as the model requests.
This loop is Called - **<u>Agentic Loop</u>**.

### Exception Handling
What if a tool call fails? it might affect the other tool calls and program may crash.
So we need to acknowledge this and catch the error and append the error to message history as role : tool.

That is why we put the tool call logic in
Try-Except block, to catch the exceptions.

Chained tool calling can run indefinetly - if the model keeps asking for tool calls, it will run forever.

To Handle it, we can add a limit on the loop - a limited for loop. So if the limit exceeds we can stop the loop and give response to user with a fallback message saying that the model can't complete the response within the step limit.

#### Other Limitations
- If a Tool call returns wrong result, then the tools dependant on its result may carry the wrong result and the final output also will be wrong.

- Small models may not be that intelligent , so the order of tool call in chained tool calling may not be the best order. This is a model-level limitation.
Small models struggle with multi-step planning.

- **Prompt Injection** - Let's say we have a tool which searches web.
And say it searches a website which has malicious code in it and it returns the result and that malicious result gets passed to LLM and then it takes its action. This is a security limitation.
<hr>

#### ANSI Escape codes.
special sequences of characters embedded in text that control terminal display features like text colors, font styles (such as bold or underline), and cursor movement

Working:
1. An ANSI escape sequence starts with an Escape character (ESC), represented as \033 or \x1b.
2. It is followed by [ (Control Sequence Introducer).
3. Parameters specify the action to perform.
4. The final character determines the operation.

Example:

print("\033[31mHello World\033[0m")

- \033 – Escape character.
- [ – Begins the control sequence.
- 31m – Changes text color to red.
- \033[0m – Resets text formatting to default.
- 0 – Parameter that resets all text formatting to default.
- m – Final character indicating a text formatting (SGR) command.The letter m indicates the end of the ANSI formatting command and tells the terminal to apply the specified formatting.

#### Common ANSI Escape Codes:
Code	Function : 
- \033[31m	Red text
- \033[32m	Green text
- \033[33m	Yellow text
- \033[34m	Blue text
- \033[1m	Bold text
- \033[90m - Grey text

Applications:
- Displaying colored text in terminals.
- Highlighting important messages.
- Creating command-line interfaces.
- Controlling cursor position.
- Clearing and updating terminal screens

In short: ANSI escape codes allow programs to control the appearance and behavior of terminal output using special character sequences.
<hr>

#### Add Streaming to Agent.
Make the response appear as word by word(token by token)

**Streaming** -> Real time continuous generation and flow of data from diverse sources, captured and processed as it arrives rather than stored in large batches(Data arrives as segments(small pieces)).

To make our agent stream response, in the agent call add stream = True.<br>
Right now we print the response after all the segments are recieved, that is why it feels like the response is taking time.
Right now, our program waits for complete response, then prints it.

Wait 10 sec to see full response X.<br>
First Word appears in 1-2 seconds - Yes.

Streaming does not make the model faster , total time taken to respond is still the same, what improves is the <u>*Time to see the first word*</u>

**TTFT(Time to First Token)** -

TTFT is the duration between sending a prompt to a LLM and recieving the first piece of output.It measures how quickly an AI system transitions from Idle to Active,
**Directly shaping the users <u>perception of speed and responsiveness**</u>.

Once streaming is on, we need to process the chunks accordingly.

**Stream Processing**.