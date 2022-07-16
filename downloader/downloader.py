import os
import re
import sys
import logging
import downloader_functions as funs
import sql_functions as sql
import constants as c
import unzipper as z
from send_email import send_email
from time import sleep
from random import randint
from zipfile import BadZipfile


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


# The searcher algorythm of opensubtitles is clever enough to redirect to a grammatically - or
# meaning-similiar title's website if the given title was not found.
# For eg.: The Gifted (1999) redirects to The Talented Mr. Ripley (1999)
# This could be checked before download although I download the found subtitle anyway
# and gonna get it's details later from IMDb.

def downloader(dest, temp):
    logging.info("Started downloader")
    send_email("Started downloader")
    for year in range(2020, c.MIN_YEAR-1, -1):
        to_search = sql.slice_sql(year).sample(frac=1)[["original_title_year", "primary_title_year"]]
        for o, p in to_search.values:

            if sql.check_download_count(year) >= c.MOVIES_PER_YEAR:
                logging.info(f"Downloading 100 movies from {year} completed")
                send_email(f"Downloading 100 movies from {year} completed")
                break

            sleep(randint(1, 4))
            logging.info(f"Searching subtitle - original title: {o} - primary title: {p}")
            cond_val = o.replace("\'", "\'\'")  # reformat to sql readable
            sql.update_searched(cond_val)
            logging.info("Updated search column")

            try:
                logging.info("Getting movie site...")
                movie_site = funs.get_movie_site(o)
            except TypeError:
                try:
                    movie_site = funs.get_movie_site(p)
                except TypeError:
                    continue
            logging.info("Getting title and download site...")
            title, download_site = funs.get_title_and_download_site(movie_site)

            if download_site:
                title = re.sub(c.forbidden_chars, " ", title).strip()
                logging.info("Getting download link...")
                download_link = funs.get_download_link(download_site)
            else:
                continue

            if download_link:
                download_path = os.path.join(temp, title + ".zip")
                try:
                    logging.info("Downloading subtitle...")
                    funs.donwload_file(download_link, download_path)
                    z.extractor(download_path, temp)
                    z.renamer(download_path, dest, temp)
                    sql.update_downloaded(cond_val)
                    logging.info("Updated download column")
                    logging.info(f"Downloaded - {title}")
                except (TypeError, IndexError, BadZipfile):
                    continue


if __name__ == "__main__":
    try:
        downloader(c.SUBTITLES_DIR, c.TEMP_DIR)
    except Exception as e:
        logging.error(e)
        send_email(f"Something went wrong with the downloader... {e}")
