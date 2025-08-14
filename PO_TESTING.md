# Test PO File Translation Feature

This document provides test cases for the new PO file translation functionality.

## Test Setup

Create test PO files:

```bash
# Create test directory
mkdir -p test_po_files

# Create test PO file 1
cat > test_po_files/messages.po << 'EOF'
msgid ""
msgstr ""
"Project-Id-Version: Test Project 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"

msgid "Hello"
msgstr ""

msgid "Goodbye" 
msgstr ""

msgid "Thank you"
msgstr ""
EOF

# Create test PO file 2
cat > test_po_files/errors.po << 'EOF'
msgid ""
msgstr ""
"Project-Id-Version: Test Project 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"

msgid "Error"
msgstr ""

msgid "Warning"
msgstr ""
EOF
```

## Test Cases

### 1. Single PO File Translation

```bash
# Test translating a single PO file
translate --po eng_Latn spa_Latn test_po_files/messages.po
```

**Expected Result:**
- PO file is updated with Spanish translations
- Original structure and metadata preserved
- Only untranslated entries are modified

### 2. Directory PO File Translation

```bash
# Test translating all PO files in directory
translate --po --directory test_po_files eng_Latn fra_Latn
```

**Expected Result:**
- All `.po` files in directory are processed
- Each file gets appropriate translations
- Log shows progress for each file

### 3. Verify PO File Structure

After translation, verify:
- ✅ File structure preserved (headers, comments, etc.)
- ✅ Metadata unchanged (`Project-Id-Version`, etc.)
- ✅ Only `msgstr` fields updated
- ✅ `msgid` fields unchanged

## Manual Testing

You can test the utility functions directly:

```python
import sys
sys.path.append('translator')
import utils

# Test reading PO file
po_file = utils.read_po_file('test_po_files/messages.po')
print(f"Loaded {len(po_file)} entries")

# Test extracting untranslated
untranslated = utils.extract_untranslated_from_po(po_file)
print(f"Found {len(untranslated)} untranslated entries")

# Test directory scanning
po_files = utils.glob_po_files_from_dir('test_po_files')
print(f"Found {len(po_files)} PO files")
```

## Integration Points

The feature integrates with existing translator functionality:
- Uses same translation models and algorithms
- Respects batch size and processing options
- Follows same logging and progress reporting patterns
- Compatible with all supported languages