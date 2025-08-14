# Test PO File Translation Feature

This document provides test cases for the new PO file translation functionality.

## New Features in PO Translation

### Language-Aware Translation
- **Smart Language Detection**: Reads Language metadata from PO files
- **Multi-Language Project Support**: Only translates files matching source language
- **Recursive Directory Search**: Finds PO files in nested directory structures

### Force Translation Mode
- **`--force` flag**: Translates all entries, including already translated ones
- **Default behavior**: Only translates untranslated entries (empty msgstr fields)

## Test Setup

Create test locale directory structure (Django-style):

```bash
# Create test locale directories
mkdir -p test_locale/en/LC_MESSAGES
mkdir -p test_locale/fr/LC_MESSAGES

# Create English PO file
cat > test_locale/en/LC_MESSAGES/django.po << 'EOF'
msgid ""
msgstr ""
"Project-Id-Version: Test Project 1.0\n"
"Language: en\n"
"Content-Type: text/plain; charset=UTF-8\n"

msgid "Hello"
msgstr ""

msgid "Goodbye" 
msgstr ""

msgid "Thank you"
msgstr ""
EOF

# Create French PO file with some existing translations
cat > test_locale/fr/LC_MESSAGES/django.po << 'EOF'
msgid ""
msgstr ""
"Project-Id-Version: Test Project 1.0\n"
"Language: fr\n"
"Content-Type: text/plain; charset=UTF-8\n"

msgid "Hello"
msgstr "Bonjour"

msgid "Goodbye" 
msgstr ""

msgid "Thank you"
msgstr "Merci"
EOF
```

## Test Cases

### 1. Single PO File Translation

```bash
# Test translating a single English PO file to Spanish
translate --po eng_Latn spa_Latn test_locale/en/LC_MESSAGES/django.po
```

**Expected Result:**
- English PO file is updated with Spanish translations
- Only untranslated entries (empty msgstr) are modified
- Language metadata is preserved

### 2. Smart Directory Translation

```bash
# Test translating English files to French in a multi-language project
translate --po --directory test_locale eng_Latn fra_Latn
```

**Expected Result:**
- Only English PO files (Language: en) are translated
- French PO files are skipped (Language: fr doesn't match source)
- Logs show "Skipping" messages for non-matching files
- Recursive search finds files in subdirectories

### 3. Force Translation Mode

```bash
# Force retranslation of all entries, including already translated ones
translate --po --force --directory test_locale fra_Latn eng_Latn
```

**Expected Result:**
- All entries in French PO files are retranslated to English
- Even entries with existing translations are overwritten
- Logs show "all entries (force mode)" instead of "untranslated entries"

### 4. Language Mismatch Handling

```bash
# Try to translate French files with English as source
translate --po --directory test_locale eng_Latn spa_Latn
```

**Expected Result:**
- French PO files are skipped with language mismatch warning
- Only English PO files are processed
- Clear logging about why files were skipped

### 5. Verify PO File Structure

After translation, verify:
- ✅ File structure preserved (headers, comments, etc.)
- ✅ Language metadata unchanged
- ✅ Only `msgstr` fields updated (or all fields in force mode)
- ✅ `msgid` fields unchanged
- ✅ Recursive directory scanning works

## Manual Testing

You can test the utility functions directly:

```python
import sys
sys.path.append('translator')
import utils

# Test reading PO file
po_file = utils.read_po_file('test_locale/en/LC_MESSAGES/django.po')
print(f"Loaded {len(po_file)} entries")

# Test language detection
language = utils.get_po_language(po_file)
print(f"Detected language: {language}")

# Test should translate logic
should_translate = utils.should_translate_po_file(po_file, 'eng_Latn')
print(f"Should translate (eng_Latn): {should_translate}")

# Test extracting untranslated vs all entries
untranslated = utils.extract_untranslated_from_po(po_file)
all_entries = utils.extract_all_from_po(po_file)
print(f"Untranslated: {len(untranslated)}, All: {len(all_entries)}")

# Test recursive directory scanning
po_files = utils.glob_po_files_from_dir('test_locale')
print(f"Found {len(po_files)} PO files recursively")
for po_file in po_files:
    print(f"  - {po_file}")
```

## Integration Points

The feature integrates with existing translator functionality:
- Uses same translation models and algorithms
- Respects batch size and processing options
- Follows same logging and progress reporting patterns
- Compatible with all supported languages

## Command Line Examples

### Basic Usage
```bash
# Translate single PO file
translate --po eng_Latn spa_Latn messages.po

# Translate directory with language awareness
translate --po --directory locales eng_Latn fra_Latn

# Force retranslation of all entries
translate --po --force --directory locales eng_Latn deu_Latn
```

### Real-World Django Example
```bash
# In a Django project root with locale/ directory
translate --po --directory . eng_Latn fra_Latn

# This will:
# - Find locale/en/LC_MESSAGES/*.po files and translate them
# - Skip locale/fr/LC_MESSAGES/*.po files (wrong source language)
# - Skip locale/es/LC_MESSAGES/*.po files (wrong source language)
```

## Troubleshooting

### "language mismatch" warnings
- Check the Language field in your PO file metadata
- Ensure it matches your source language parameter
- Use `--force` with the correct source language if needed

### No files found
- Ensure you're using `--directory` for directory scanning
- Check that PO files have Language metadata set
- Verify file permissions and paths