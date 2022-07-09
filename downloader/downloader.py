import os
import sys
import logging
import pandas as pd
import donwloader_functions as funs
import constants as c
import unzipper as z
from urllib.request import urlretrieve
from sqlalchemy import create_engine
from sqlalchemy import text
from send_email import send_email

# Setting up SQL connection
con = f"postgresql://postgres:{os.environ.get('PASS')}@localhost:5432/postgres"
engine = create_engine(con)

# Creating directories
dirs = [c.DATA_DIR, c.SUBTITLES_DIR, c.TEMP_DIR, c.SUBTITLES_TEST_DIR, c.TEMP_TEST_DIR]
for d in dirs:
    if not os.path.exists(d):
        os.mkdir(d)

# Setting up logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s —  %(message)s",
                    handlers=[logging.FileHandler("log.log", encoding='UTF-8'),
                              logging.StreamHandler(sys.stdout)
                              ])

# Getting titles to be searched
to_search = pd.read_sql(
                    text('select original_title_year, primary_title_year\
                         from movies.search\
                         where searched = 0'),
                    con)

# The searcher algorythm of opensubtitles is clever enough to redirect to a grammatically - or
# meaning-similiar title's website if the given title was not found.
# For eg.: The Gifted (1999) redirects to The Talented Mr. Ripley (1999)
# This could be checked before download although I download the found subtitle anyway
# and gonna get it's details later from IMDb.

def update_sql(cond_val):
    query = f"update movies.search set searched = 1 where original_title_year = '{cond_val}'"
    engine.execute(text(query))

def downloader(dest, temp):
    logging.info("Started downloading")
    send_email("Started downloading")
    for i, v in enumerate(to_search.values):
        o, p = v[0], v[1]
        logging.info(f"Searching {o}")
        cond_val = o.replace("\'", "\'\'")
        url = c.URL + c.MOVIE_END + o.replace(" ", "+")
        title, download_link = funs.get_title_and_download_link(url)
        if download_link is None:
            try:
                subt_link = funs.get_subt_link(url)
                title, download_link = funs.get_title_and_download_link(subt_link)
            except TypeError:
                update_sql(cond_val)
                continue
        if download_link and title:
            download_path = os.path.join(c.TEMP_TEST_DIR, title + ".zip")
            urlretrieve(download_link, download_path)
            z.extractor(download_path, temp)
            z.renamer(download_path, dest, temp)
            update_sql(cond_val)
            logging.info(f"Downloaded {title}")


if __name__ == "__main__":
    try:
        downloader(c.SUBTITLES_DIR, c.TEMP_DIR)
    except:
        send_email("Something went wrong with the downloader... Check the logs.")
