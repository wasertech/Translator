import sys

from argparse import ArgumentParser
from translator import Translator, LANGS, __version__

def parse_arguments():
    argument_parse = ArgumentParser(description="Translate from one language to another.")
    argument_parse.add_argument('-v', '--version', action='store_true', help="shows the current version of translator")
    argument_parse.add_argument('sentence', nargs="*", help="Something to translate.")
    argument_parse.add_argument('-s', '--source', default="eng_Latn", help="Source language to translate.")
    argument_parse.add_argument('-t', '--target', default="fra_Latn", help="Target language to translate.")
    argument_parse.add_argument('-l', '--max_length', default=500, help="Max length of output.")
    argument_parse.add_argument('-m', '--model_id', default="facebook/nllb-200-distilled-600M", help="HuggingFace model ID to use.")
    argument_parse.add_argument('-p', '--pipeline', default="translation", help="Pipeline task to use.")
    argument_parse.add_argument('-L', '--language_list', action='store_true', help="Show list of languages.")


    return argument_parse.parse_args()

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
    print(translator.translate(args.sentence))

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)