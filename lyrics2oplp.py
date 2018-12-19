import json
import re
from datetime import datetime
from urllib import request, parse
from bs4 import BeautifulSoup


def identify_url(url):
    """Identify from which site a url is.

    Return values:
    'letras'   for 'letras.mus.br'
    'vagalume' for 'vagalume.com.br'
    'unknown'  if not able to identify.
    """

    if not isinstance(url, str):
        raise ValueError('url is not a string')
    url = url.strip()
    pattern = re.compile(r'^https?://.+\..+$')
    if pattern.search(url) == None:
        raise ValueError('not a webpage')

    sources = {
        'letras': r'letras\.mus\.br',
        'vagalume': r'vagalume\.com\.br'
    }
    for key in sources:
        pattern = re.compile(sources[key])
        if pattern.search(url) != None:
            return key

    return 'unknown'

def html_from_url(url):
    """Extracts html from a webpage."""

    response = request.urlopen(url)
    html = response.read()
    return html

def info_from_html(html, name_selector, author_selector):
    """Return a tuple with song's name and author from a page.

    name_selector -> css selector for song's name
    author_selector -> css selector for author's name
    """

    soup = BeautifulSoup(html, 'html.parser')
    name = soup.select(name_selector)[0]
    author = soup.select(author_selector)[0]

    return (name.get_text().strip(), author.get_text().strip())

def info_from_letrasmus(html):
    """Return a tuple with song's name and author from a 'letras.mus.br' page."""

    return info_from_html(html, '.cnt-head_title h1', '.cnt-head_title h2 a')

def lyrics_from_letrasmus(html):
    """Extracts lyrics from the html of a webpage of 'letras.mus.br'."""

    lyrics = ''
    soup = BeautifulSoup(html, 'html.parser')
    verses = soup.select('.cnt-letra article p')

    for para in verses:
        lyrics += para.get_text('\n') + '\n\n'

    return lyrics

def info_from_vagalume(html):
    """Return a tuple with song's name and author from a 'vagalume.com.br' page."""

    soup = BeautifulSoup(html, 'html.parser')
    name = soup.select('#lyricContent h1')[0]
    author = soup.select('#lyricContent h2 a')[0]

    return info_from_html(html, '#lyricContent h1', '#lyricContent h2 a')
    return (name.get_text().strip(), author.get_text().strip())


def lyrics_from_vagalume(html):
    """Extracts lyrics from a webpage of 'vagalume.com.br'.  """

    lyrics = ''
    soup = BeautifulSoup(html, 'html.parser')
    verses = soup.select('#lyrics')[0].contents
    for verse in verses:
        if verse.name == 'br':
            lyrics += '\n'
        else:
            lyrics += verse
    return lyrics



def lyrics_from_url(url):
    """Return a tuple with song's name, author and lyrics."""

    source = identify_url(url)
    extractor = {
        'letras': (lyrics_from_letrasmus, info_from_letrasmus),
        'vagalume': (lyrics_from_vagalume, info_from_vagalume)
    }
    html = html_from_url(url)
    if source in extractor:
        info = extractor[source][1](html)
        return (info[0], info[1], extractor[source][0](html))
    raise Exception("Unknow url's source.")


def xml_from_lyrics(lyrics, name, author):
    """Return the lyrics formated as xml."""

    xml_soup = BeautifulSoup('','xml')

    # <song>
    attributes = {
        "xmlns": "http://openlyrics.info/namespace/2009/song",
        "version": "0.8",
        "createdIn": "lyrics2oplp",
        "modifiedIn": "",
        "modifiedDate": datetime.now().isoformat()
    }
    song = xml_soup.new_tag("song", attrs = attributes)
    xml_soup.append(song)

    # <properties>
    properties = xml_soup.new_tag("properties")

    ## titles
    titles = xml_soup.new_tag("titles")
    title = xml_soup.new_tag("title")

    title.append(name) # add song name
    titles.append(title)
    properties.append(titles)

    ## authors
    authors = xml_soup.new_tag("authors")
    auth = xml_soup.new_tag("author")

    auth.append(author)
    authors.append(auth)
    properties.append(authors)

    song.append(properties)

    # <lyrics>
    lyr = xml_soup.new_tag("lyrics")
    verse_number = 1
    verse = xml_soup.new_tag("verse",
                             attrs={"name": "v{}".format(verse_number)})
    lyr.append(verse)

    lin_list = lyrics.split('\n')
    while(lin_list[-1] == ''):
        lin_list.pop()

    lin = xml_soup.new_tag("lines")
    for line in lin_list:
        if line == '':
            verse.append(lin)
            verse_number += 1
            verse = xml_soup.new_tag("verse",
                                     attrs={"name": "v{}".format(verse_number)})
            lyr.append(verse)
            lin = xml_soup.new_tag("lines")
            continue
        lin.append(line)
        lin.append(xml_soup.new_tag("br"))

    verse.append(lin)
    song.append(lyr)

    return xml_soup

def xml_from_url(url):
    """Return a OpenLyrics' XML from a url."""

    data = lyrics_from_url(url)
    return xml_from_lyrics(data[2], data[0], data[1])

def save_to_file(filename, xml_data):
    """Write data to a file."""

    with open('{}.xml'.format(filename), 'w') as file:
        file.write(str(xml_data))


if __name__ == '__main__':
    xml = xml_from_url(input('url: '))
    arquivo = input('salvar como: ')
    save_to_file(arquivo, xml)
