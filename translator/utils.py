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
    """Get all PO files from directory recursively, excluding temporary files"""
    import os
    po_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(suffix) and not file.endswith(f".tmp{suffix}"):
                po_files.append(os.path.join(root, file))
    return po_files

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

def extract_all_from_po(po_file):
    """Extract all entries (msgid) from a PO file, including translated ones"""
    all_entries = []
    for entry in po_file:
        if entry.msgid.strip():  # Skip empty strings
            all_entries.append(entry.msgid)
    return all_entries

def get_po_language(po_file):
    """Extract language code from PO file metadata"""
    # Check the Language header in metadata
    language = po_file.metadata.get('Language', '').strip()
    if language:
        return language
    
    # If Language field is empty, try to extract from Language-Team
    language_team = po_file.metadata.get('Language-Team', '').strip()
    if language_team and '<' in language_team:
        # Extract language code from "LANGUAGE <LL@li.org>" format
        language = language_team.split('<')[0].strip()
        if language and language != 'LANGUAGE':
            return language
    
    return None

def should_translate_po_file(po_file, source_language="eng_Latn"):
    """Determine if a PO file should be translated based on its language metadata"""
    po_language = get_po_language(po_file)
    
    # If no language is set, assume it's meant to be translated
    if not po_language:
        return True
    
    # Convert common language codes to NLLB format for comparison
    source_lang_short = source_language.split('_')[0] if '_' in source_language else source_language
    
    # Handle common language code variations
    if po_language.lower() in ['en', 'eng', 'english']:
        return source_lang_short.lower() in ['en', 'eng', 'english']
    elif po_language.lower() in ['fr', 'fra', 'french']:
        return source_lang_short.lower() in ['fr', 'fra', 'french']
    elif po_language.lower() in ['es', 'spa', 'spanish']:
        return source_lang_short.lower() in ['es', 'spa', 'spanish']
    elif po_language.lower() in ['de', 'deu', 'german']:
        return source_lang_short.lower() in ['de', 'deu', 'german']
    
    # Default: check if the language matches the source
    return po_language.lower() == source_lang_short.lower()

def update_po_with_translations(po_file, translations_dict, force=False):
    """Update PO file entries with translations"""
    if force:
        # Update all entries, including already translated ones
        for entry in po_file:
            if entry.msgid in translations_dict:
                entry.msgstr = translations_dict[entry.msgid]
    else:
        # Update only untranslated entries
        for entry in po_file.untranslated_entries():
            if entry.msgid in translations_dict:
                entry.msgstr = translations_dict[entry.msgid]
    
def save_po_file(po_file, filepath):
    """Save PO file to specified path"""
    po_file.save(filepath)
