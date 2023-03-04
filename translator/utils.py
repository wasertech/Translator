import time

from pathlib import Path
from glob import glob

def save_txt(translations, file_path, append=False):
    with open(file_path, 'w' if not append else 'a') as f:
        f.write("\n".join(translations))

def read_txt(filepath):
    p = Path(filepath)
    if p.exists() and p.is_file():
        with open(p, 'r') as f:
            return f.read().split("\n")
    else:
        return []

def glob_files_from_dir(directory, suffix=".txt"):
    return list(set(glob(f"{directory}/*{suffix}")) - set(glob(f"{directory}/*.tmp{suffix}")))

def read_txt_files(directory):
    r = []
    for f in glob_files_from_dir(directory, suffix=".txt"):
        for l in read_txt(f):
            r.append(l)
    return r
