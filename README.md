# Interpres (Translator)

> Latin Noun
>
> **interpres** *m* or *f* (genitive interpretis); third declension
>
> 1. *An agent between two parties*; *broker*, *negotiator*, *factor*. 
>
>>> Synonyms: *cōciō*, *arillātor*
>
>
> 2. *A translator*, *interpreter*, *expounder*, *expositor*, *explainer*; *dragoman*. 
>
>>> Synonyms: *coniector*, *commentātor*, *interpretātor*, *trānslātor*


*`Translate`* *`from` one language* *`to` another*, *any `sentence` you would like*.

```zsh
# Translate [FROM] [TO] [SENTENCES]
❯ translate fr "Traduisez quelle que soit la phrase que vous voulez."
Translate whatever sentence you want.
```

Uses Meta's NLLB model [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M) by default. You can change it by passing a custom flag `--model_id`. Checkout the [Show & Tell discussions](https://github.com/wasertech/Translator/discussions/categories/show-and-tell) to see popular models and share your favorites.

## Installation

Use `pip` to install Translator.

```zsh
❯ pip install interpres
```

Or from source.
```zsh
❯  pip install git+https://github.com/wasertech/Translator.git
```

You can also use a specific version.
```zsh
❯  pip install interpres==0.3.1b4
❯  pip install git+https://github.com/wasertech/Translator.git@v0.3.1b4
```

Locate Translator.
```zsh
❯ which translate
```

## Usage

Using `translate` from your favorite shell.

```zsh
❯ translate help
usage: translate [-h] [-v] [-d DIRECTORY] [--po] [--force] [-S SAVE] [-l MAX_LENGTH] [-m MODEL_ID] [-p PIPELINE] [-b BATCH_SIZE] [-n NPROC] [-e NEPOCH] [-L]
                 [_from] [_to] [sentences ...]

Translate [FROM one language] [TO another], [any SENTENCE you would like].

positional arguments:
  _from                 Source language to translate from.
  _to                   Target language to translate towards.
  sentences             Sentences to translate.

options:
  -h, --help            show this help message and exit
  -v, --version         shows the current version of translator
  -d DIRECTORY, --directory DIRECTORY
                        Path to directory to translate in batch instead of unique sentence.
  --po                  Translate PO (Portable Object) files instead of text files.
  --force               Force translation of all entries in PO files, including already translated ones.
  -S SAVE, --save SAVE  Path to text file to save translations.
  -l MAX_LENGTH, --max_length MAX_LENGTH
                        Max length of output.
  -m MODEL_ID, --model_id MODEL_ID
                        HuggingFace model ID to use.
  -p PIPELINE, --pipeline PIPELINE
                        Pipeline task to use.
  -b BATCH_SIZE, --batch_size BATCH_SIZE
                        Number of sentences to batch for translation.
  -n NPROC, --nproc NPROC
                        Number of process to spawn for filtering untraslated sentences.
  -e NEPOCH, --nepoch NEPOCH
                        Number of epoch(s) to translate batched sentences.
  -L, --language_list   Show list of languages.
```

You can `translate` `from` one language `to` another, any `sentence` you would like.

Greet Translator.
```
❯ translate
ℹ Welcome!
ℹ I am Translator version: 0.3.1b5
ℹ At your service.
? What would you like to translate? Manually typed sentences
ℹ Translating from: Manually typed sentences
? What language to translate from? en
ℹ Translating from eng_Latn.
? What language to translate to? fr
ℹ Translating to fra_Latn.
ℹ Preparing to translate...
Type [Ctrl] + [C] to exit.
          
What would you like to translate?
? Translate: This is a prompt-like translation shell!
C'est une coquille de traduction rapide !

What would you like to translate?
? Translate: You can quickly and effortlessly translate anything from here!
Vous pouvez traduire n'importe quoi rapidement et sans effort.

What would you like to translate?
? Translate: I hope you like my work and are considering becoming a sponsor...
J'espère que vous aimez mon travail et que vous envisagez devenir sponsor...

What would you like to translate?
? Translate:                                                                                                                                                                                 

Cancelled by user
```

Get Translator version.
```zsh
❯ translate version
```

Translate from English in French.
```
❯ translate eng_Latn fra_Latn "This is French."
C'est français.

❯ LANG="fr_CH.UTF-8" translate en "This is also French."
C'est aussi français.
```

Translate from English in Spanish.
```zsh
❯ translate eng_Latn spa_Latn "This is Spanish."
Esto es español.

❯ translate en es "This is also Spanish."
Esto también es español.
```

You can also easily `translate` files from a `--directory` and `--save` to a file.

```zsh
❯ translate --directory . --save en2fr.txt eng_Latn fra_Latn -n 24 -e 1000 -b 64
```

## PO File Translation

Translator supports translating PO (Portable Object) files commonly used with gettext for localization. This is perfect for Poedit workflows and supports multi-language projects.

### Basic Usage

Translate all PO files in a directory:
```zsh
❯ translate --po --directory ./locales eng_Latn fra_Latn
```

Translate a single PO file:
```zsh  
❯ translate --po eng_Latn fra_Latn messages.po
```

### Advanced Features

#### Language-Aware Translation
The `--po` flag includes smart target language detection that looks for PO files in target language directories and validates Language metadata. This ensures you only translate the intended target language files:

```zsh
# In a Django project with locale/en/, locale/fr/, locale/es/ directories
❯ translate --po --directory . eng_Latn fra_Latn
# Finds and translates PO files in locale/fr/ directories with Language: fr metadata

# Short form (defaults source to English)
❯ translate --po --directory . fr
# Equivalent to above - finds French target files and translates from English
```

#### Force Translation Mode
Use `--force` to retranslate all entries in PO files or ignore cache for text files:

```zsh
# For PO files: translate ALL entries, not just empty msgstr fields
❯ translate --po --force --directory locales eng_Latn deu_Latn

# For text files: ignore cache and retranslate everything from scratch
❯ translate --force --directory texts --save output.txt eng_Latn fra_Latn
```

### Key Features

The `--po` mode:
- **Preserves Structure**: Maintains all PO file metadata, comments, and formatting
- **Target Language Detection**: Finds PO files in target language directories and validates Language metadata
- **Selective Translation**: Only translates untranslated entries by default (empty `msgstr` fields)  
- **Multi-Language Safety**: Only processes files in target language directories with matching metadata
- **Recursive Processing**: Finds all `.po` files in nested directory structures
- **Batch Optimization**: Uses Translator's optimized algorithms for efficiency

This allows you to leverage Translator's optimized batch translation algorithm on your localization files while maintaining compatibility with Poedit and other gettext tools.

Define:
  - `--nepoch (-e)` as small as possible but as big as necessary.
    
    Translator uses this number `e` of epoch to determine 
    the rate of time between updates 
    by the amount of sentences 
    given for translation at once.

    If this number is too small, you will face Out-Of-Memory (OOM) errors.
    If it is too big, you will get poor efficency.

    Keep it between 1 and the sum of sentences to translate.

    For maximum efficiency keep it as low as you can while being able 
    to fit `epoch_split` number of sentences 
    into `device`'s memory.

  - `--batch_size (-b)` as big as possible but as small as necessary.

    Translator uses this value every time it needs to batch sentences to work on them.

    Mostly impacts the amount of sentences to batch togheter from `epoch_split` sentences to translate in one go.

    Keep it as high as possible (<`epoch_split`) but as low as your `device` memory allows to (>=1).

    For GPU using multiples of `2` is best for memory optimization 
    (i.e. `2`, `4`, `8`, `16`, `32`, `64`, `128`, `256`, `512`, etc.).

  - `--nproc (-n)` to equal your amount of virtual threads on CPU for maximum performance.

    This value is used by translator everytime multiples sentences need to be processed by the CPU.

    Keeping it at its highest possible value, 
    garanties maximum performances. 

With a good processor and a single fast and large GPU, 
you can translate an average just shy of a 100 sentences per second.

On my Threadripper 2920X's 24 threads, 
using my RTX 3060's 12 Gb of space, 
I can peak at ~97 translations/second averaging a bit lower at 83.

I have not tested yet on my two RTX Titans but if you want to distribute the computation, you'll have to do it manually for now.
It's in my todo list but I won't be offended if you send me a pull request to implement it.

Using `Translator` with `python`.

```python
from translator import Translator

translator = Translator("eng_Latn", "fra_Latn")

english_sentence = "This is just a simple phrase." or [
    "Those are multiples sentences.",
    "If you have lots of them, load them directly from file.",
    "To efficiently batch translate them."
  ]
french_sentence = translator.translate(english_sentence)

print(f"{english_sentence=}")
print(f"{french_sentence=}")
```

For PO file processing:

```python
from translator import Translator, utils

# Initialize translator
translator = Translator("eng_Latn", "spa_Latn")

# Process a PO file
po_file = utils.read_po_file("messages.po")

# Check if file should be translated based on language metadata
if utils.should_translate_po_file(po_file, "eng_Latn"):
    # Extract entries (untranslated by default, or all with force=True)
    untranslated = utils.extract_untranslated_from_po(po_file)
    # For force mode: all_entries = utils.extract_all_from_po(po_file)
    
    # Translate the entries
    translations = translator.translate(untranslated)
    
    # Create translation mapping and update PO file
    translation_dict = dict(zip(untranslated, translations))
    utils.update_po_with_translations(po_file, translation_dict, force=False)
    utils.save_po_file(po_file, "messages.po")
else:
    print("PO file language doesn't match source language")
```

## Languages

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

## Using a custom model

Checkout [HuggingFace Zoo of Translation Models](https://huggingface.co/models?pipeline_tag=translation&sort=downloads).

Or [train your own model](https://huggingface.co/autotrain) for the `translate` or `translate_xx_to_xx` pipeline.

## License

This project is distributed under [Mozilla Public License 2.0](LICENSE).

Using this tool to translate a sentence, 
the licence of the original sentence still applies unless specified otherwise.

Meaning, 
if you translate a sentence 
under [Creative Commons CC0](https://creativecommons.org/share-your-work/public-domain/cc0/), 
the translation is also under Creative Commons CC0.

Idem for any licence.

## Contribution

I love stars ⭐ 
but also chocolate 🍫 
so don't hesitate 
to [sponsor this project](https://github.com/sponsors/wasertech)!

Otherwise 
if you like the project 
and want to see it grow, 
get more convenience features 
like a dedicated service/client 
to speed up multiple translations,
etc. 

Don't hesitate to share your ideas 
by opening a ticket 
or even proposing a pull request.
