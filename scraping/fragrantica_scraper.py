import requests
from bs4 import BeautifulSoup

import re

# 1. UTILITAIRES #

def get_soup(url):
    """
    Récupère et parse le contenu HTML d'une page Fragrantica.

    Args:
        url (str): URL complète du parfum.

    Returns:
        BeautifulSoup: objet parseur de la page HTML, ou None si erreur.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Erreur {response.status_code} sur l'URL : {url}")
        return None

# 2. INFOS GENERALES PARFUM #

def get_id_parfum(url):
    """
    Extrait l'identifiant numérique du parfum à partir de son URL Fragrantica.

    Args:
        url (str): URL du parfum.

    Returns:
        str or None: identifiant du parfum (ex: '70189'), ou None si non trouvé.
    """
    try:
        match = re.search(r"-(\d+)\.html$", url)
        if match:
            return match.group(1)
    except Exception as e:
        print("Erreur dans get_id_parfum :", e)
    return None

def get_nom_parfum(soup):
    """
    Extrait le nom du parfum depuis la section de description.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        str or None: nom du parfum, ou None si non trouvé.
    """
    try:
        desc_div = soup.find('div', itemprop='description')
        if desc_div:
            bold_tags = desc_div.find_all('b')
            if len(bold_tags) >= 1:
                return bold_tags[0].text.strip()
    except Exception as e:
        print("Erreur dans get_nom_parfum :", e)
    return None

def get_maison(soup):
    """
    Extrait le nom de la maison de parfum depuis la description.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        str or None: nom de la maison, ou None si non trouvé.
    """
    try:
        desc_div = soup.find('div', itemprop='description')
        if desc_div:
            bold_tags = desc_div.find_all('b')
            if len(bold_tags) >= 2:
                return bold_tags[1].text.strip()
    except Exception as e:
        print("Erreur dans get_maison :", e)
    return None

def get_parfumeurs(soup):
    """
    Extrait la liste des parfumeurs (noses) d'un parfum, s'ils sont mentionnés.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        list: liste des noms de parfumeurs uniques (str), vide si non trouvés.
    """
    try:
        # Étape 1 : trouver le conteneur principal des parfumeurs
        container = soup.find("div", class_="grid-x grid-padding-x grid-padding-y small-up-2 medium-up-2")
        if not container:
            return []

        # Étape 2 : chercher tous les <a> à l’intérieur de ce conteneur uniquement
        links = container.find_all("a", href=lambda href: href and "/noses/" in href)

        # Étape 3 : extraire le texte unique
        names = list({a.text.strip() for a in links if a.text.strip().lower() != "perfumers"})
        return names
    except Exception as e:
        print("Erreur dans get_parfumeurs :", e)
        return []


    """
    Extrait la liste des parfumeurs (noses) d'un parfum, sur Fragrantica (FR ou EN).

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        list: liste des noms de parfumeurs uniques (str), vide si non trouvés.
    """
    try:
        # Cherche tous les liens vers des profils de nez
        links = soup.find_all("a", href=lambda href: href and "/noses/" in href)
        
        # On extrait uniquement le texte des <a> sans doublons
        seen = set()
        names = []
        for a in links:
            name = a.text.strip()
            if name and name not in seen:
                names.append(name)
                seen.add(name)
        
        return names
    except Exception as e:
        print("Erreur dans get_parfumeurs :", e)
        return []

def get_image_url(soup):
    """
    Extrait l'URL de l'image principale du parfum.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        str or None: URL de l'image (format JPG), ou None si non trouvée.
    """
    try:
        # Recherche la première grande image du parfum
        img = soup.find("img", src=lambda s: s and "mdimg/perfume/" in s)
        if img:
            return img['src']
    except Exception as e:
        print("Erreur dans get_image_url :", e)
    return None


    """
    Extrait la description Fragrantica associée au parfum.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        str or None: description du parfum, ou None si non trouvée.
    """
    try:
        desc_div = soup.find('div', itemprop='description')
        if desc_div:
            return desc_div.get_text(strip=True)
        else:
            return None
    except Exception as e:
        print("Erreur dans get_description :", e)
        return None

def get_description(soup):
    """
    Extrait la description principale du parfum (sans les langues).

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        str or None: description propre du parfum.
    """
    try:
        desc_div = soup.find('div', itemprop='description')
        if not desc_div:
            return None

        first_p = desc_div.find('p')
        if not first_p:
            return None

        # Récupérer toutes les chaînes de texte proprement, même à l'intérieur de balises
        return ' '.join(first_p.stripped_strings)

    except Exception as e:
        print("Erreur dans get_description :", e)
        return None

def get_date(soup):
    """
    Extrait l'année de lancement du parfum à partir de la description.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        str or None: année de lancement (ex: '2023'), ou None si non trouvée.
    """
    try:
        desc_text = get_description(soup)
        if not desc_text:
            return None
        
        match = re.search(r"a été lancé en (\d{4})", desc_text)
        if match:
            return match.group(1)
    except Exception as e:
        print("Erreur dans get_year_from_description :", e)
    
    return None

# 3. COMPOSITION PARFUM #

def get_famille(soup):
    """
    Extrait la famille olfactive (ex: Cuir, Oriental, Floral, etc.) depuis la description.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        str or None: nom de la famille olfactive si trouvée, sinon None.
    """
    try:
        description = get_description(soup)
        if not description:
            return None

        # Cherche la structure "... est un parfum XYZ pour ..."
        match = re.search(r"est un parfum (.+?) pour", description, re.IGNORECASE)
        if match:
            famille = match.group(1).strip()
            return famille.capitalize()  # majuscule initiale pour l’esthétique
    except Exception as e:
        print("Erreur dans get_famille_from_description :", e)

    return None

def get_accords(soup):
    """
    Extrait les accords principaux du parfum avec leur poids en pourcentage depuis Fragrantica.fr.

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page.

    Returns:
        list of tuples: liste [(accord, pourcentage)], ex: [("oud", 100), ("fruité", 98), ...]
    """
    try:
        accords = []
        accord_divs = soup.find_all("div", class_="accord-bar")

        for div in accord_divs:
            nom_accord = div.text.strip().capitalize()
            style = div.get("style", "")
            match = re.search(r"width:\s*([\d\.]+)%", style)
            if match:
                pourcentage = round(float(match.group(1)))
                accords.append((nom_accord, pourcentage))

        return accords

    except Exception as e:
        print("Erreur dans get_accords_principaux :", e)
        return []


    """
    Extrait les notes dominantes si la pyramide olfactive n’est pas présente.

    Returns:
        list: notes globales (sans distinction)
    """
    try:
        note_divs = soup.find_all("div", class_="note-box")
        notes = []
        for div in note_divs:
            notes += [img["alt"].strip() for img in div.find_all("img") if "alt" in img.attrs]
        return list(set(notes))
    except Exception as e:
        print("Erreur dans get_notes_globales :", e)
        return []

def split_notes(text):
    """
    Sépare une chaîne comme 'Ambre, Vanille et Cuir' en liste ['Ambre', 'Vanille', 'Cuir'].
    Gère aussi les cas avec 2 ou 1 note.

    Args:
        text (str): chaîne textuelle décrivant les notes

    Returns:
        list of str: liste de notes nettoyées
    """
    text = text.strip()
    if " et " in text:
        parts = text.rsplit(" et ", 1)
        left = parts[0]
        last = parts[1]
        notes = [n.strip().capitalize() for n in left.split(",") if n.strip()] + [last.strip().capitalize()]
    else:
        notes = [n.strip().capitalize() for n in text.split(",") if n.strip()]
    return notes

def get_notes_from_description(soup):
    """
    Extrait les notes olfactives (tête, cœur, fond) à partir de la description textuelle du parfum.

    Args:
        soup (BeautifulSoup): contenu HTML parsé.

    Returns:
        dict: dictionnaire avec clés 'notes_tete', 'notes_coeur', 'notes_fond'
    """
    description = get_description(soup)
    notes = {"notes_tete": [], "notes_coeur": [], "notes_fond": []}

    if not description:
        return notes

    try:
        tete_match = re.search(r"(?:la|les) note[s]? de tête (?:est|sont) (.+?)(?:[;\.]|$)", description, re.IGNORECASE)
        coeur_match = re.search(r"(?:la|les) note[s]? de c(?:oe|œur)r (?:est|sont) (.+?)(?:[;\.]|$)", description, re.IGNORECASE)
        fond_match = re.search(r"(?:la|les) note[s]? de fond (?:est|sont) (.+?)(?:[;\.]|$)", description, re.IGNORECASE)

        if tete_match:
            notes["notes_tete"] = split_notes(tete_match.group(1))
        if coeur_match:
            notes["notes_coeur"] = split_notes(coeur_match.group(1))
        if fond_match:
            notes["notes_fond"] = split_notes(fond_match.group(1))

    except Exception as e:
        print("Erreur dans get_notes_from_description :", e)

    return notes

# 4. AVIS PARFUM #

def get_note_moyenne(soup):
    """
    Extrait la note moyenne sur 5 du parfum à partir du champ itemprop="ratingValue".

    Args:
        soup (BeautifulSoup): HTML parsé.

    Returns:
        float or None: note moyenne (ex: 4.4) ou None si introuvable.
    """
    try:
        tag = soup.find("span", itemprop="ratingValue")
        if tag:
            return float(tag.text.strip().replace(",", "."))
    except Exception as e:
        print("Erreur dans get_note_moyenne :", e)
    return None

def get_nb_votes(soup):
    """
    Extrait le nombre de votes depuis l’attribut 'content' du champ itemprop="ratingCount".

    Args:
        soup (BeautifulSoup): HTML parsé.

    Returns:
        int or None: nombre de votes, ou None si introuvable.
    """
    try:
        tag = soup.find("span", itemprop="ratingCount")
        if tag and tag.has_attr("content"):
            return int(tag["content"])
    except Exception as e:
        print("Erreur dans get_nb_votes :", e)
    return None

def get_tenacite(soup):
    """
    Extrait les votes pour chaque modalité de ténacité (ex: médiocre, faible, etc.).

    Args:
        soup (BeautifulSoup): contenu HTML parsé de la page parfum.

    Returns:
        list of tuples: [(modalité, nombre de votes), ...]
    """
    try:
        tenacite = []
        sections = soup.find_all("div", class_="grid-x grid-margin-x")

        for section in sections:
            nom_tag = section.find("span", class_="vote-button-name")
            vote_tag = section.find("span", class_="vote-button-legend")

            if nom_tag and vote_tag:
                nom = nom_tag.text.strip().lower()
                votes = int(vote_tag.text.strip())
                tenacite.append((nom, votes))

        return tenacite

    except Exception as e:
        print("Erreur dans get_tenacite :", e)
        return []


## TEST ##

url = "https://www.fragrantica.fr/parfum/Tom-Ford/Soleil-Blanc-34893.html"
soup = get_soup(url)

id = get_id_parfum(url)
nom = get_nom_parfum(soup)
maison = get_maison(soup)
parfumeurs = get_parfumeurs(soup)
image_url = get_image_url(soup)
description = get_description(soup)
date = get_date(soup)


famille = get_famille(soup)
accords = get_accords(soup)
notes = get_notes_from_description(soup)

moyenne = get_note_moyenne(soup)
votes = get_nb_votes(soup)

print("ID:", id)
print("Parfum:", nom)
print("Maison :", maison)
print("Date :", date)
print("Parfumeurs :", parfumeurs)
print("Image URL :", image_url)
print("Description :", description)

print("Famille olfactive :", famille)
print("Accords principaux :", accords)

print("Tête :", notes["notes_tete"])
print("Cœur :", notes["notes_coeur"])
print("Fond :", notes["notes_fond"])

print(f"Note moyenne : {moyenne} / 5")
print(f"Nombre de votes : {votes}")
print(get_tenacite(soup))