import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

BASE_URL = "https://www.fragrantica.com"

headers = {"User-Agent": "Mozilla/5.0"}

# 1. Récupérer toutes les maisons
def get_all_houses():
    url = f"{BASE_URL}/designers/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    house_links = soup.select("a[href^='/designers/']")
    houses = []
    
    for link in house_links:
        house_name = link.text.strip()
        house_url = BASE_URL + link['href']
        houses.append((house_name, house_url))
    
    return houses

# 2. Pour une maison, récupérer tous les parfums listés
def get_perfumes_from_house(house_name, house_url):
    response = requests.get(house_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    perfume_links = soup.select("a[href^='/perfume/']")
    perfumes = []

    for link in perfume_links:
        href = link['href']
        if href.endswith(".html"):
            name = link.text.strip()
            url = BASE_URL + href
            try:
                parfum_id = int(href.split("-")[-1].replace(".html", ""))
            except:
                parfum_id = None
            perfumes.append({
                "parfum": name,
                "maison": house_name,
                "url": url,
                "id": parfum_id
            })

    return perfumes
