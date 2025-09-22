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
    ("Fire Incident Information", "https://gacc.nifc.gov/swcc/information/information.htm"),
    ("Arizona Wildfire Home Page", "https://wildlandfire.az.gov/"),
    ("Arizona Wildfire Situation", "https://wildlandfire.az.gov/wildfire-situation"),
    ("Arizona Wildfire Prevention", "https://wildlandfire.az.gov/wildfire-prevention"),
    ("Arizona Fire Restrictions", "https://wildlandfire.az.gov/fire-restrictions"),
    ("Southwest Area Fire Restrictions Map", "https://nifc.maps.arcgis.com/apps/dashboards/aa9ff369dd414b74b69b696b40a1d057"),
    ("Arizona Wildfire Resources", "https://wildlandfire.az.gov/wildfire-resources"),
    ("About Arizona Interagency Wildfire Prevention", "https://wildlandfire.az.gov/about-us"),
    ("New Mexico Fire Information Home Page", "https://nmfireinfo.com/"),
    ("About New Mexico Fire Information Interagency", "https://nmfireinfo.com/about/"),
    ("New Mexico Fire Information", "https://nmfireinfo.com/information/"),
    ("New Mexico Fire Restrictions", "https://nmfireinfo.com/fire-restrictions/"),
    ("New Mexico Smoke Management", "https://nmfireinfo.com/smoke-management/"),
    ("New Mexico Fire Information Links", "https://nmfireinfo.com/links/"),
    ("Incident Map", "https://inciweb.wildfire.gov/"),
    ("Dispatch Operations", "https://gacc.nifc.gov/swcc/dispatch_logistics/dispatch/dispatch.htm"),
    ("Aviation Operations", "https://gacc.nifc.gov/swcc/dispatch_logistics/aviation/aviation.htm"),
    ("Southwest Tactical Crews", "https://gacc.nifc.gov/swcc/dispatch_logistics/crews/crews.htm"),
    ("Equipment and Supplies", "https://gacc.nifc.gov/swcc/dispatch_logistics/equipment/equipment_supplies.htm"),
    ("Overhead, Support, and Teams", "https://gacc.nifc.gov/swcc/dispatch_logistics/overhead/overhead.htm"),
    ("Predictive Information Services", "https://gacc.nifc.gov/swcc/predictive/intelligence/intelligence.htm"),
    ("Weather Services", "https://gacc.nifc.gov/swcc/predictive/weather/weather.htm"),
    ("Fuels and Fire Danger Information", "https://gacc.nifc.gov/swcc/predictive/fuels_fire-danger/fuels_fire-danger.htm"),
    ("Fire Outlooks", "https://gacc.nifc.gov/swcc/predictive/outlooks/outlooks.htm"),
    ("Critical Incident Stress Management", "https://gacc.nifc.gov/swcc/management_admin/cism/cism.htm"),
    ("Incident Business Management", "https://gacc.nifc.gov/swcc/management_admin/incident_business/incident_business.htm"),
    ("Safety Management", "https://gacc.nifc.gov/swcc/management_admin/safety/safety.htm"),
    ("Software Applications", "https://gacc.nifc.gov/swcc/management_admin/software/software.htm"),
    ("Training Information", "https://gacc.nifc.gov/swcc/management_admin/training/training.htm"),
    ("National Geographic Area Coordination Center Portal", "https://gacc.nifc.gov/links/links.htm"),
    ("National Interagency Coordination Center Home Page", "https://www.nifc.gov/nicc"),
    ("National Interagency Fire Center Fire News and Information", "https://www.nifc.gov/fire-information/nfn"),
    ("About Southwest Coordination Center", "https://gacc.nifc.gov/swcc/About_Us/About_Us.htm"),
    ("Southwest Coordination Center Site Disclaimer", "https://gacc.nifc.gov/swcc/Admin/Disclaimer/Site_Disclaimer.htm"),
}

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