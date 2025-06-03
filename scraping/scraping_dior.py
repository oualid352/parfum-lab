import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.fragrantica.com"
HOUSE_NAME = "Dior"
HOUSE_URL = f"{BASE_URL}/designers/Dior.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

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

# ▶ Scraping des parfums Dior
parfums_dior = get_perfumes_from_house(HOUSE_NAME, HOUSE_URL)

# ▶ Création du DataFrame
df = pd.DataFrame(parfums_dior)

# ▶ Affichage d’un aperçu
print(df.head())


# ▶ Sauvegarde dans le dossier 'data'
output_path = "parfumlab/data/parfums_dior.csv"  # si tu es dans 'scraping/'
df.to_csv(output_path, index=False)
print(f"{len(df)} parfums enregistrés dans '{output_path}'")

