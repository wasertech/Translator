import os, sys, psutil, time
import locale
import datetime

from multiprocessing import Queue, Process
from threading import Thread
from pathlib import Path
from argparse import ArgumentParser
from datasets import load_dataset, Dataset
from halo import Halo
from translator import Translator, utils, __version__
from translator.language import get_nllb_lang, get_sys_lang_format

locale.setlocale(locale.LC_ALL, '')

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
    argument_parse.add_argument('-n', '--nproc', default=4, type=int, help="Number of process to spawn for filtering untraslated sentences.")
    argument_parse.add_argument('-L', '--language_list', action='store_true', help="Show list of languages.")
    

    return argument_parse.parse_args()

def translate_sentence(sentence, translator):
    return translator.translate(sentence)

def main():
    args = parse_arguments()

    spinner = Halo(spinner="dots12")

    if args.language_list:
        print("Language list:")
        for l in get_nllb_lang():
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
        if _lang not in get_nllb_lang() and args.model_id == "facebook/nllb-200-distilled-600M":
            print(f"Warning! {_lang=} is not in listed as supported by the current model.")
            print("There is a high probability translation operations will fail.")
            print("Type translate --language_list to get the full list of supported languages.")
            print("Or type translate --help to get help.")
            _nllb_lang = get_nllb_lang(_lang)
            print(f"Using {_nllb_lang} instead of {_lang}.")


    spinner.info("Preparing to translate...")
    spinner.start()
    spinner.text = "Please be patient."

    translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline)

    translations = []
    _translated = []

    spinner.text = ""
    spinner.stop()

    if args.directory and Path(args.directory).exists():
        spinner.info("No sentence was given but directory was provided.")
        spinner.info(f"Using {translator.device} to translate sentences in {args._from} to {args._to} from text files in directory \'{args.directory}\' by batches of size {args.batch_size}.")
        source_path = args.directory
        output_path = args.save
        batch_size = args.batch_size
        n_proc = args.nproc
        
        cache = f"{output_path.replace('.txt', f'.{_from}.{_to}.tmp.cache')}"
        translated_input_path = f"{cache}/{os.path.basename(output_path)}.{_from}.txt"

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
            if _l == 0:
                spinner.info("No files to translate.")
                sys.exit(1)
            spinner.info(f"Found {_l} text file{'s' if _l > 1 else ''}.")
            spinner.stop()
            mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            dataset = load_dataset('text', data_files={'translate': txt_files}, streaming=False, split="translate", cache_dir=cache)
            mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            spinner.info(f"RAM memory used by dataset: {(mem_after - mem_before):n} MB")
            _ds = dataset.dataset_size
            spinner.info(f"Translating {_ds:n} sentences...")
            spinner.start()
            
            # Load already translated data if any
            time_before_1 = time.perf_counter()
            spinner.info("Loading translated sentences...")
            spinner.stop()
            if Path(translated_input_path).exists() and Path(translated_input_path).is_file():
                translated_dataset = load_dataset('text', data_files={'translated': [translated_input_path]}, streaming=False, split="translated", cache_dir=cache)
                _translated = translated_dataset['text']
                spinner.info(f"Translated {len(_translated):n} sentences already.")
                spinner.start()
            else:
                spinner.info("Not translated any sentences yet.")
                spinner.start()
            time_after_1 = time.perf_counter()
            _td_1 = time_after_1 - time_before_1
            spinner.info(f"Took {_td_1} second(s) to load {len(_translated):n} translated sentence(s).")
            spinner.start()

            # Filter translated data from all data to get untranslated data
            time_before_2 = time.perf_counter()
            spinner.stop()
            if not _translated:
                untranslated_dataset = dataset
            else:
                spinner.info("Filtering untranslated sentences...")
                #spinner.start()
                #spinner.text = "Please wait..."
                untranslated_dataset = dataset.filter(lambda x: {'text': x['text'] if x['text'] not in _translated else ""}, num_proc=n_proc, batched=True)
                spinner.text = ""
            time_after_2 = time.perf_counter()
            _td_2 = time_after_2 - time_before_2
            _ut_ds = _ds - len(_translated)
            spinner.info(f"Took {_td_2} second(s) to compute {_ut_ds:n} untranslated sentence(s).")
            spinner.start()
            
            # Translate untranslated data
            time_before_3 = time.perf_counter()
            spinner.info("Translating untranslated sentences...")
            spinner.start()
            spinner.text = f"Processing first batch of {batch_size} sentences ({_ut_ds:n} total)... please wait for statistics."
            _i, _t = 0, 0
            
            for batch in untranslated_dataset.iter(batch_size):
                _t = time.perf_counter()
                _batch_text =  batch['text']
                _translated += _batch_text
                translations += translate_sentence(_batch_text, translator)
                time_meanwhile = time.perf_counter()
                _td = time_meanwhile - _t
                _td2 = time_meanwhile - time_before_3
                _i += batch_size
                _avg1 = batch_size/_td
                _avg2 = _i/_td2
                _avg = (_avg1 + _avg2)/2
                _eta = (_ut_ds - _i) / _avg
                spinner.text = f"[{_i:n}/{_ut_ds:n} ({_i/_ut_ds:.2%}) | ~{_avg:.2f} sentences / second | ETA : {datetime.timedelta(seconds=_eta)}]"
            
            time_after_3 = time.perf_counter()
            _td_3 = time_after_3 - time_before_3
            spinner.text = ""
            spinner.info("Translation completed.")
            spinner.info(f"Took {_td_3:.1f} second(s) to translate {_ut_ds:n} sentences.")

            # Report translation
            time_after = time.perf_counter()
            _td = time_after - time_before
            spinner.info(f"All files in {args.directory} have been translated from {_from} to {_to}.")
            spinner.info(f"Took {_td:.1f} second(s) to translate over {_ut_ds >> 30} GB (~ {float(_ut_ds >> 27)/_td:.1f} Gb/s).")
            
            if Path(cache).exists(): os.rmdir(cache)

        except UserWarning:
            pass
        except KeyboardInterrupt as e:
            spinner.warn("You are about to loose your progress!")
            if args.save and translations and _translated:
                with Path(translated_input_path) as p:
                    if not p.parent.exists():
                        p.parent.mkdir(parents=True, exist_ok=True)
                    utils.save_txt(_translated, p)
                utils.save_txt(translations, Path(output_path))            
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