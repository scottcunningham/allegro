import urllib
import json
import requests
from bs4 import BeautifulSoup

LISTING_BASE_URL = 'http://allegro.pl/listing'
SEARCH_BASE_URL = 'http://allegro.pl/listing/listing.php'
DEFAULT_ARGS = {
    'order': 'm',
    'match': 's0-e-0113'
}


def _format_search_url(search_term):
    args = dict(DEFAULT_ARGS)
    args['string'] = search_term
    encoded_args = urllib.urlencode(args)
    return "{}?{}".format(SEARCH_BASE_URL, encoded_args)


def _get_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('HTTP %s when accessing %s:' %
                        (response.status_code, url, response.content))
    return response.content


def _parse_html(html):
    soup = BeautifulSoup(html)
    parsed_sales = []
    for item in soup.find_all('article'):
        excerpt = item.find(attrs={'class': 'excerpt'})
        img_urls_raw = excerpt.find(attrs={'class': 'photo'})['data-img']
        img_urls = json.loads(img_urls_raw)
        img_url = img_urls[0][-1:]

        details = item.find(attrs={'class': 'details'})
        var = {
            'title': details.h2.text,
            'url': LISTING_BASE_URL + details.a.attrs['href'],
            'img_url': img_url,
            'price': excerpt.find(attrs={'class': 'purchase'})
                            .find(attrs={'class': 'price'})
                            .text
                            .replace('\n', '')
                            .encode('utf-8')
        }
        parsed_sales.append(var)
    return parsed_sales


def search(search_term):
    url = _format_search_url(search_term)
    html = _get_url(url)
    parsed = _parse_html(html)
    return parsed
