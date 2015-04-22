''' CLI to get the top definition from Urban Dictionary for whatever
    the search term is
'''

from BeautifulSoup import BeautifulSoup as bs
import requests
from HTMLParser import HTMLParser
import html2text
import os, sys

term_url = "http://www.urbandictionary.com/define.php?term={term}"
rand_url = "http://www.urbandictionary.com/random.php"

html_parser = HTMLParser()

def handle_html(tag):
    #takes a BeautifulSoup tag, and spits out a formatted string
    h = html2text.HTML2Text()
    h.ignore_links = True

    return h.handle(str(tag))

def get_term(term):
    term_plus = '+'.join(term.split())

    page_url = term_url.format(term=term_plus)

    response = requests.get(page_url)

    if not response.ok:
        #something fucked up
        #NB: even if a term doesn't exist, the page will still
        #give a 200 response, so this really is a connection error
        raise LookupError("Cannot connect to Urban Dictionary") 

    soup = bs(response.text)

    return process_soup(soup)

def process_soup(soup):
    #turns soup into a word, meaning and example

    #this is where we can ascertain whether a term exists or not
    word = soup.find('a', attrs={"class": "word"})

    if not word:
        #this happens when the term doesn't exist yet
        raise ValueError("The requested term does not exist")

    meaning = soup.find('div', attrs={"class": "meaning"})

    #is this guaranteed? If it isn't there, I think this will
    #simply evaluate to None
    example = soup.find('div', attrs={"class": "example"})

    return map(handle_html,
            filter(None,
                (word.getText(), meaning, example)
            )
        )

if __name__=="__main__":
    n = len(sys.argv)

    if n == 1:
        #should we actually let it go? By default it gets the word of the day.
    
        #called with no arguments
        print "Usage:"
        print "\tpython [-rd] urban_dictionary.py [TERM]"
        print "\nTERM can be space-delimited or '+'-delimited."
        print "-r\tget a random word"
        print "-d\tget the word of the day"

        sys.exit(0)

    #this is where I'll handle options being passed properly (TODO)
    
    if sys.argv[1] == "-r":
        #get a random word using random.php
        response = requests.get(rand_url)
        if not response.ok:
            raise LookupError("Cannot connect to Urban Dictionary")

        word, meaning, example = process_soup(bs(response.text))
    elif sys.argv[1] == "-d":
        #word of the day
        term = ''

        #when ud's define.php is given an empty string, it gets the dailies
        #the first such result is the word of the day
        word, meaning, example = get_term(term)
    else:
        term = ' '.join(sys.argv[1:])
    
        try:
            word, meaning, example = get_term(term)
        except ValueError, msg:
            print msg
            sys,exit(1)
    
    print "---- {} ----\n".format(word.strip('\n')).encode("utf-8")
    if meaning: print meaning.encode("utf-8")
    if example: print "----\n" + example.encode("utf-8")
