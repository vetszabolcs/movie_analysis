from os.path import join
from constants import *
from urllib.parse import urlencode
from requests import get
from bs4 import BeautifulSoup
import re


def get_movie_site(title):
    search = URL + "/search?" + urlencode({"q": title})
    soup = BeautifulSoup(get(search).text, features="lxml")
    body = str(soup.find("div", class_="media-body"))
    movie_endp = re.search("href=\"(.*)\"", body)[1]
    return URL + movie_endp


def get_title_and_download_site(movie_site) -> tuple:
    try:
        soup = BeautifulSoup(get(movie_site).text, features="lxml")
        title = soup.find(class_="movie-main-title").text
        table = soup.find(class_="table other-subs")
        sub_link = re.search("\"/subtitle.*-english-yify.*?\"", str(table))[0].replace("\"", "")
        download_site = URL + sub_link
        return title, download_site
    except TypeError:
        return None, None


def get_donwload_link(download_site):
    try:
        soup = BeautifulSoup(get(download_site).text, features="html.parser")
        download_endp = soup.find(class_="download-subtitle").get("href")
        download_link = URL + download_endp
        return download_link
    except TypeError:
        return None


def donwload_file(url, dest):
    r = get(url)
    with open(dest, 'wb') as out:
        out.write(r.content)

# Used for opensubtitles:
# def get_subt_link(url):
#     soup = BeautifulSoup(get(url).text, features="lxml")
#     anchort = soup.find("a", class_="bnone")
#     href = re.search("(href=\")(.*?)( )", str(anchort))[2].replace("\"", "")
#     return URL + href
# 
# 
# def get_title_and_download_link(url):
#     soup = BeautifulSoup(get(url).text, features="lxml")
#     download_button = soup.find(id="bt-dwl-bt")
#     title, download_link = None, None
#     if download_button:
#         download_button = str(download_button)
#         download_endp = re.search("(href=)(.*?\"+)( )", download_button)[2].replace("\"", "")
#         download_link = URL + download_endp
#         title = re.search("data-product-title=\"(.*?)(\" )", download_button)[1].strip()
#     return title, download_link
