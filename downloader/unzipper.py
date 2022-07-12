import os
import shutil
import time
import re
from zipfile import ZipFile
from constants import forbidden_chars


def extractor(zip_name, dest):
    re.sub(forbidden_chars, " ", zip_name).strip()
    extensions = ("ass", "mkv", "mmc", "mpl2", "sami", "sbv", "scc", "srt", "ssa", "stl", "sub", "txt", "xml")
    with ZipFile(zip_name, "r") as zipf:
        files = zipf.namelist()
        for f in files:
            if f.endswith(extensions):
                zipf.extract(f, dest)


def renamer(zip_name, dest, temp_dir):
    extracted = [f for f in os.listdir(temp_dir) if not f.endswith("zip")][0]  # glob does not recognize leading dot
    extension = "." + extracted.split(".")[-1]
    new_name = re.sub(".zip$", extension, zip_name.split("\\")[-1])
    new_name = re.sub(forbidden_chars, " ", new_name).strip()
    new_name = os.path.join(dest, new_name)
    if not os.path.exists(new_name):
        os.rename(os.path.join(temp_dir, extracted), new_name)
        time.sleep(1)
    shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
