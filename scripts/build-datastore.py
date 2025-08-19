import weaviate
import weaviate.classes.config as wvc
from weaviate.classes.config import Property, DataType
from weaviate.util import generate_uuid5
import os
from dotenv import load_dotenv

dotenv_path = "/home/ubuntu/fire-behavior/.env"
load_dotenv(dotenv_path)
COLLECTION_NAME = "FireBehavior"
COHERE_API_KEY = os.environ["COHERE_API_KEY"]

Webpages = {
    ("Homepage for the Southwest Coordination Center", "https://gacc.nifc.gov/swcc/"),
    ("Predictive intelligence services", "https://gacc.nifc.gov/swcc/predictive/intelligence/intelligence.htm"),
    ("SW Morning Situation Report", "https://gacc.nifc.gov/swcc/predictive/intelligence/daily/SWCC_Morning_Situation_Report/SWCC_Morning_Situation_Report.htm"),
}

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
    
    print(f"Connected to Weaviate: {client.is_ready()}")

    return client

def main():
    client = get_weaviate_client()

    print("Checking if collection exists")
    if COLLECTION_NAME in client.collections.list_all():
        print("Collection exists, deleting and recreating")
        client.collections.delete(COLLECTION_NAME)  #Delete existing collection
    print("Creating collection")
    files = client.collections.create( #Create Weaviate collection
        name=COLLECTION_NAME,
        properties=[
            Property(name="url", data_type=DataType.TEXT),
            Property(name="description", data_type=DataType.TEXT),
        ],
        vectorizer_config=wvc.Configure.Vectorizer.text2vec_cohere(  #Use Cohere vectorizer
            model="embed-english-v3.0",
        ),
            generative_config=wvc.Configure.Generative.cohere( #Configure generative module
            model="command"
        )
    )
    print("Collection successfully created, adding urls")

    collection = client.collections.get(COLLECTION_NAME)

    with collection.batch.dynamic() as batch:
        for page in Webpages:
            print(f"Adding object {page[1]}")
            batch.add_object(
                {
                    "url": page[1],
                    "description": page[0]
                }
            )
            print("Successfully Added")
            if batch.number_errors > 10:
                print("Batch import stopped due to excessive errors.")

    print("Done adding objects, closing client")
    client.close()

if __name__ == "__main__":
    main()