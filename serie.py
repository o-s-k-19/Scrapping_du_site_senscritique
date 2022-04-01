import sys
import time
from urlextract import URLExtract
import requests
from bs4 import BeautifulSoup

print("**********************************************************************************************************************************\n")
print("                           SCRAPPING THE SENSCRITIQUE SERIES SECTIONS WEB SITE                                                \n")
print("NB : Ce script permet seulement de recuperer les donnees disponibles pour la section des series et seulement pour :"
      "\nauteur(s); titre; descriptions; acteur(s); categories; annee de sortie; image de couverture et video de la bande annonce")
print("Aussi le programme n'a pas ete optimise pour gerer toutes les erreurs qui peuvent subvenir \n")
print("**************************************************************************************************************************************")
while True:
    nb_input = input("Combien de series souhaitez vous extraire ? :)\n")
    try:
        nb_input = int(nb_input)
    except ValueError:
        print("Veuillez saisir un entier")
        continue
    except TypeError:
        print("Veuillez saisir un type entier")
        continue
    if nb_input > 46079:
        print("Nombre de series maximum depasses")
        continue
    elif nb_input <= 0:
        print("Le nombre saisie n'est pas valable")
        continue
    else:
        break

# -----------------------------------------------------------------------------------------------------------------------

# Definir les headers pour simuler le comportement d'un client web --> astuce pour eviter d'etre ban temporairement sur le site

headers = {
    "Referer": "https://www.senscritique.com/search?categories[0][0]=S%C3%A9ries",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    # "User-Agent": "custom",
    "X-Requested-With": "XMLHttpRequest",
}

# -----------------------------------------------------------------------------------------------------------------------
"""
response.ok --> renvoie vrai si la requete a ete bien traite
response.text --> pour afficher le contenu de la response de la requete
"""

# traitement pour la collecte des liens descriptifs de chaque serie

list_liens_page_serie = []
nb_liens = 0
nb_pages = int((nb_input / 16) + 1)

for i in range(0, nb_pages):
    url = 'https://www.senscritique.com/search?categories[0][0]=S%C3%A9ries&p=' + str(i+1)
    response = requests.get(url, headers=headers)  # headers)
    #print(response)
    if response.ok:

        # on va utiliser le module BeautifulSoup pour pouvoir selectionner les elements de la page à extraire
        soup = BeautifulSoup(response.text, 'html.parser')

        # dans un premier temps il faut extraire les liens des pages descriptifs des series
        div_liens = soup.find_all("div", {"class": "ProductListItem__TextContainer-sc-1ci68b-8 kKuZab"})
        for div_lien in div_liens:
            a = div_lien.find('a')
            lien = a['href']
            list_liens_page_serie.append(lien)
            nb_liens += 1
    else:
        print("Ooops :\n-Soit le serveur est trop surcharge\n-Soit l'acces au serveur vous a ete refuse temporairement "
              "\nVerifier sur votre navigateur si l'accés a : " + str(
            url) + " est autorise\nVeuillez réessayer plus tard :)")
        sys.exit(1)

# fin traitement
# ------------------------------------------------------------------------------------------------------------------------------------
"""
Maintenant pour chaque serie on va recuperer les informations concernant : authors; title; content; actors; category; year; image_url; video_url
et les exporter au format csv :
"""
print("*********************** Exportation en cours ... ***************************************************")
print("Un ficher series_data.csv sera creer et visible dans le repertoire courant :)")

# un break de 5 seconde
time.sleep(5)

#Pour exporter les données dans un format csv :
with open('series_data.csv', 'w', encoding="utf-8") as outstream:
    outstream.write('auteur(s);titre;descriptions;acteur(s);categories;annee de sortie;image de couverture;video de la bande annonce\n')
    headers_serie = {'User-Agent': 'custom'}
    n = 0
    for serie in list_liens_page_serie:
        url = serie
        response = requests.get(url, headers=headers_serie)
        print("\n************************************ traitement de " + serie)
        print(response)
        response = requests.get(url, headers=headers_serie)

        if response.ok:
            # on va utiliser BeautifulSoup pour pouvoir selectionner les elements de la page à extraire
            soup_serie = BeautifulSoup(response.text, 'html.parser')

            # les elements à extraire
            # Logique de l'Algoritme : on va indiquer les selecteurs css qui permettent d'identifier l'element

            # auteur :
            auteurs = []
            creators = soup_serie.find_all("span", {"itemprop": "creator"})
            if creators == None:
                acteurs = ""
            else:
                for creator in creators:
                    span = creator.find('span')
                    auteur = span.text
                    auteurs.append(auteur)
                auteurs = " ".join(auteurs)
                auteurs = auteurs.replace(" ", ",")
            print(auteurs)

            # acteurs
            acteurs = []
            actors = soup_serie.find_all("span", {"class": "d-offset ecot-contact-label"})
            if actors == None:
                acteurs = ""
            else:
                for actor in actors:
                    acteur = actor.text
                    acteurs.append(acteur)
                acteurs = " ".join(acteurs)
                acteurs = acteurs.replace(" ", ",")
            print(acteurs)

            # titre
            title = soup_serie.find("h1", {"class": "pvi-product-title"})
            if title == None:
                titre = ""
            else:
                titre = str(title.text).replace("\t", "")
                titre = titre.replace("\n", "")
            print(titre)

            # description
            small = soup_serie.find("p", {"data-rel": "small-resume"})
            # full = soup_serie.find("p", {"class": "pvi-productDetails-resume d-hidden"})
            if small == None:
                description = ""
            else:
                description = small.text
                description = str(description).replace("\t", "")
                description = description.replace("\n", "")
            print(description)

            # annee de sortie
            date = soup_serie.find("li", {"class": "pvi-productDetails-item nowrap"})
            annee = date.find('time').string
            print(annee)

            # categorie : ensemble de genre
            categorie = []
            genres = soup_serie.find_all("span", {"itemprop": "genre"})
            if genres == None:
                categorie = ""
            else:
                for genre in genres:
                    categorie.append(genre.text)
                categorie = " ".join(categorie)
                categorie = categorie.replace(" ", ",")
            print(categorie)

            # image de couverture
            img = soup_serie.find("img", {"class": "pvi-hero-poster"})
            s = URLExtract().find_urls(str(img))

            if s == None:
                img_src = ""
            else:
                img_src = s[0]
                img_src = str(img_src)
            print(img_src)

            # video de bande d'annonce
            vid = soup_serie.find("iframe", {"style": "border: none;"})
            if vid == None:
                video = ""
            else:
                video = vid['src']
                video = str(video)
            print(video)

            # outstream.write('authors;title;content;actors;category;year;image;movie\n')

            outstream.write(auteurs + ";" + titre + ";" + description +
                            ";" + acteurs + ";" + categorie + ";" +
                            annee + ";" + img_src + ";" + video + "\n")

            print("\nSUCCES !!!")
            n = n + 1
            print("\nseries recuperées : " + str(n))
            if n == nb_input:
                break
        time.sleep(3)

print("\nSeries recuperées au total : " + str(n))
print("\n-A present toutes vos series ont ete collecte suivant cet ordre pour les colonnes :\nauteur(s); titre; descriptions; acteur(s); "
      "categories; annee de sortie; image de couverture et video de la bande annonce")
print("\n-Si vous souhaitez modifier l'ordre des colonnes vous pouvez le faire via un logiciel de traitement de texte comme excel")
print("\n-Noubliez pas que la premiere ligne du fichier csv correspond a l'entete de vos donnes :)")
print("\n                                       BYE                                         ")
print("*********************** Fin  ***************************************************")

# ------------------------------------------------------------------------------------------------------------------------------------