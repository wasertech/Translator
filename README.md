# Translator
*`Translate`* *`from` one language* *`to` another*, *any `sentence` you would like*.

```zsh
# Translate [FROM] [TO] [SENTENCES]
❯ translate fra_Latn eng_Latn "Traduisez quelle que soit la phrase que vous voulez."
Translate whatever sentence you want.
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
usage: translate [-h] [-v] [-d DIRECTORY] [-S SAVE] [-l MAX_LENGTH] [-m MODEL_ID] [-p PIPELINE] [-b BATCH_SIZE] [-n NPROC] [-L]
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
  -L, --language_list   Show list of languages.
```

You can `translate` `from` one language `to` another, any `sentence` you would like.

```zsh
# Translate from English in French
❯ translate eng_Latn fra_Latn "This is French."
C\'est français.

# Translate from English in Spanish
❯ translate eng_Latn spa_Latn "This is Spanish."
Esto es español.
```

You can also easily `translate` files from a `--directory` and `--save` to a file.

```zsh
❯ translate --directory . --save en2fr.txt eng_Latn fra_Latn 
```

Using `Translator` with `python`.

```python
from translator import Translator

translator = Translator("eng_Latn", "fra_Latn")

english_sentence = "This is just a simple phrase." or [
    "Those are multiples sentences.",
    "If you have lots of them, load them directly from file",
    "To efficeienty batch translate them."
  ]
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
