from pymongo import MongoClient
import time
import random

#Import beautiful soup
import requests
import re
from bs4 import BeautifulSoup

# Connect to client as a global to save passing it
client = MongoClient()
database = client['Films']   # Database name
mongo_connect = database['Imdb 2018 films'] # Collection name

def scrape(item_number):
    
    while item_number < 11800:
    
        response = requests.get('https://www.imdb.com/search/title/?title_type=feature&release_date=2018-01-01,2018-12-31&start={}&ref_=adv_nxt'.format(item_number))

        soup = BeautifulSoup(response.text, 'html.parser')
        movie_containers = soup.find_all('div', class_ = 'lister-item mode-advanced')






        for container in movie_containers:
            fields = {}
            title = container.h3.a
            if title:
                fields['Film title'] = title.text


            list_number = container.find('span', class_ = 'lister-item-index unbold text-primary')
            if list_number:
                fields['Imdb 2018 list number'] = (int(list_number.text.strip(".")))   


            year = container.h3.find('span', class_ = 'lister-item-year text-muted unbold')
            if year:
                fields['Year released'] = year.text.strip("()")





            runtime = container.find('span', class_ = 'runtime')
            if runtime:
                fields['Runtime'] = runtime.text.strip("()")


            imdb_sc = container.strong
            if imdb_sc:
                fields['Imdb Score'] = float(imdb_sc.text.strip("()"))


            mscore = container.find('span', class_ = 'metascore favorable')
            if mscore:
                fields['Metascore'] = (int(mscore.text))

            genres = container.find('span', class_ = 'genre')
            if genres:
                fields['Genres'] = genres.text.strip("\n")


            MPAA_rating = container.find('span', class_ = 'certificate')
            if MPAA_rating:
                fields['MPAA rating'] = MPAA_rating.text



            directors, stars = names(container)
            if directors:
                fields['Director(s)'] = directors


            if stars:
                fields['Actor(s)'] = stars



            votes, gross = vote_gross(container)

            if votes:
                fields['Votes'] = int(votes.strip(","))           


            if gross:
                fields['Gross'] = gross                

            mongo_connect.insert_one(fields)

            item_number += 50

        time.sleep(random.randint(5,30))    

    pass 
        
        
        
def names(container):
    name_list = []
    for elem in container(text=re.compile(r'Director')):
        if elem:
            name_list = elem.parent.text

            names = name_list.split('\n')
            names = [i for i in names if i] 
        
        
            names_s = []
            for name in names: 
                name_s = name.strip()
                name_s = name_s.strip(",")
                names_s.append(name_s)  
                names_s = [i for i in names_s if "|" not in i] 

            star_ind = names_s.index('Stars:')
            if star_ind:
                stars = names_s[star_ind + 1:len(names_s)]
            
                if names_s[0][0:8] == 'Director':
                    director_s = names_s[1:star_ind ]

    
        
    return director_s, stars  


def vote_gross(container):
    gross_tot = None
    votes = container.find('p', class_ = 'sort-num_votes-visible')
    if votes:
        votes = votes.text
        votes = votes.replace('\n', ' ')
        votes = votes.replace('|', '')
        votes = votes.strip(" ")
        votes = votes.split(" ")
        votes = [i for i in votes if i]
        if votes[0] == 'Votes:':
                vote_s = votes[1]
        if len(votes) > 2:
            if votes[2] == 'Gross:':
                gross_tot = votes[3]
         
    return  vote_s, gross_tot  

    
        
        
        

        


