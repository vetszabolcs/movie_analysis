from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
from constants import SQL_CON


# Setting up SQL connection
engine = create_engine(SQL_CON)

def slice_sql(year):
    """Getting titles to be searched"""
    query = text(f'select original_title_year, primary_title_year, "startYear"\
                     from movies.search\
                     where searched = 0 and "startYear" = {year}\
                     order by "startYear" desc')
    return pd.read_sql(query, SQL_CON)


def check_download_count(year):
    query = text(f'select count(*)\
                     from movies.search\
                     where downloaded = 1\
                     and "startYear" = {year}')
    res = engine.execute(query)
    count = [x[0] for x in res][0]
    return count


def update_searched(cond_val):
    query = f'update movies.search\
                set searched = 1\
                where original_title_year = \'{cond_val}\''
    engine.execute(text(query))


def update_downloaded(cond_val):
    query = f'update movies.search\
                set downloaded = 1\
                 where original_title_year = \'{cond_val}\''
    engine.execute(text(query))