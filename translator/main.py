import sys

from glob import glob
from pathlib import Path
from argparse import ArgumentParser
from translator import Translator, LANGS, __version__

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

def save_txt(translations, file_path):
    with open(file_path, 'w') as f:
        f.write("\n".join(translations))

def read_txt(filepath):
    with open(filepath, 'r') as f:
        return f.read().split("\n")

def read_txt_files(directory):
    r = []
    for f in glob(f"{directory}/*.txt"):
        for l in read_txt(f):
            r.append(l)
    return r

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

    translator = Translator(args.source, args.target, args.max_length, args.model_id, args.pipeline)

    translations = []

    if not args.sentence and Path(args.directory).exists():
        print("No sentence was given but directory was.")
        print(f"Loading batch of sentences from {args.directory}")
        sentences = read_txt_files(args.directory)
        for s in sentences:
            print(f"sentence={s}")
            translation = translator.translate(s)
            print(f"{translation=}")
            translations.append(translation)
    else:
        translation = translator.translate(args.sentence)
        print(translation)
        translations.append(translation)
    
    if args.save:
        if not Path(args.save).exists():
            save_txt(translations, Path(args.save))
        else:
            print(f"{args.save} exists already. Please specify another path or remove {args.save}.") 

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)