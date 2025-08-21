# Interpres — Translator

Translate text and files between languages using Hugging Face translation models (default: Meta NLLB).

Interpres (Translator) is a lightweight CLI and Python package for fast, batch-friendly translation workflows. It supports single-sentence translation, directory and file translation, and robust PO (gettext) file handling for localization workflows.

## Key features
- CLI + Python API
- Default model: [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M) (configurable)
- Fast batch translation with configurable batch size, epochs, and parallelism
- Full support for PO files: preserves metadata, comments, and structure; translates only untranslated entries by default; force retranslate option
- Language list compatible with NLLB (200+ languages)

## Quick install

pip:
```zsh
pip install interpres
```

Install from source:
```zsh
pip install git+https://github.com/wasertech/Translator.git
```

Specify a release:
```zsh
pip install interpres==0.3.1b4
pip install git+https://github.com/wasertech/Translator.git@v0.3.1b4
```

## CLI overview

Run:
```zsh
translate [FROM] [TO] [SENTENCES...]
```

### Basic examples:
```zsh
# Single sentence
translate en fr "This is a test."

# Interactive shell
translate
# or get help
translate --help

# Translate a directory and save output
translate --directory ./texts --save translations.txt eng_Latn fra_Latn
```

### Important options (common)
- -m, --model_id MODEL_ID : Hugging Face model ID to use
- -d, --directory DIRECTORY : Translate files in a directory
- --po : Translate PO files (gettext)
- --force : Force retranslation (including already translated entries)
- -b, --batch_size : Batch size for model inference
- -e, --nepoch : Number of epoch splits used to pipeline batches (tweak to avoid OOM)
- -n, --nproc : Number of CPU workers for preprocessing/filtering
- -L, --language_list : Show supported languages

### PO-file translation (high level)
- Finds .po files recursively and validates Language metadata
- By default translates empty msgstr entries only
- --force reprocesses every entry
- Preserves comments, headers, and file formatting — ideal for Poedit/Django workflows

## Python API (simple)
```python
from translator import Translator

t = Translator("eng_Latn", "fra_Latn")
out = t.translate("This is a simple sentence.")
print(out)
```

## PO-file example (Python)
```python
from translator import Translator, utils

translator = Translator("eng_Latn", "spa_Latn")
po = utils.read_po_file("messages.po")

if utils.should_translate_po_file(po, "eng_Latn"):
    entries = utils.extract_untranslated_from_po(po)
    translations = translator.translate(entries)
    mapping = dict(zip(entries, translations))
    utils.update_po_with_translations(po, mapping, force=False)
    utils.save_po_file(po, "messages.po")
```

## Language support
Depending on models used, you might get fewer choices 
but with `NLLB` you get more than 200 most popular ones.

```zsh
# translate -L
❯ translate --language_list
Language list:
    ...
```

From `python`:
```python
>>> import translator
>>> len(translator.LANGS)
202
>>> translator.LANGS
['ace_Arab', '...', 'zul_Latn']
>>> from translator.language import get_nllb_lang, get_sys_lang_format
>>> nllb_lang = get_nllb_lang("en")
>>> nllb_lang
'eng_Latn'
>>> get_sys_lang_format()
'fra_Latn'
```

Checkout [`LANGS`](translator/language.py) to see the full list of supported languages.

## Custom models
- Use any [Hugging Face translation model](https://huggingface.co/models?pipeline_tag=translation&sort=downloads) compatible with the Transformers pipeline:
  `translate --model_id "HUGGINGFACE/MODEL_ID" ...`
- Prefer models that match your language pair and domain. Models trained or fine-tuned specifically for a given language pair (e.g., en→fr) often produce noticeably better results than general multilingual models.
- Domain/context-specific models are best: if you're translating a website, a model trained on website or localization data (or fine-tuned on your site's content) will usually yield more accurate, consistent, and context-aware translations than the default general-purpose model.

## Performance tips
- Set nepoch (-e) and batch_size (-b) to fit your device memory. Bigger batch_size speeds throughput but uses more memory.
- Use -n to match your CPU threads for preprocessing speed.
- Use custom models: choosing a language-pair-specific or domain-specific model (or fine-tuning one on your data) often improves translation quality and consistency, especially for specialized content such as legal texts, technical docs, or websites.

## License
Mozilla Public License 2.0 — see [LICENSE](LICENSE)

Using this tool to translate a sentence, the licence of the original sentence still applies unless specified otherwise.

Meaning, if you translate a sentence under [Creative Commons CC0](https://creativecommons.org/share-your-work/public-domain/cc0/), the translation is also under Creative Commons CC0.

Idem for any licence.

## Contribute & sponsor
- [Share and talk](https://github.com/wasertech/Translator/discussions/categories/show-and-tell) about translations models you like to use and tell us why.
- [Open issues](https://github.com/wasertech/Translator/issues) or [PRs for features, bugfixes, or performance improvements](https://github.com/wasertech/Translator/pulls).
- [Sponsor this project](https://github.com/sponsors/wasertech)

Thanks for building with Interpres — translate confidently, scale thoughtfully.
