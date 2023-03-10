import os, sys, psutil, time

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
    argument_parse.add_argument('sentences', nargs="*", default=["Translator version:"], help="Sentences to translate.")
    argument_parse.add_argument('-d', '--directory', type=str, help="Path to directory to translate in batch instead of unique sentence.")
    argument_parse.add_argument('-S', '--save', type=str, help="Path to text file to save translations.")
    argument_parse.add_argument('-l', '--max_length', default=500, help="Max length of output.")
    argument_parse.add_argument('-m', '--model_id', default="facebook/nllb-200-distilled-600M", help="HuggingFace model ID to use.")
    argument_parse.add_argument('-p', '--pipeline', default="translation", help="Pipeline task to use.")
    argument_parse.add_argument('-b', '--batch_size', default=128, type=int, help="Number of sentences to batch for translation.")
    argument_parse.add_argument('-L', '--language_list', action='store_true', help="Show list of languages.")
    

    return argument_parse.parse_args()

def translate_sentence(sentence, translator):
    return translator.translate(sentence)

def main():
    args = parse_arguments()

    spinner = Halo(spinner="dots12")

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


    spinner.info("Preparing to translate...")
    spinner.start()
    spinner.text = "Please be patient."

    translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline)

    translations = []

    spinner.text = ""
    spinner.stop()

    if args.directory and Path(args.directory).exists():
        spinner.info("No sentence was given but directory was provided.")
        spinner.info(f"Using {translator.device} to translate sentences in {args._from} to {args._to} from text files in directory \'{args.directory}\' by batches of size {args.batch_size}.")
        source_path = args.directory
        output_path = args.save
        batch_size = args.batch_size
        
        cache = f"{output_path.replace('.txt', f'.{_from}.{_to}.tmp.cache')}"

        try:
            # Load Data
            spinner.start()
            spinner.text = "Loading datasets..."
            
            # Load all data to translate
            time_before = time.perf_counter()
            spinner.info("Loading all sentences...")
            spinner.text = ""
            spinner.start()
            txt_files = list(set(utils.glob_files_from_dir(source_path, suffix=".txt")) - set([output_path, f"{source_path}/{output_path}"]) - set(utils.glob_files_from_dir(cache, suffix="*")))
            _l = len(txt_files)
            spinner.info(f"Found {_l} text file{'s' if _l > 1 else ''}.")
            spinner.stop()
            mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            dataset = load_dataset('text', data_files={'translate': txt_files}, streaming=False, split="translate", cache_dir=cache)
            mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            spinner.info(f"RAM memory used by dataset: {(mem_after - mem_before)} MB")
            _ds = dataset.dataset_size
            spinner.info(f"Translating {_ds:n} sentences...")
            spinner.start()
            
            # Load already translated data if any
            time_before_1 = time.perf_counter()
            spinner.info("Loading translated sentences...")
            spinner.stop()
            if Path(output_path).exists() and Path(output_path).is_file():
                translated_dataset = load_dataset('text', data_files={'translated': [output_path]}, streaming=False, split="translated", cache_dir=cache)
                translations = translated_dataset['text']
                spinner.info(f"Translated {len(translations)} sentences already.")
                spinner.start()
            else:
                spinner.info("Not translated any sentences yet.")
                spinner.start()
            time_after_1 = time.perf_counter()
            _td_1 = time_after_1 - time_before_1
            spinner.info(f"Took {_td_1} second(s) to load translated sentences.")
            spinner.start()

            # Filter translated data from all data to get untranslated data
            time_before_2 = time.perf_counter()
            spinner.info("Loading translated sentences...")
            spinner.stop()
            if not translations:
                untranslated_dataset = dataset
            else:
                spinner.info("Filtering untranslated sentences...")
                untranslated_dataset = dataset.filter(lambda example: example not in translations)
            time_after_2 = time.perf_counter()
            _td_2 = time_after_2 - time_before_2
            spinner.info(f"Took {_td_2} second(s) to compute untranslated sentences.")
            spinner.start()

            _ut_ds = untranslated_dataset.dataset_size
            
            # Translate untranslated data
            time_before_3 = time.perf_counter()
            spinner.info("Translating untranslated sentences...")
            spinner.start()
            spinner.text = f"[0/{_ut_ds} (0%) | 0 sentences / second"
            _i = 0
            for batch in untranslated_dataset.iter(batch_size):
                translations += translate_sentence(batch['text'], translator)
                time_meanwhile = time.perf_counter()
                _td = time_meanwhile - time_before
                _i += batch_size
                spinner.text = f"[{_i}/{_ut_ds} ({_i/_ut_ds:.2%}) | ~{_i/_td:.2f} sentences / second]"
            time_after_3 = time.perf_counter()
            _td_3 = time_after_3 - time_before_3
            spinner.text = ""
            spinner.info("Translation completed.")
            spinner.info(f"Took {_td_3} second(s) to translate untranslated sentences.")

            # Report translation            
            time_after = time.perf_counter()
            _td = time_after - time_before
            spinner.info(f"All files in {args.directory} have been translated from {args.source} to {args.target}.")
            spinner.info(f"Took {_td:.1f} second(s) to translate over {_ut_ds >> 30} GB (~ {float(_ut_ds >> 27)/_td:.1f} Gb/s).")
            
            if Path(cache).exists(): os.rmdir(cache)

        except UserWarning:
            pass
        except KeyboardInterrupt as e:
            spinner.warn("You are about to loose your progress!")
            if args.save and translations:
                utils.save_txt(translations, Path(args.save))                
                spinner.info("Partial translation has been saved.")
            sys.exit(1)
    else:
        translation = translate_sentence(args.sentences, translator)
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