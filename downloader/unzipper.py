import os
from glob import glob
import shutil
import time
import re
from zipfile import ZipFile


def extractor(zip_name, dest):
    extensions = ("ass", "mkv", "mmc", "mpl2", "sami", "sbv", "scc", "srt", "ssa", "stl", "sub", "txt", "xml")
    with ZipFile(zip_name, "r") as zipf:
        files = zipf.namelist()
        for f in files:
            if f.endswith(extensions):
                zipf.extract(f, dest)


def renamer(zip_name, dest, temp_dir):
    forbidden_chars = "[\\\/:\*\?\"<>\|]"
    extracted = glob(temp_dir + "/*[!.zip]")[0]
    extension = "." + extracted.split(".")[-1]
    new_name = re.sub(".zip$", extension, zip_name.split("\\")[-1])
    new_name = re.sub(forbidden_chars, " ", new_name).strip()
    new_name = os.path.join(dest, new_name)
    if not os.path.exists(new_name):
        os.rename(extracted, new_name)
        time.sleep(1)
    shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
