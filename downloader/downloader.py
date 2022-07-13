import os
import re
import sys
import logging
import pandas as pd
import donwloader_functions as funs
import constants as c
import unzipper as z
from sqlalchemy import create_engine
from sqlalchemy import text
from send_email import send_email
from time import sleep
from random import randint

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
                         where searched = 0 and "startYear" <= 2020\
                         order by "startYear" desc'),
                    con)


# The searcher algorythm of opensubtitles is clever enough to redirect to a grammatically - or
# meaning-similiar title's website if the given title was not found.
# For eg.: The Gifted (1999) redirects to The Talented Mr. Ripley (1999)
# This could be checked before download although I download the found subtitle anyway
# and gonna get it's details later from IMDb.

def update_searched(cond_val):
    query = f"update movies.search set searched = 1 where original_title_year = '{cond_val}'"
    engine.execute(text(query))


def update_downloaded(cond_val):
    query = f"update movies.search set downloaded = 1 where original_title_year = '{cond_val}'"
    engine.execute(text(query))


def downloader(dest, temp):
    logging.info("Started downloader")
    send_email("Started downloader")
    for o, p in to_search.loc[:, ["original_title_year", "primary_title_year"]].values:
        sleep(randint(1, 4))
        logging.info(f"Searching subtitle - original title: {o} - primary title: {p}")
        cond_val = o.replace("\'", "\'\'")  # reformat to sql readable
        update_searched(cond_val)
        logging.info("Updated search column")
        try:
            movie_site = funs.get_movie_site(o)
        except TypeError:
            try:
                movie_site = funs.get_movie_site(p)
            except TypeError:
                continue

        title, download_site = funs.get_title_and_download_site(movie_site)
        if download_site is None:
            continue
        title = re.sub(c.forbidden_chars, " ", title).strip()
        download_link = funs.get_download_link(download_site)

        if download_link:
            download_path = os.path.join(temp, title + ".zip")
            try:
                funs.donwload_file(download_link, download_path)
                z.extractor(download_path, temp)
                z.renamer(download_path, dest, temp)
                update_downloaded(cond_val)
                logging.info("Updated download column")
                logging.info(f"Downloaded - {title}")
            except (TypeError, IndexError):
                continue


if __name__ == "__main__":
    try:
        downloader(c.SUBTITLES_DIR, c.TEMP_DIR)
    except Exception as e:
        logging.error(e)
        send_email(f"Something went wrong with the downloader... {e}")

