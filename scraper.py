import re
import sys
import time
import random
import datetime
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import quote_plus
import subprocess
import requests
from bs4 import BeautifulSoup

def bing(stub: str) -> str:
    if not stub.startswith('http'):
        return f'https://www.bing.com{stub}'
    if stub.startswith('https://www.bing.com/ck/a?!&&p='):
        source = requests.get(url=stub, headers=header, timeout=30)
        if match := re.search(r'var u = "(.*?)";', source.text):
            return re.split(r'\?msclkid=|\&msclkid=', match[1])[0]
    return stub

def yahoo(stub: str) -> str:
    if stub.startswith('https://r.search.yahoo.com/_ylt='):
        source = requests.get(url=stub, headers=header, timeout=30)
        if match := re.search(r'window.location.replace\("(.*?)"\);', source.text):
            return match[1]
    return stub

def content_parser(
    choice: str, file_path: Path, soup: BeautifulSoup, base_url: str, query: str,
) -> str | None:
    parse_array_find = {
        '1': ('a', {'id': 'pnnext'}),
        '2': ('a', {'class': 'sb_pagN'}),
        '3': ('a', {'class': 'next'}),
        '4': ('div', {'class': 'nav-link'})
    }

    parse_array_find_all = {
        '1': ('div', {'class': 'yuRUbf'}),
        '2': ('h2', {}),
        '3': ('h3', {}),
        '4': ('h2', {}),
    }

    engine_specific = {
        '1': callable,
        '2': bing,
        '3': yahoo,
        '4': callable,
    }

    next_pg_elm = soup.find(*parse_array_find[choice])
    page_titles = soup.find_all(*parse_array_find_all[choice])

    for pg_t in page_titles:
        if not pg_t or not (anchor := pg_t.find('a', href=True)):
            continue
        if choice in '23':
            try:
                link = engine_specific[choice](anchor['href'])
            except requests.RequestException as exp:
                print(f'Warning: {exp}')
                continue
        else:
            link = anchor['href']

        link = link.replace("https://", "").replace("http://", "")

        print(link)
        with open(file=file_path, encoding='utf-8', mode='at') as out_f:
            out_f.write(f'{link}\n')

    if choice == '4':
        return f'{base_url}/search?q={query}&s=64&o=json'

    if not next_pg_elm or not (next_url := next_pg_elm.get('href')):
        print('END OF PAGE REACHED ')
        return None

    return f'{next_url}' if choice == '3' else f'{base_url}{next_url}'

def web_scraper(
    choice: str, file_path: Path, base_url: str, query: str, pg_count: int
) -> None:
    url, current_page = f'{base_url}/search?q={query}', 1

    while current_page <= pg_count:
        print(f'\nPAGE: {current_page}/{pg_count} [{url}]')

        try:
            response = requests.get(url=url, headers=header, timeout=30)
        except requests.RequestException as exp:
            print(f'Warning: {exp}')
            break

        if response.status_code != 200:
            print('Warning: Site Unreachable')
            print(response.text)
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        if not (url := content_parser(choice, file_path, soup, base_url, query)):
            break

        current_page += 1
        if current_page <= pg_count:
            print(f'MOVING TO PAGE {current_page}')
            time.sleep(random.randint(5, 15))
        else:
            print('PAGE COUNT REACHED')

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'
}

def main():
    engine_data = {
        '1': ('google.list', 'https://www.google.com'),
        '2': ('bing.list', 'https://www.bing.com'),
        '3': ('yahoo.list', 'https://search.yahoo.com'),
        '4': ('duckduckgo.list', 'https://duckduckgo.com/html'),
    }

    your_query = input('What search term would you like to scrape for emails?')
    pg_count = int(input('How many pages of search terms would you like to scrape?'))
    user_choice = input('Choose a search engine: 1 = Google, 2 = Bing, 3 = Yahoo, 4 = Duckduckgo')
    url_list_file, base_url = engine_data[user_choice]

    web_scraper(user_choice, "out.txt", base_url, your_query, pg_count)

if __name__ == '__main__':
    print("Lead Finder")
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped")
