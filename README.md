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
❯ translate --help
usage: translate [-h] [-v] [-d DIRECTORY] [-S SAVE] [-s SOURCE] [-t TARGET]
                 [-l MAX_LENGTH] [-m MODEL_ID] [-p PIPELINE] [-L]
                 [sentence ...]

Translate from one language to another.

positional arguments:
  sentence              Something to translate.

options:
  -h, --help            show this help message and exit
  -v, --version         shows the current version of translator
  -d DIRECTORY, --directory DIRECTORY
                        Path to directory to translate in batch instead of
                        unique sentence.
  -S SAVE, --save SAVE  Path to text file to save translations.
  -s SOURCE, --source SOURCE
                        Source language to translate.
  -t TARGET, --target TARGET
                        Target language to translate.
  -l MAX_LENGTH, --max_length MAX_LENGTH
                        Max length of output.
  -m MODEL_ID, --model_id MODEL_ID
                        HuggingFace model ID to use.
  -p PIPELINE, --pipeline PIPELINE
                        Pipeline task to use.
  -L, --language_list   Show list of languages.

❯ translate --source eng_Latn --target fra_Latn "This sentence can be transcribed in any language now."
Cette phrase peut être transcrite dans n\'importe quelle langue maintenant.

❯ translate -s eng_Latn -t spa_Latn "This sentence can be transcribed in any language now."
Esta frase puede ser transcrita en cualquier idioma ahora.

# Loading sentences from text files in current directory
# and save the translation to a text file
❯ translate -d . -S en2fr.txt -s eng_Latn -t fra_Latn
# during the translation process
# two buffer files are create
❯ cat ./*.eng_Latn.tmp.txt | tail -n 1
❯ cat ./*.fra_Latn.tmp.txt | tail -n 1
# This allows for interuptions in the process
# At the end of the process, translation are saved:
# under each respective file
❯ cat ./*.fra_Latn.txt
# and if flag --save (-S) has been given
❯ cat en2fr.txt
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
