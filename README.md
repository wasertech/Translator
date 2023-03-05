# Translator
Translate from one language to another.

```zsh
❯ translate --source eng_Latn --target fra_Latn "This is an original sentence."
Ceci est une phrase originale.
```

Uses Meta's NLLB model [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M) by default. You can change it by passing a custom flag `--model_id`.


## Installation

Use `pip` to install Translator (only from source for now).

```zsh
pip install git+https://github.com/wasertech/Translator.git
which translate
```

## Usage

Using `translate` from your favorite shell.

```zsh
# Meet Translate
❯ translate --help
usage: translate [-h] [-v] [-d DIRECTORY] [-S SAVE] [-l MAX_LENGTH] [-m MODEL_ID] [-p PIPELINE] [-L] _from _to [sentence ...]

Translate [FROM one language] [TO another].

positional arguments:
  _from                 Source language to translate from.
  _to                   Target language to translate towards.
  sentence              Something to translate.

options:
  -h, --help            show this help message and exit
  -v, --version         shows the current version of translator
  -d DIRECTORY, --directory DIRECTORY
                        Path to directory to translate in batch instead of unique sentence.
  -S SAVE, --save SAVE  Path to text file to save translations.
  -l MAX_LENGTH, --max_length MAX_LENGTH
                        Max length of output.
  -m MODEL_ID, --model_id MODEL_ID
                        HuggingFace model ID to use.
  -p PIPELINE, --pipeline PIPELINE
                        Pipeline task to use.
  -L, --language_list   Show list of languages.


# Translate from English in French
❯ translate eng_Latn fra_Latn "This sentence can be translated in any language now."
Cette phrase peut être traduite dans n\'importe quelle langue maintenant.

# Translate from English in Spanish
❯ translate eng_Latn spa_Latn "This sentence can be translated in any language now."
Esta frase puede traducirse a cualquier idioma ahora.

# Loading sentences from text files from  --directory (-d)
# and --save (-S) the translated sentences to a text file
❯ translate --directory . --save en2fr.txt eng_Latn fra_Latn & bg
# during the translation process
# two buffer files are created
❯ ls ./*.eng_Latn.tmp.txt
❯ ls ./*.fra_Latn.tmp.txt
# This allows for interuptions in the process...
# At the end of the process
❯ fg
# Only when all sentences have been translated, result is saved:
# -   under each respective file
❯ ls ./*.fra_Latn.txt
# -   under --save (-S) if given
❯ cat en2fr.txt | head
# Buffers are also removed
❯ ls *.tmp.txt
```

Using `Translator` with `python`.

```python
from translator import Translator

translator = Translator("eng_Latn", "fra_Latn")

english_sentence = "This is just a simple phrase."
french_sentence = translator.translate(english_sentence)

print(f"{english_sentence=}")
print(f"{french_sentence=}")
```

## Languages

Depending on models used, you might get fewer choices but with `NLLB` you get more than 200 most popular ones.

```zsh
# translate -L
❯ translate --language_list
Language list:
    ...
```

From `python`:
```python
import translator
>>> len(translator.LANGS)
202
>>> translator.LANGS
['ace_Arab', '...', 'zul_Latn']
```

Checkout [`LANGS`](translator/__init__.py) to see the full list of supported languages.

## License

This project is distributed under [Mozilla Public License 2.0](LICENSE).

Using this tool to translate a sentence, the licence of the original sentence still applies unless specified otherwise.

Meaning, if you translate a sentence under [Creative Commons CC0](https://creativecommons.org/share-your-work/public-domain/cc0/), the translation is also under Creative Commons CC0.

Idem for any licence.

## Contribution

I love stars ⭐ but also chocolate 🍫 so don't hesitate to [sponsor this project](https://github.com/sponsors/wasertech)!

Otherwise if you like the project and want to see it grow and get more convenience features like a dedicated service/client to speed up multiple translations. Don't hesitate to share your ideas by opening a ticket or even proposing a pull request.
