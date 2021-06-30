import unidecode, os, sys, unicodedata

"""
    Bounded levenshtein algorithm credited to user amirouche on stackoverflow.
    Implementation borrowed from https://stackoverflow.com/questions/59686989/levenshtein-distance-with-bound-limit
"""

# levenshetin algo to determine string matches
def levenshtein(s1, s2, maximum):  
    # length of string1 is greater than length of string 2
    if len(s1) > len(s2):
        # essentially swap the variables
        s1, s2 = s2, s1
    # distances between words is the range of length of s1 which WAS string 2, + 1)
    distances = range(len(s1) + 1)
    # for i2, c2 in enumerate(s2), where i2 will be index, and c2 will be character
    for i2, c2 in enumerate(s2):
        # distances_ is index plus one so it doesn't start at 0
        distances_ = [i2+1]
        # for index, character in s1, 
        for i1, c1 in enumerate(s1):
            # if character one is equal to character two
            if c1 == c2:
                # append distances_ list with the character of distances at index 1
                distances_.append(distances[i1])
            else:
                # otherwise, append to distance 1, plus the minimum of distances at index i1, distances i1 + 1, and the last char in distances.
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        # if x is greater than or equal to the maximum for all items in distances; IF thats true, return -1
        if all((x >= maximum for x in distances_)):
            return -1
        # old distances = new_distances
        distances = distances_
    # return the last character of distances
    return distances[-1]

"""
    User input is normalized/anglicized, then assigned a levenshtein score to 
    find the closest matches. If an identical and unique match is found, it is 
    returned. If many matches are found, either identical or distanced, all
    are returned for final user approval.
"""
def lookup(player, ask_matches = True):
    '''
    Function to lookup a player
    '''
    # open up path of player names text doc
    path = os.path.join(os.path.dirname(__file__), 'br_names.txt')
    # normalize the string of the player name passed in 
    normalized = unidecode.unidecode(player)
    # create empty matches set
    matches = []
    # open the file
    with open(path) as file:
        # create lines variable
        Lines = file.readlines()
        # loop through lines
        for line in Lines:
            """
                A bound of 5 units of levenshtein distance is selected to   
                account for possible misspellings or lingering non-unidecoded 
                characters.
            """
            # distance is the lowercase playername through the levenstein algo, between each line, with a score of 5
            dist = levenshtein(normalized.lower(), line[:-1].lower(), 5)
            # if the dist between our levenshtein string and the player name is 0, or greater
            if dist >= 0: 
                # add that line to matches, plus the distance to see how close it is. 
                matches += [(line[:-1], dist)]

    """
        If one match is found, return that one;
        otherwise, return list of likely candidates and allow
        the user to confirm specifiy their selection.
    """
    # if there's one match, or ask_matches is False
    if len(matches) == 1 or ask_matches == False:
        # sort the matches list by first tuple index result, 
        matches.sort(key=lambda tup: tup[1])
        # you searched for player, # of matches results found, result is matches[0][0]
        print("You searched for \"{}\"\n{} result found.\n{}".format(player, len(matches), matches[0][0]))
        # results for matches[0][0]
        print("Results for {}:\n".format(matches[0][0]))
        # return that match
        return matches[0][0]
    
    
    # if there's more than one match
    elif len(matches) > 1:
        print("You searched for \"{}\"\n{} results found.".format(player, len(matches)))
        # sort by first  index of tuple again
        matches.sort(key=lambda tup: tup[1])
        # set i pointer
        i = 0
        # for match in matches
        for match in matches:
            # print number of matches
            print("{}: {}".format(i, match[0])) 
            i += 1           
        
        # select a match
        selection = int(input("Pick one: "))
        # print the result
        print("Results for {}:\n".format(matches[selection][0]))
        # return match
        return matches[selection][0]
    
    # elif if there's 0 matches
    elif len(matches) < 1:
        print("You searched for \"{}\"\n{} results found.".format(player, len(matches)))
        return ""
       
    # return the player name
    else:
        print("You searched for \"{}\"\n{} result found.\n{}".format(player, len(matches), matches[0][0]))
        print("Results for {}:\n".format(matches[0][0]))
        return matches[0][0]

    return ""
