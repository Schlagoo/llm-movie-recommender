import json
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.imdb.com"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0.0.0 Safari/537.36',
    'accept': 'text/html',
}


def get_movies_with_some_details() -> list:
    url = f"{BASE_URL}/chart/top/?ref_=nv_mv_250"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    script = soup.select_one("script[type='application/ld+json']")
    content = json.loads(script.text)
    data = []
    for entry in content["itemListElement"]:
        data.append({
            "title": entry["item"]["name"],
            "url": entry["item"]["url"],
            "duration": entry["item"]["duration"][2:],
            "rating": entry["item"]["aggregateRating"]["ratingValue"]
        })
    
    return data

def get_further_details(url: str) -> list:
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    script = soup.select_one("script[type='application/ld+json']")
    content = json.loads(script.text)
    # Get information
    genres = content["genre"]
    timestamp = content["datePublished"] if "datePublished" in content else ""
    directors = [v["name"] for v in content["director"] if v["@type"] == "Person"]
    stars = [v["name"] for v in content["actor"]]
   
    return genres, timestamp, directors, stars


def get_synopsis(url: str) -> str:
    response = requests.get(url + "plotsummary/", headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    synopsis = soup.select("div.ipc-html-content-inner-div")[-1].get_text(strip=True)
    
    return synopsis


data = get_movies_with_some_details()
for index, movie in enumerate(data):
    url = movie["url"]
    synopsis = get_synopsis(url=url)
    genres, timestamp, directors, stars = get_further_details(url=url)
    data[index]["genres"] = genres
    data[index]["date"] = timestamp
    data[index]["directors"] = directors
    data[index]["stars"] = stars
    data[index]["synopsis"] = synopsis

with open("imdb_top250_movies.json", "w") as f:
    json.dump(data, f)
