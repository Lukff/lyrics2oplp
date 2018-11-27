import urllib.request as request
from bs4 import BeautifulSoup
import re


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
    response = request.urlopen(url)
    html = response.read()
    return html

def lyrics_from_letrasmus(html):
    lyrics = ''
    soup = BeautifulSoup(html, 'html.parser')
    verses = soup.select('.cnt-letra article p')

    for para in verses:
        lyrics += para.get_text('\n') + '\n\n'

    return lyrics

def lyrics_from_url(url):
    """Return the lyrics extracted from a url."""

    source = identify_url(url)
    extractor = {
        'letras': lyrics_from_letrasmus
    }
    html = html_from_url(url)
    if source in extractor:
        return extractor[source](html)
