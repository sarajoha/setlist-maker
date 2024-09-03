import os
import requests
from dotenv import load_dotenv

from fastapi import FastAPI

load_dotenv()
app = FastAPI()

BASE_URL = "https://api.setlist.fm/rest/"


@app.get("/search/{name}")
def search_setlist(name):
    path = f"1.0/search/setlists?artistName={name}"
    url = BASE_URL + path
    headers = {"x-api-key": os.getenv("SETLIST_API_KEY"), "accept": "application/json"}

    response = requests.get(url, headers=headers)
    print(url)
    print(headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON response directly if successful
        return response.json()
    else:
        # If the request failed, return an error response
        print(response.text)
        return {"error": "Failed to fetch data", "status_code": response.status_code}


@app.get("/get-setlist/{id}")
def fetch_setlist(id):
    path = f"1.0/setlist/{id}"
    url = BASE_URL + path
    headers = {"x-api-key": os.getenv("SETLIST_API_KEY"), "accept": "application/json"}

    # Use the requests library to perform a synchronous HTTP GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON response directly if successful
        data = response.json()
        songs_list = data.get("sets", {}).get("set", {})[0].get("song")
        print(len(songs_list))
        return songs_list
    else:
        # If the request failed, return an error response
        return {"error": "Failed to fetch data", "status_code": response.status_code}
