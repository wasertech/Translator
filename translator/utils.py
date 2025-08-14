import time

from pathlib import Path
from glob import glob
import polib

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

def glob_po_files_from_dir(directory, suffix=".po"):
    """Get all PO files from directory, excluding temporary files"""
    return list(set(glob(f"{directory}/*{suffix}")) - set(glob(f"{directory}/*.tmp{suffix}")))

def read_po_file(filepath):
    """Read a PO file and return polib POFile object"""
    return polib.pofile(filepath)

def extract_untranslated_from_po(po_file):
    """Extract untranslated entries (msgid) from a PO file"""
    untranslated = []
    for entry in po_file.untranslated_entries():
        if entry.msgid.strip():  # Skip empty strings
            untranslated.append(entry.msgid)
    return untranslated

def update_po_with_translations(po_file, translations_dict):
    """Update PO file entries with translations"""
    for entry in po_file.untranslated_entries():
        if entry.msgid in translations_dict:
            entry.msgstr = translations_dict[entry.msgid]
    
def save_po_file(po_file, filepath):
    """Save PO file to specified path"""
    po_file.save(filepath)
