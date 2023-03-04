import os, sys

from multiprocessing import Queue, Process
from threading import Thread
from pathlib import Path
from argparse import ArgumentParser
from translator import Translator, LANGS, utils, __version__

from tqdm import tqdm

def parse_arguments():
    argument_parse = ArgumentParser(description="Translate from one language to another.")
    argument_parse.add_argument('-v', '--version', action='store_true', help="shows the current version of translator")
    argument_parse.add_argument('sentence', nargs="*", help="Something to translate.")
    argument_parse.add_argument('-d', '--directory', type=str, help="Path to directory to translate in batch instead of unique sentence.")
    argument_parse.add_argument('-S', '--save', type=str, help="Path to text file to save translations.")
    argument_parse.add_argument('-s', '--source', default="eng_Latn", help="Source language to translate.")
    argument_parse.add_argument('-t', '--target', default="fra_Latn", help="Target language to translate.")
    argument_parse.add_argument('-l', '--max_length', default=500, help="Max length of output.")
    argument_parse.add_argument('-m', '--model_id', default="facebook/nllb-200-distilled-600M", help="HuggingFace model ID to use.")
    argument_parse.add_argument('-p', '--pipeline', default="translation", help="Pipeline task to use.")
    argument_parse.add_argument('-L', '--language_list', action='store_true', help="Show list of languages.")

    return argument_parse.parse_args()

def translate_sentence(sentence, translator):
    return translator.translate(sentence)

def main():
    args = parse_arguments()
    
    if args.version:
        print(f"Translator version {__version__}")
        sys.exit(0)
    
    if args.language_list:
        print("Language list:")
        for l in LANGS:
            print(f"- {l}")
        print()
        sys.exit(0)

    print("Preparing to translate...")
    print("Please be patient.")

    translator = Translator(args.source, args.target, args.max_length, args.model_id, args.pipeline)

    translations = []

    if not args.sentence and Path(args.directory).exists():
        print("No sentence was given but directory was provided.")
        print(f"Translating sentences in {args.source} to {args.target} from text files in directory \'{args.directory}\'")
        source_path = args.directory
        output_path = args.save
        print("Translating files...")
        txt_files = utils.glob_files_from_dir(source_path, suffix=".txt")
        _l = len(txt_files)
        print(f"Found {_l} text file{'s' if _l > 1 else ''}.")
        
        try:
            _files = tqdm(txt_files, position=1)
            for _f in _files:
                _t = _f.replace(".txt", f"{translator.source}-{translator.target}.txt")
                if not Path(_t).exists():
                    _files.set_description(f"Translating file {_f}...")
                    _b = _f.replace('.txt', f'.{translator.target}.tmp.txt')
                    translated_sentences = utils.read_txt(_b)
                    _i = 0
                    i = len(translated_sentences) - 1
                    with open(_f) as f:
                        _lines = tqdm(f.readlines(), position=0)
                        for sentence in _lines:
                            if _i >= 100 and args.save:
                                _lines.set_description("Saving buffer...")
                                utils.save_txt(translated_sentences, _b)
                                _i = 0
                            if sentence not in translated_sentences:
                                sentence = sentence.strip().replace("\n", "")
                                _lines.set_description(f"Translating \"{sentence}\"...")
                                translation = translate_sentence(sentence, translator)
                                _lines.set_description(f"Translated as \"{translation}\".")
                                translated_sentences.append(translation)
                                _i += 1
                    
                    if Path(_b).exists():
                        os.remove(_b)
                elif args.save:
                    _files.set_description(f"Translated file {_f}.")

                if args.save:
                    translations += translated_sentences
                    utils.save_txt(translated_sentences, _t)
                    
            print(f"All files in {args.directory} have been translated from {args.source} to {args.target}.")
        except KeyboardInterrupt as e:
            print("You are about to loose your progress!")
            print("Let me at least save the current progress.")
            print("You can thank me later.")
            utils.save_txt(translated_sentences, _b)
            print("Done.")
            print("You're welcome.")
            raise e
    else:
        translation = translate_sentence(args.sentence, translator)
        print(translation)
        translations.append(translation)
    
    if args.save:
        if not Path(args.save).exists():
            utils.save_txt(translations, Path(args.save))
        else:
            print(f"{args.save} exists already. Please specify another path or (re)move {args.save}.")
            print("What? Do you expect this program to append to the end of the file in this case?")
            print("It still would require user input confirmation but it can be done.")
            print(f"But not with this version of Translator ({__version__}).")
            print("Feel free to open a pull request: https://github.com/wasertech/Translator")

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)