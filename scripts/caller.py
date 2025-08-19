from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os, json
from dotenv import load_dotenv
from tools import tool_schemas, call_tool
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

SYSTEM_INSTRUCTIONS = """
You are an AI assistant meant for quickly synthesizing data and giving concise summaries of weather and fire behavior forcasts.
You have access to the 'fetch_url' tool. If given a prompt asking for information about weather forcasting or
fire behavior you are to us the query_links tool to find a url for a webpage with the relevant data, and then use the fetch_url
tool on that url to extract the data. Provide all links where you found relevant data first thing in your response, then give a
short summary of what the data says which answers the user's prompt.

Provide your response in html format.
"""

TEST_INSTRUCTIONS = """
Return "POST REQUEST SUCCESSFUL"
"""

@app.route("/ask", methods=["POST"])
def ask():
    print("POST request received")
    user_prompt = request.json.get("prompt")
    messages = [{"role": "system", "content": TEST_INSTRUCTIONS},
                {"role": "user", "content": user_prompt}]

    tools = [{"type": "function", "function": func} for func in tool_schemas]

    response = openai_client.chat.completions.create(
        model="o3-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    tool_calls = response_message.tool_calls

    while tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"Executing tool: {function_name} with args: {function_args}")

            function_response = call_tool(
                name=function_name,
                args=function_args
            )

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response),
                }
            )
        response = openai_client.chat.completions.create(
            model="o3-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

    return jsonify({"response": response_message.content})

if __name__ == "__main__":
    app.run(port=8000, debug=True)