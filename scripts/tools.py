import requests
import os
import json
from dotenv import load_dotenv
import weaviate
import weaviate.classes as wvc
from bs4 import BeautifulSoup

dotenv_path = "/home/ubuntu/fire-behavior/.env"
load_dotenv(dotenv_path)
COHERE_API_KEY = os.environ["COHERE_API_KEY"]

tool_schemas = [
    {
        "name": "query_links",
        "description": "Searches Weaviate for relevant links.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": { "type": "string", "description": "Search query" }
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetches and extracts readable content from a web page.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": { "type": "string", "description": "A webpage URL to extract from" }
            },
            "required": ["url"]
        }
    },
    {
        "name": "national_weather",
        "description": "Retreives weather data and alerts at a specific latitude and longitude.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": { "type": "string", "descriptions": "The latitude coordinate to get weather information from." },
                "longitude": { "type": "string", "descriptions": "The longitude coordinate to get weather information from." }
            },
            "required": ["latitude", "longitude"]
        }
    }
]

def get_weaviate_client():
    client = weaviate.connect_to_custom(
        http_host="128.196.254.74",
        http_port=8081,
        http_secure=False,
        grpc_host="128.196.254.74",
        grpc_port=50051,
        grpc_secure=False,
        headers={"X-Cohere-Api-Key": COHERE_API_KEY}
    )

    print(f"Connected to Weaviate client: {client.is_ready()}")

    return client

def query_links(args):
    client = get_weaviate_client()

    try:
        print("Finding collection")
        collection = client.collections.get("FireBehavior")

        print("Making query")
        response = collection.query.hybrid(
            query=args["query"],
            limit=2
        )

        print(f"Weaviate query successful: {response}")

        serializable_data = []
        for obj in response.objects:
            serializable_data.append(obj.properties) 

        return json.dumps(serializable_data)
    
    except Exception as e:
        print("Weaviate query failed")
        return []
    finally:
        client.close()


def fetch_url(args):
    url = args["url"]
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        raw_html = response.text

        print(raw_html[:10000])
        return { "content": raw_html }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return { "content": f"Error: Could not fetch content from {url}. {e}" }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return { "content": f"Error: An unexpected error occurred while fetching {url}. {e}" }
    
def national_weather(args):
    lat = args["latitude"]
    lon = args["longitude"]
    weather_url = f"https://api.weather.gov/points/{lat},{lon}"

    try:
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()

        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data from {weather_url}: {e}")
        return { "content": f"Error: Could not fetch content from {weather_url}. {e}" }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return { "content": f"Error: An unexpected error occurred while fetching {weather_url}. {e}" }

def call_tool(name, args):
    if name == "query_links":
        return query_links(args)
    elif name == "fetch_url":
        return fetch_url(args)
    elif name == "national_weather":
        return national_weather(args)
    else:
        raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    get_weaviate_client()
