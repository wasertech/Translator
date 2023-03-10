import os, sys

from langcodes import closest_supported_match
from multiprocessing import Queue, Process
from threading import Thread
from pathlib import Path
from argparse import ArgumentParser
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
    
    _from, _to = args._from[0], args._to[0]

    if args.version:
        if _from == _to == "eng_Latn":
            print(f"Translator version: {__version__}")
        else:
            translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline)
            version = translator.translate(args.sentence)
            print(version, " ", __version__)
        sys.exit(0)
    
    if args.language_list:
        print("Language list:")
        for l in LANGS:
            print(f"- {l}")
        print()
        sys.exit(0)

    print("Preparing to translate...")
    print("Please be patient.")

    for _lang in [_from, _to]:
        if _lang not in LANGS and args.model_id == "facebook/nllb-200-distilled-600M":
            print(f"Warning! {_lang=} is not in listed as supported by the current model.")
            print("There is a high probability translation operations will fail.")
            print("Type translate --language_list to get the full list of supported languages.")
            print("Or type translate --help to get help.")

    translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline)

    translations = []

    if not args.sentence and Path(args.directory).exists():
        print("No sentence was given but directory was provided.")
        print(f"Translating sentences in {args._from} to {args._to} from text files in directory \'{args.directory}\'")
        source_path = args.directory
        output_path = args.save
        print("Translating files...")
        txt_files = utils.glob_files_from_dir(source_path, suffix=".txt")
        _l = len(txt_files)
        print(f"Found {_l} text file{'s' if _l > 1 else ''}.")
        
        try:
            # Load files
            _files = tqdm(txt_files, position=1)
            for _f in _files:
                _t = _f.replace(".txt", f"{translator.source}-{translator.target}.txt")
                if not Path(_t).exists():
                    _files.set_description(f"Translating file {_f}...")
                    
                    # Load buffers
                    _b1 = _f.replace('.txt', f'.{translator.target}.tmp.txt')
                    _b2 = _f.replace('.txt', f'.{translator.source}.tmp.txt')
                    
                    translated_sentences = utils.read_txt(_b1)
                    _translated_sentences = utils.read_txt(_b2)
                    
                    # Load sentences
                    _i = 0
                    i = len(translated_sentences) - 1
                    with open(_f) as f:
                        _lines = tqdm(f.readlines(), position=0)
                        for sentence in _lines:
                            # Translate sentence
                            sentence = sentence.strip().replace("\n", "")
                            
                            # If not already translated
                            if sentence not in _translated_sentences:
                                _translated_sentences.append(sentence)
                                # If buffer is too big save it
                                if _i >= 100 and args.save:
                                    _lines.set_description("Saving buffer...")
                                    utils.save_txt(_translated_sentences, _b2)
                                    utils.save_txt(translated_sentences, _b1)
                                    _i = 0

                                # Translate sentence
                                _lines.set_description(f"Translating \"{sentence}\"...")
                                translation = translate_sentence(sentence, translator)
                                _lines.set_description(f"Translated as \"{translation}\".")
                                
                                # Save translation if not already
                                if translation not in translated_sentences:
                                    translated_sentences.append(translation)
                                _i += 1
                    
                    if Path(_b).exists():
                        os.remove(_b1)
                        os.remove(_b2)
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
            utils.save_txt(_translated_sentences, _b2)
            utils.save_txt(translated_sentences, _b1)
            print("Done.")
            print("You're welcome.")
            print("Quitting now.")
            sys.exit(1)
    else:
        translation = translate_sentence(" ".join(args.sentence), translator)
        print(translation)
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