import requests
import os
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
    }
]

def get_weaviate_client():
    client = weaviate.connect_to_custom(
        http_host="128.196.65.212",
        http_port=8081,
        http_secure=False,
        grpc_host="128.196.65.212",
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

        return "https://gacc.nifc.gov/swcc/predictive/intelligence/daily/SWCC_Morning_Situation_Report/SWCC_Morning_Situation_Report.htm"
    
    except Exception as e:
        print("Weaviate query failed")
        return []
    finally:
        client.close()


def fetch_url(args):
    url = args["url"]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return { "content": text[:5000] }

def call_tool(name, args):
    if name == "query_links":
        return query_links(args)
    elif name == "fetch_url":
        return fetch_url(args)
    else:
        raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    get_weaviate_client()
