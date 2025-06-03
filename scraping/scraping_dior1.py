import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# -------------------------------
# CONFIGURATION
# -------------------------------
BASE_URL = "https://www.fragrantica.com"
HOUSE_NAME = "Dior"
HOUSE_URL = f"{BASE_URL}/designers/Dior.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# -------------------------------
# FONCTION : RÉCUPÉRER LES PARFUMS DE LA MAISON
# -------------------------------
def get_perfumes_from_house(house_name, house_url):
    response = requests.get(house_url, headers=HEADERS)
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

# -------------------------------
# FONCTION : EXTRAIRE LE(S) CRÉATEUR(S)
# -------------------------------
def get_createur_from_parfum_page(url):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Liste finale des créateurs
        createurs = []

        # Cherche tous les liens vers des fiches /noses/
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            nom = tag.text.strip()

            if href.startswith('/noses/') and nom not in {"Perfumers", "Perfumer", "", "Nose"}:
                createurs.append(nom)

        return ", ".join(createurs) if createurs else None

    except Exception as e:
        print(f"  ⚠️ Erreur lors de l’extraction du créateur : {e}")
        return None

# -------------------------------
# EXÉCUTION DIRECTE
# -------------------------------
print(f"📦 Scraping des parfums de la maison {HOUSE_NAME}...")

# Étape 1 : récupérer les parfums
parfums = get_perfumes_from_house(HOUSE_NAME, HOUSE_URL)
print(f"✅ {len(parfums)} parfums trouvés.")

# Étape 2 : récupérer les créateurs
for parfum in parfums:
    print(f"🔍 {parfum['parfum']}")
    createur = get_createur_from_parfum_page(parfum['url'])
    parfum['createur'] = createur
    print(f"   ➤ Créateur : {createur}")
    time.sleep(1)

# Étape 3 : créer la table
df = pd.DataFrame(parfums)

# Étape 4 : sauvegarder dans le dépôt data
output_path = "data/parfums_dior.csv"
df.to_csv(output_path, index=False)
print(f"💾 Données enregistrées dans : {output_path}")
