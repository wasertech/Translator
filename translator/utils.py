import time
import os

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

def should_translate_po_file(po_file, target_language):
    """Determine if a PO file should be translated based on its language metadata matching target language"""
    po_language = get_po_language(po_file)
    
    # If no language is set, assume it should be translated ONLY if user explicitly sets Language metadata
    if not po_language:
        return False  # Require explicit Language metadata for safety
    
    # Convert target language to short code for comparison
    target_short = nllb_to_short_code(target_language)
    
    # Handle common language code variations - check if PO language matches target
    po_lang_lower = po_language.lower()
    target_short_lower = target_short.lower()
    
    # Direct match
    if po_lang_lower == target_short_lower:
        return True
    
    # Common variations
    target_variations = {
        'en': ['en', 'eng', 'english'],
        'fr': ['fr', 'fra', 'french'],
        'es': ['es', 'spa', 'spanish'],
        'de': ['de', 'deu', 'german'],
        'it': ['it', 'ita', 'italian'],
        'pt': ['pt', 'por', 'portuguese'],
        'ru': ['ru', 'rus', 'russian'],
        'ja': ['ja', 'jpn', 'japanese'],
        'ko': ['ko', 'kor', 'korean'],
        'zh': ['zh', 'zho', 'chinese'],
        'ar': ['ar', 'arb', 'arabic'],
        'hi': ['hi', 'hin', 'hindi'],
        'bn': ['bn', 'ben', 'bengali'],
        'tr': ['tr', 'tur', 'turkish'],
        'nl': ['nl', 'nld', 'dutch'],
        'sv': ['sv', 'swe', 'swedish'],
        'da': ['da', 'dan', 'danish'],
        'no': ['no', 'nob', 'norwegian'],
        'fi': ['fi', 'fin', 'finnish'],
        'pl': ['pl', 'pol', 'polish'],
    }
    
    # Check if PO language matches any variation of target language
    for variations in target_variations.values():
        if target_short_lower in variations and po_lang_lower in variations:
            return True
    
    return False

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

def normalize_language_code(lang_code):
    """Convert short language codes to NLLB format and vice versa"""
    if not lang_code:
        return lang_code
        
    # Common mappings from short codes to NLLB codes
    short_to_nllb = {
        'en': 'eng_Latn',
        'fr': 'fra_Latn', 
        'es': 'spa_Latn',
        'de': 'deu_Latn',
        'it': 'ita_Latn',
        'pt': 'por_Latn',
        'ru': 'rus_Cyrl',
        'ja': 'jpn_Jpan',
        'ko': 'kor_Hang',
        'zh': 'zho_Hans',
        'ar': 'arb_Arab',
        'hi': 'hin_Deva',
        'bn': 'ben_Beng',
        'tr': 'tur_Latn',
        'nl': 'nld_Latn',
        'sv': 'swe_Latn',
        'da': 'dan_Latn',
        'no': 'nob_Latn',
        'fi': 'fin_Latn',
        'pl': 'pol_Latn',
        'cs': 'ces_Latn',
        'hu': 'hun_Latn',
        'ro': 'ron_Latn',
        'uk': 'ukr_Cyrl',
        'bg': 'bul_Cyrl',
        'hr': 'hrv_Latn',
        'sk': 'slk_Latn',
        'sl': 'slv_Latn',
        'et': 'est_Latn',
        'lv': 'lvs_Latn',
        'lt': 'lit_Latn',
        'mt': 'mlt_Latn',
        'el': 'ell_Grek',
        'cy': 'cym_Latn',
        'ga': 'gle_Latn',
        'eu': 'eus_Latn',
        'ca': 'cat_Latn',
        'gl': 'glg_Latn',
        'is': 'isl_Latn',
        'mk': 'mkd_Cyrl',
        'sq': 'als_Latn',
        'be': 'bel_Cyrl',
        'ka': 'kat_Geor',
        'hy': 'hye_Armn',
        'az': 'azj_Latn',
        'kk': 'kaz_Cyrl',
        'ky': 'kir_Cyrl',
        'uz': 'uzn_Latn',
        'tk': 'tuk_Latn',
        'mn': 'khk_Cyrl',
        'th': 'tha_Thai',
        'vi': 'vie_Latn',
        'id': 'ind_Latn',
        'ms': 'zsm_Latn',
        'tl': 'tgl_Latn',
        'my': 'mya_Mymr',
        'km': 'khm_Khmr',
        'lo': 'lao_Laoo',
        'am': 'amh_Ethi',
        'ti': 'tir_Ethi',
        'or': 'ory_Orya',
        'as': 'asm_Beng',
        'ur': 'urd_Arab',
        'fa': 'pes_Arab',
        'ps': 'pbt_Arab',
        'sd': 'snd_Arab',
        'ne': 'npi_Deva',
        'si': 'sin_Sinh',
        'ta': 'tam_Taml',
        'te': 'tel_Telu',
        'kn': 'kan_Knda',
        'ml': 'mal_Mlym',
        'gu': 'guj_Gujr',
        'pa': 'pan_Guru',
        'mr': 'mar_Deva',
        'sa': 'san_Deva',
        'sw': 'swh_Latn',
        'yo': 'yor_Latn',
        'ig': 'ibo_Latn',
        'ha': 'hau_Latn',
        'zu': 'zul_Latn',
        'xh': 'xho_Latn',
        'af': 'afr_Latn',
        'he': 'heb_Hebr',
        'yi': 'ydd_Hebr',
    }
    
    # If it's a short code, convert to NLLB
    if lang_code.lower() in short_to_nllb:
        return short_to_nllb[lang_code.lower()]
    
    # If it's already an NLLB code, return as is
    if '_' in lang_code and len(lang_code) > 3:
        return lang_code
        
    # Return as is if no mapping found
    return lang_code

def nllb_to_short_code(nllb_code):
    """Convert NLLB language code to short code for directory matching"""
    short_to_nllb = {
        'en': 'eng_Latn',
        'fr': 'fra_Latn', 
        'es': 'spa_Latn',
        'de': 'deu_Latn',
        'it': 'ita_Latn',
        'pt': 'por_Latn',
        'ru': 'rus_Cyrl',
        'ja': 'jpn_Jpan',
        'ko': 'kor_Hang',
        'zh': 'zho_Hans',
        'ar': 'arb_Arab',
        'hi': 'hin_Deva',
        'bn': 'ben_Beng',
        'tr': 'tur_Latn',
        'nl': 'nld_Latn',
        'sv': 'swe_Latn',
        'da': 'dan_Latn',
        'no': 'nob_Latn',
        'fi': 'fin_Latn',
        'pl': 'pol_Latn',
        'cs': 'ces_Latn',
        'hu': 'hun_Latn',
        'ro': 'ron_Latn',
        'uk': 'ukr_Cyrl',
        'bg': 'bul_Cyrl',
        'hr': 'hrv_Latn',
        'sk': 'slk_Latn',
        'sl': 'slv_Latn',
        'et': 'est_Latn',
        'lv': 'lvs_Latn',
        'lt': 'lit_Latn',
        'mt': 'mlt_Latn',
        'el': 'ell_Grek',
        'cy': 'cym_Latn',
        'ga': 'gle_Latn',
        'eu': 'eus_Latn',
        'ca': 'cat_Latn',
        'gl': 'glg_Latn',
        'is': 'isl_Latn',
        'mk': 'mkd_Cyrl',
        'sq': 'als_Latn',
        'be': 'bel_Cyrl',
        'ka': 'kat_Geor',
        'hy': 'hye_Armn',
        'az': 'azj_Latn',
        'kk': 'kaz_Cyrl',
        'ky': 'kir_Cyrl',
        'uz': 'uzn_Latn',
        'tk': 'tuk_Latn',
        'mn': 'khk_Cyrl',
        'th': 'tha_Thai',
        'vi': 'vie_Latn',
        'id': 'ind_Latn',
        'ms': 'zsm_Latn',
        'tl': 'tgl_Latn',
        'my': 'mya_Mymr',
        'km': 'khm_Khmr',
        'lo': 'lao_Laoo',
        'am': 'amh_Ethi',
        'ti': 'tir_Ethi',
        'or': 'ory_Orya',
        'as': 'asm_Beng',
        'ur': 'urd_Arab',
        'fa': 'pes_Arab',
        'ps': 'pbt_Arab',
        'sd': 'snd_Arab',
        'ne': 'npi_Deva',
        'si': 'sin_Sinh',
        'ta': 'tam_Taml',
        'te': 'tel_Telu',
        'kn': 'kan_Knda',
        'ml': 'mal_Mlym',
        'gu': 'guj_Gujr',
        'pa': 'pan_Guru',
        'mr': 'mar_Deva',
        'sa': 'san_Deva',
        'sw': 'swh_Latn',
        'yo': 'yor_Latn',
        'ig': 'ibo_Latn',
        'ha': 'hau_Latn',
        'zu': 'zul_Latn',
        'xh': 'xho_Latn',
        'af': 'afr_Latn',
        'he': 'heb_Hebr',
        'yi': 'ydd_Hebr',
    }
    
    # Create reverse mapping
    nllb_to_short = {v: k for k, v in short_to_nllb.items()}
    
    return nllb_to_short.get(nllb_code, nllb_code.split('_')[0] if '_' in nllb_code else nllb_code)

def glob_po_files_for_target_language(directory, target_language, suffix=".po"):
    """Get PO files from target language directories only"""
    po_files = []
    
    # Convert target language to short code for directory matching
    target_short = nllb_to_short_code(target_language)
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(suffix) and not file.endswith(f".tmp{suffix}"):
                file_path = os.path.join(root, file)
                
                # Check if this file is in a target language directory
                rel_path = os.path.relpath(file_path, directory)
                path_parts = rel_path.split(os.sep)
                
                # Check if any part of the path matches our target language
                for part in path_parts:
                    if part == target_short:
                        po_files.append(file_path)
                        break
                    # Also check for exact matches like "locale/fr" pattern
                    if len(path_parts) >= 2:
                        for i in range(len(path_parts) - 1):
                            if path_parts[i] == "locale" and path_parts[i + 1] == target_short:
                                po_files.append(file_path)
                                break
    
    return po_files

def detect_target_languages_from_directory(directory):
    """Detect all target languages available in the directory structure"""
    target_languages = set()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.po') and not file.endswith('.tmp.po'):
                file_path = os.path.join(root, file)
                
                # Check if this file has Language metadata
                try:
                    po_file = read_po_file(file_path)
                    lang_metadata = po_file.metadata.get('Language', '').strip()
                    
                    if lang_metadata:
                        # Convert short code to NLLB format if needed
                        target_lang = normalize_language_code(lang_metadata)
                        if target_lang != 'eng_Latn':  # Don't include source language
                            target_languages.add(target_lang)
                except Exception:
                    # Skip files that can't be read
                    continue
    
    return sorted(list(target_languages))
