import requests
from bs4 import BeautifulSoup

url = "https://www.fragrantica.com/perfume/Les-Liquides-Imaginaires/Blanche-Bete-70189.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Trouver la div qui contient la description avec itemprop="description"
desc_div = soup.find('div', itemprop='description')

if desc_div:
    bold_tags = desc_div.find_all('b')
    if len(bold_tags) >= 2:
        nom_parfum = bold_tags[0].text.strip()
        maison = bold_tags[1].text.strip()

        print("Nom du parfum :", nom_parfum)
        print("Maison :", maison)
    else:
        print("Impossible de trouver les deux balises <b>")
else:
    print("Section description non trouvée")
