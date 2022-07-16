from os.path import join
import os

# Connections
URL = "https://yifysubtitles.org"
SQL_CON = f"postgresql://postgres:{os.environ.get('PASS')}@localhost:5432/postgres"

# Locations
DATA_DIR = "./../../data"
SUBTITLES_DIR = join(DATA_DIR, "subtitles")
TEMP_DIR = join(SUBTITLES_DIR, "temp")
SUBTITLES_TEST_DIR = join(DATA_DIR, "subtitles_test")
TEMP_TEST_DIR = join(SUBTITLES_TEST_DIR, "temp")

# Downloader
forbidden_chars = "[\\\\/:\\*\\?\"<>\\|]"
MIN_YEAR = 1918
MOVIES_PER_YEAR = 100
