import os

from openai import OpenAI
from dotenv import load_dotenv
import requests
from requests import RequestException
import json
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print(os.getenv("OPENAI_API_KEY"))
app = FastAPI()

function_description = [
    {
      "name": "coin_data",
      "parameters": {
        "type": "object",
        "properties": {
          "coin_name": {
            "type": "string",
            "description": "The name of the coin or list of coins we need details about."
          }
        },
        "required": [
          "coin_name"
        ]
      },
      "description": "Get data about a coin from just the coin name"
    }
]

# question = "What is the current market cap of bitcoin?"
# prompt = f"Extract coin names from: {question}. Then answer the question"
#
# completion = client.chat.completions.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": question}],
#     functions=function_description,
#     function_call="auto"
# )
#
# output = completion.choices[0].message

def coin_data(coin_name):
    try:
        # Make a GET request to the API
        response = requests.get(url=f"https://api.coingecko.com/api/v3/coins/markets", params={"vs_currency":"usd", "ids":f"{coin_name}"}) #

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse and return the JSON response
            return (f"The live data about {coin_name}: {json.dumps(response.json())}")
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except RequestException as e:
        # Handle exceptions (e.g., timeout, connection error)
        print(f"Error: {e}")
        return None


# coin_name = str(json.loads(output.function_call.arguments).get("coin_name")).lower()
#
# print(coin_name)
#
# coinInfo = coin_data(coin_name)
# print(coinInfo)
#
# second_completion = client.chat.completions.create(
#     model="gpt-4",
#     messages=[
#         {"role": "user", "content": prompt},
#         {"role": "function", "name": output.function_call.name, "content": coinInfo},
#     ],
#     functions=function_description,
# )
# response = second_completion.choices[0].message.content
# print(response)

class Question(BaseModel):
    content: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def get_answer(question: Question):
    quesn = question.content
    prompt = f"Extract coin names from: {quesn}. Then answer the question"

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": quesn}],
        functions=function_description,
        function_call="auto"
    )

    output = completion.choices[0].message

    coin_name = str(json.loads(output.function_call.arguments).get("coin_name")).lower()

    print(coin_name)

    coinInfo = coin_data(coin_name)
    print(coinInfo)

    second_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "function", "name": output.function_call.name, "content": coinInfo},
        ],
        functions=function_description,
    )
    response = second_completion.choices[0].message.content
    print(response)

    return {"response": response}