import time

from glob import glob

def save_txt(translations, file_path):
    with open(file_path, 'w') as f:
        f.write("\n".join(translations))

def read_txt(filepath):
    with open(filepath, 'r') as f:
        return f.read().split("\n")

def glob_files_from_dir(directory, suffix=".txt"):
    return glob(f"{directory}/*{suffix}")

def read_txt_files(directory):
    r = []
    for f in glob_files_from_dir(directory, suffix=".txt"):
        for l in read_txt(f):
            r.append(l)
    return r
