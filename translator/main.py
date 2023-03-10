import os, sys

from langcodes import closest_supported_match
from multiprocessing import Queue, Process
from threading import Thread
from pathlib import Path
from argparse import ArgumentParser
from datasets import load_dataset
from halo import Halo
from translator import Translator, LANGS, utils, __version__


from tqdm import tqdm

def get_sys_lang_format():
    i18n = os.environ.get('LANG', "en_EN.UTF-8").split(".")[0]
    return closest_supported_match(i18n, LANGS)

def parse_arguments():
    argument_parse = ArgumentParser(description="Translate [FROM one language] [TO another], [any SENTENCE you would like].")
    argument_parse.add_argument('-v', '--version', action='store_true', help="shows the current version of translator")
    argument_parse.add_argument('_from', nargs='?', default=["eng_Latn"], help="Source language to translate from.")
    argument_parse.add_argument('_to', nargs='?', default=[get_sys_lang_format()], help="Target language to translate towards.")
    argument_parse.add_argument('sentence', nargs="*", default=["Translator version:"], help="Something to translate.")
    argument_parse.add_argument('-d', '--directory', type=str, help="Path to directory to translate in batch instead of unique sentence.")
    argument_parse.add_argument('-S', '--save', type=str, help="Path to text file to save translations.")
    argument_parse.add_argument('-l', '--max_length', default=500, help="Max length of output.")
    argument_parse.add_argument('-m', '--model_id', default="facebook/nllb-200-distilled-600M", help="HuggingFace model ID to use.")
    argument_parse.add_argument('-p', '--pipeline', default="translation", help="Pipeline task to use.")
    argument_parse.add_argument('-L', '--language_list', action='store_true', help="Show list of languages.")

    return argument_parse.parse_args()

def translate_sentence(sentence, translator):
    return translator.translate(sentence)

def main():
    args = parse_arguments()

    spinner = Halo(spinner="pong")

    if args.language_list:
        print("Language list:")
        for l in LANGS:
            print(f"- {l}")
        print()
        sys.exit(0)

    _from, _to = "".join(args._from), "".join(args._to)

    if args.version:
        if _from == _to == "eng_Latn":
            print(f"Translator version: {__version__}")
        else:
            spinner.start()
            translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline)
            version = translate_sentence(args.sentence, translator)
            spinner.stop()
            print(version[0], " ", __version__)
        sys.exit(0)

    for _lang in [_from, _to]:
        if _lang not in LANGS and args.model_id == "facebook/nllb-200-distilled-600M":
            print(f"Warning! {_lang=} is not in listed as supported by the current model.")
            print("There is a high probability translation operations will fail.")
            print("Type translate --language_list to get the full list of supported languages.")
            print("Or type translate --help to get help.")

    #print("Preparing to translate...")
    #print("Please be patient.")
    spinner.start()

    translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline)

    translations = []

    spinner.stop()

    if args.directory and Path(args.directory).exists():
        print("No sentence was given but directory was provided.")
        print(f"Translating sentences in {args._from} to {args._to} from text files in directory \'{args.directory}\'")
        print(f"Using {translator.device} to batch translate")
        source_path = args.directory
        output_path = args.save
        print("Translating files...")
        txt_files = utils.glob_files_from_dir(source_path, suffix=".txt")
        _l = len(txt_files)
        print(f"Found {_l} text file{'s' if _l > 1 else ''}.")
        
        try:
            print("Loading dataset...")
            dataset = load_dataset('text', data_files={'translate': txt_files})

            print("Translating dataset...")
            print("Please wait. This can take a while depending on the amount of data and your computing platform.")
            spinner.start()
            
            translations = translate_sentence(dataset['translate']['text'], translator)
            
            spinner.stop()
            print(f"All files in {args.directory} have been translated from {args.source} to {args.target}.")
        except KeyboardInterrupt as e:
            print()
            print("You are about to loose your progress!")
            sys.exit(1)
    else:
        translation = translate_sentence(args.sentence, translator)
        for t in translation: print(t)
        translations.append(translation)
    
    if args.save:
        if not Path(args.save).exists():
            utils.save_txt(translations, Path(args.save))
        else:
            print(f"{args.save} exists already.")
            print("Please mind the following fact:")
            print("Translated sentences will be added at the end of the file.")
            utils.save_txt(translations, Path(args.save), append=True)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)