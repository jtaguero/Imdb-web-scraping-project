import psycopg2 as pg2
from psycopg2 import extras
import time
import random

#Import beautiful soup
import requests
import re
from bs4 import BeautifulSoup


def scrape(item_number, end_number):
    global vote_s
    global director
    global star
    
    vote_s = None
    director = None
    star = None
    
    while item_number < end_number:
    
        response = requests.get('https://www.imdb.com/search/title/?title_type=feature&release_date=2018-01-01,2018-12-31&start={}&ref_=adv_nxt'.format(item_number))

        soup = BeautifulSoup(response.text, 'html.parser')
        movie_containers = soup.find_all('div', class_ = 'lister-item mode-advanced')

        

        dada = []
        for container in movie_containers:
            
            data = []
            title = container.h3.a
            if title:
                data.append(title.text)
            else:
                data.append(None)

            list_number = container.find('span', class_ = 'lister-item-index unbold text-primary')
            if list_number:
                list_number = list_number.text.replace(',', '')
                data.append(int(list_number.strip(".")))   
            else:
                data.append(None)

            year = container.h3.find('span', class_ = 'lister-item-year text-muted unbold')
            if year:

                data.append(year.text.strip("()"))
            else:
                data.append(None)

            runtime = container.find('span', class_ = 'runtime')
            if runtime:
                data.append(runtime.text.strip("()"))
            else:
                data.append(None)

            imdb_sc = container.strong
            if imdb_sc:
                data.append(float(imdb_sc.text.strip("()")))
            else:
                data.append(None)

            mscore = container.find('span', class_ = 'metascore favorable')
            if mscore:
                data.append(int(mscore.text))
            else:
                data.append(None)                

            genres = container.find('span', class_ = 'genre')
            if genres:
                data.append(genres.text.strip("\n"))
            else:
                data.append(None)                

            MPAA_rating = container.find('span', class_ = 'certificate')
            if MPAA_rating:
                data.append(MPAA_rating.text)
            else:
                data.append(None)    

            
            director, star = names(container)
            if director:
                data.append(director)
            else:
                data.append(None)

            if star:
                data.append(star)
            else:
                data.append(None)                
            votes = None
            vote_s = None
            votes, gross = vote_gross(container)

            if votes:
                data.append(votes)            
            else:
                data.append(None)

            if gross:
                data.append(gross)                
            else:
                data.append(None)
                
            data = tuple(data)    
            
            dada.append(data)
            
            
            
        item_number = item_number + 50
        
        print(dada)
        insert(dada)    

        time.sleep(random.randint(5,30))    

    pass 
        
        
def vote_gross(container):
    gross_tot = None
    vote_s = None
    votes = container.find('p', class_ = 'sort-num_votes-visible')
    if votes:
        votes = votes.text
        votes = votes.replace('\n', ' ')
        votes = votes.replace('|', '')
        votes = votes.strip(" ")
        votes = votes.split(" ")
        votes = [i for i in votes if i]
        vote_s = None
        gross_tot = None
        if 'Votes:' in votes:
            votes_ind = votes.index('Votes:')
            if len(votes) >= votes_ind + 1:
                vote_s = int(votes[1].replace(',', ''))
                
            
                
        if len(votes) > 2:
            if votes[2] == 'Gross:':
                gross_tot = votes[3]
         
    return  vote_s, gross_tot  

def names(container):
    
    global director
    global star
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
            director = None
            star = None
            if len(names_s) > 1:
                if names_s[0][0:8] == 'Director':
                        director = names_s[1]
                if 'Stars:' in names_s:
                    star_ind = names_s.index('Stars:')
                    if star_ind:
                        star = names_s[star_ind + 1]

    
        
    return director, star  

def insert(row):
#     """ insert a new row into the imdb2018 table """
    sql = """
        INSERT INTO imdb2018 (film_title, Imdb_num, Year, Runtime, Imdb_score, Metascore, Genres, MPAA_rating, Director, Actor, Votes, Gross) 
        VALUES %s
        """
    conn = None
    
    try:
        connection = pg2.connect(user = "johnaguero",
                                      password = "torTuosity2",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "films")
        c = connection.cursor()
        

        extras.execute_values(c, sql, row) 
        connection.commit()
        count = c.rowcount
        print (count)
    except (Exception, pg2.Error) as error :
        if(connection):
            print("Failed to insert record into mobile table", error)
    finally:
        #closing database connection.
        if(connection):
            c.close()
            connection.close()
                                

    
        
        
        

        
