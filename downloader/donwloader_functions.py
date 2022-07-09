from bs4 import BeautifulSoup
from requests import get
import re
from constants import *


def get_subt_link(url):
    soup = BeautifulSoup(get(url).text, features="lxml")
    anchort = soup.find("a", class_="bnone")
    href = re.search("(href=\")(.*?)( )", str(anchort))[2].replace("\"", "")
    return URL + href


def get_title_and_download_link(url):
    soup = BeautifulSoup(get(url).text, features="lxml")
    download_button = soup.find(id="bt-dwl-bt")
    title, download_link = None, None
    if download_button:
        download_button = str(download_button)
        download_endp = re.search("(href=)(.*?\"+)( )", download_button)[2].replace("\"", "")
        download_link = URL + download_endp
        title = re.search("data-product-title=\"(.*?)(\" )", download_button)[1].strip()
    return title, download_link
