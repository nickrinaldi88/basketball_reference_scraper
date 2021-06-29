# libraries

from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata, unidecode


# get game suffix 
def get_game_suffix(date, team1, team2):
    '''
    Function taking in 3 parameters, date, team1, team 2
    '''
    # get request f string
    r = get(f'https://www.basketball-reference.com/boxscores/index.fcgi?year={date.year}&month={date.month}&day={date.day}')
    # suffix variable equalt to none
    suffix = None
    # Check for successful request
    if r.status_code==200:
        # if so, make Soup object
        soup = BeautifulSoup(r.content, 'html.parser')
        # iterate through all table elements in soup with the class teams
        for table in soup.find_all('table', attrs={'class': 'teams'}):
            # loop through all anchor or link tags; for all anchor tags in every anchor tag located in the table
            for anchor in table.find_all('a'):
                # if boxscores exist in the link for that team
                if 'boxscores' in anchor.attrs['href']:
                    # if team 1 or team 2 is in that link
                    if team1 in anchor.attrs['href'] or team2 in anchor.attrs['href']:
                        # the suffix is that link
                        suffix = anchor.attrs['href']
    # return it
    return suffix

"""
    Helper function for inplace creation of suffixes--necessary in order
    to fetch rookies and other players who aren't in the /players
    catalogue. Added functionality so that players with abbreviated names
    can still have a suffix created.
"""
def create_suffix(name):
    # normalize the name
    normalized_name = unicodedata.normalize('NFD', name.replace(".","")).encode('ascii', 'ignore').decode("utf-8")
    # the first name suffix will be decoded normalize_name string first two chars lowercase
    first = unidecode.unidecode(normalized_name[:2].lower())
    # the last name suffix will be the normalized variable split, first index on 
    lasts = normalized_name.split(' ')[1:]
    names = ''.join(lasts)
    second = ""
    if len(names) <= 5:
        second += names[:].lower()

    else:
        second += names[:5].lower()

    return second+first

"""
    Amended version of the original suffix function--it now creates all
    suffixes in place.

    Since basketball reference standardizes URL codes, it is much more efficient
    to create them locally and compare names to the page results. The maximum
    amount of times a player code repeats is 5, but only 2 players have this
    problem--meaning most player URLs are correctly accessed within 1 to 2
    iterations of the while loop below.

    Added unidecode to make normalizing incoming string characters more
    consistent.

    This implementation dropped player lookup fail count from 306 to 35 to 0.
"""
def get_player_suffix(name):
    # normalize name
    normalized_name = unidecode.unidecode(unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode("utf-8"))
    # last initial 
    initial = normalized_name.split(' ')[1][0].lower()
    # suffix link; the initial of last name, plus the result of the player suffix function 
    suffix = '/players/'+initial+'/'+create_suffix(name)+'01.html'
    # get player request 
    player_r = get(f'https://www.basketball-reference.com{suffix}')
    # while the player status_code is successful 
    while player_r.status_code==200:
        # Player_sup
        player_soup = BeautifulSoup(player_r.content, 'html.parser')
        # find h1 tag with name itemprop
        h1 = player_soup.find('h1', attrs={'itemprop': 'name'})
        # if that h1 tag exists, 
        if h1:
            # grab their page_name 
            page_name = h1.find('span').text
            """
                Test if the URL we constructed matches the 
                name of the player on that page; if it does,
                return suffix, if not add 1 to the numbering
                and recheck.
            """
            if ((unidecode.unidecode(page_name)).lower() == normalized_name.lower()):
                return suffix
            else:
                suffix = suffix[:-6] + str(int(suffix[-6])+1) + suffix[-5:]
                player_r = get(f'https://www.basketball-reference.com{suffix}')

    return None


def remove_accents(name, team, season_end_year):
    '''
    Remove accents from strings. Take in name, team, and season end year
    '''
    # alphabet set
    alphabet = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXZY ')
    # if len of the set of characters between the name and the alphabet are 0, meaning there aren't any accents, return the name
    if len(set(name).difference(alphabet))==0:
        return name
    # request to get the teams seasons_end year
    r = get(f'https://www.basketball-reference.com/teams/{team}/{season_end_year}.html')
    # team data frame and best match variables set 
    team_df = None
    best_match = name
    # if request works
    if r.status_code==200:
        # create soup object
        soup = BeautifulSoup(r.content, 'html.parser')
        # find table element
        table = soup.find('table')
        # team's dataframe is the read_html function, on the first index of the table element, 
        team_df = pd.read_html(str(table))[0]
        max_matches = 0
        # for p in the player column of that data frame 
        for p in team_df['Player']:
             # matches for an accent is 
            matches = sum(l1 == l2 for l1, l2 in zip(p, name))
            if matches>max_matches:
                max_matches = matches
                # best_match becomes that player
                best_match = p
     # return the best match if there's an accent 
    return best_match
