"""
@author: e-Daho

A simple program to generate poetry from scraped Baudelaire poems with markov chains.
"""


from typing import Dict
import random

import requests
from bs4 import BeautifulSoup


POEMS_URL = 'http://www.poesie.webnet.fr/lesgrandsclassiques/poemes/charles_baudelaire/'


def retrieve_random_word(word_list: Dict) -> str:
    word_list_sum = sum(value for value in word_list.values())
    rand_index = random.randint(1, word_list_sum)
    for word, value in word_list.items():
        rand_index -= value
        if rand_index <= 0:
            return word


def build_word_dict(text: str) -> Dict[str, Dict]:
    # Cleans the text
    text = text.replace("\n", " ")
    text = text.replace("\"", "")
    # Make sure punctuation marks are treated as their own "words,"
    # so that they will be included in the Markov chain
    punctuation = [',', '.', ';', ':']
    for symbol in punctuation:
        text = text.replace(symbol, ' ' + symbol + ' ')
    words = text.split(' ')
    # Filter out empty words
    words = [word for word in words if word]

    word_dict = {}
    for i in range(1, len(words)):
        if words[i-1] not in word_dict:
            # Create a new dictionary for this word
            word_dict[words[i-1]] = {}
        if words[i] not in word_dict[words[i-1]]:
            word_dict[words[i-1]][words[i]] = 0
        word_dict[words[i-1]][words[i]] += 1

    return word_dict


def get_text() -> str:
    with open('baudelaire_poems.txt') as file:
        return file.read()


def scrap_baudelaire() -> None:
    text = ''
    r = requests.get(POEMS_URL + 'charles_baudelaire.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    poems_list = soup.find('ul', {'id': 'resultats_poeme'})
    poems = list(poems_list.find_all('li'))
    print('Found {} poems'.format(len(poems)))
    for poem in poems:
        link = poem.find('a', href=True)
        poem_url = POEMS_URL + link['href']
        poem_r = requests.get(poem_url)
        poem_soup = BeautifulSoup(poem_r.text, 'html.parser')
        poem_title = poem_soup.find('h1').getText()
        print('Crawling {}...'.format(poem_title))
        poem_content = poem_soup.find('p', {'class': 'last'})
        # print(text)
        text += ' '
        text += str(poem_content)

    with open('beaudelaire_poems.txt', 'w') as file:
        print(text, file=file)


def build_text(length: int=50, first_word: str='Je') -> str:
    text = get_text()
    word_dict = build_word_dict(text)

    # Generate a Markov chain of length :length:
    chain = first_word
    previous_word = first_word
    for i in range(0, length - 1):
        current_word = retrieve_random_word(word_dict[previous_word.lower()])
        if current_word in [',', '.']:
            chain += current_word
        else:
            if previous_word in ['?', '!', '.']:
                current_word = current_word.title()
            chain += " " + current_word
        previous_word = current_word

    return chain


def main() -> None:
    text = build_text()
    print(text)


if __name__ == '__main__':
    main()
