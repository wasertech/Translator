import os, sys, psutil, time
import locale
import shutil
import torch

from multiprocess import set_start_method
from datetime import timedelta
from pathlib import Path
from argparse import ArgumentParser
from datasets import load_dataset, Dataset
from halo import Halo
from translator import Translator, utils, __version__
from translator.language import get_nllb_lang, get_sys_lang_format

locale.setlocale(locale.LC_ALL, '')

try:
    set_start_method("spawn")
except RuntimeError:
    pass

def parse_arguments():
    argument_parse = ArgumentParser(description="Translate [FROM one language] [TO another], [any SENTENCE you would like].")
    argument_parse.add_argument('-v', '--version', action='store_true', help="shows the current version of translator")
    argument_parse.add_argument('_from', nargs='?', default=[], help="Source language to translate from.")
    argument_parse.add_argument('_to', nargs='?', default=[], help="Target language to translate towards.")
    argument_parse.add_argument('sentences', nargs="*", default=[], help="Sentences to translate.")
    argument_parse.add_argument('-d', '--directory', type=str, help="Path to directory to translate in batch instead of unique sentence.")
    argument_parse.add_argument('-S', '--save', type=str, help="Path to text file to save translations.")
    argument_parse.add_argument('-l', '--max_length', default=500, help="Max length of output.")
    argument_parse.add_argument('-m', '--model_id', default="facebook/nllb-200-distilled-600M", help="HuggingFace model ID to use.")
    argument_parse.add_argument('-p', '--pipeline', default="translation", help="Pipeline task to use.")
    argument_parse.add_argument('-b', '--batch_size', default=128, type=int, help="Number of sentences to batch for translation.")
    argument_parse.add_argument('-n', '--nproc', default=4, type=int, help="Number of process to spawn for filtering untraslated sentences.")
    argument_parse.add_argument('-e', '--nepoch', default=1, type=int, help="Number of epoch(s) to translate batched sentences.")
    argument_parse.add_argument('-L', '--language_list', action='store_true', help="Show list of languages.")
    

    return argument_parse.parse_args()

def translate_sentence(sentence, translator):
    return translator.translate(sentence) or []

def main():
    args = parse_arguments()

    spinner = Halo(spinner="dots12")

    if args.version:
        _version = "Translator version:"
        _lang = "eng_Latn"

        _to = args._to or get_sys_lang_format()

        if _to == _lang:
            spinner.info(f"{_version} {__version__}")
        else:
            spinner.start()
            translator = Translator(_lang, _to, args.max_length, args.model_id, args.pipeline)
            version = translate_sentence(_version, translator)
            spinner.stop()
            spinner.info(f"{version[0]} {__version__}")
        sys.exit(0)

    if args.language_list:
        spinner.info("Language list:")
        if args.model_id == "facebook/nllb-200-distilled-600M":
            for l in get_nllb_lang(): print(f"- {l}")
        else:
            raise NotImplementedError(f"{model_id=} language list not implemented.")
        print()
        sys.exit(0)

    _from, _to, _sentences = "".join(args._from), "".join(args._to), args.sentences

    if _from and _to and not _sentences:
        if _to not in get_nllb_lang() and _to == get_nllb_lang(_to):
            _sentences = [args._to]
            _to = get_sys_lang_format()
            spinner.info(f"Target language was not provided. Translating to \'{_to}\'.")
        elif not args.directory:
            spinner.fail(f"Missing sentences to translate.")
            sys.exit(1)
    
    if not _to and _from:
        if not args.directory:
            spinner.fail(f"Missing \'_to\' argument.")
            print("Please choose a target language or at least give a sentence or a directory to translate.")
            print("Type \'translate --help\' to get help.")
            sys.exit(1)
        else:
            _to = get_sys_lang_format()
            spinner.info(f"Target language was not provided. Translating to \'{_to}\'.")
    
    if not _from:
        spinner.fail(f"Missing \'_from\' argument.")
        print("Please provide at least a source language.")
        sys.exit(1)

    for _lang in [_from, _to]:
        if _lang not in get_nllb_lang() and args.model_id == "facebook/nllb-200-distilled-600M":
            spinner.warn(f"Warning! {_lang} is not listed as supported language by the current model {args.model_id}.")
            print("There is a high probability translation will fail.")
            print("Type translate --language_list to get the full list of supported languages.")
            print("Or type \'translate --help\' to get help.")
            _nllb_lang = get_nllb_lang(_lang)
            if _lang == _from:
                _from = _nllb_lang
            elif _lang == _to:
                _to = _nllb_lang
            spinner.info(f"Using {_nllb_lang} instead of {_lang}.")
    
    if _from == _to:
        spinner.warn(f"Warning! {_from=} == {_to=} ")
        print("Translating to the same language is computationally wasteful for no valid reason.")
        spinner.info("Using Hitchens's razor to shortcut translation.")
        if not args.directory:
            if not args.save:
                for sentence in _sentences: print(sentence)
            else:
                # if not Path(args.save).exists():
                utils.save_txt(_sentences, Path(args.save))
                # else:
                #     print(f"{args.save} exists already.")
                #     print("Please mind the following fact:")
                #     print("Translated sentences will be added at the end of the file.")
                #     utils.save_txt(_sentences, Path(args.save), append=True)
        else:
            txt_files = list(set(utils.glob_files_from_dir(args.directory, suffix=".txt")) - set([args.save, f"{args.directory}/{args.save}"]) - set(utils.glob_files_from_dir(f"{args.save.replace('.txt', f'.{_from}.{_to}.tmp.cache')}", suffix="*")))
            if not txt_files:
                spinner.fail(f"No files to translate in \'{args.directory}\'.")
                sys.exit(1)
            if args.save:
                with open(args.save, 'w') as outfile:
                    for fname in txt_files:
                        with open(fname) as infile:
                            for line in infile:
                                outfile.write(line)
            else:
                for fname in txt_files:
                    with open(fname) as infile: print(infile.read())
        sys.exit(0)

    spinner.info("Preparing to translate...")
    spinner.start()
    spinner.text = "Please be patient."

    translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline, batch_size=args.batch_size, n_proc=args.nproc)

    translations = []
    _translated = []

    spinner.text = ""
    spinner.stop()

    if args.directory and Path(args.directory).exists():
        spinner.info("No sentence was given but directory was provided.")
        spinner.info(f"Translate sentences in {args._from} to {args._to} from text files in directory \'{args.directory}\' by batches of size {args.batch_size}.")
        source_path = args.directory
        if not args.save:
            spinner.fail("Translating sentences from directory without passing --save argument is forbbiden.")
            print("Please choose where to store the translation as text file.")
            print("Type \'!! --save translations.txt\' to append the --save flag to your last command.")
            sys.exit(1)
        output_path = args.save
        batch_size = args.batch_size
        n_proc, n_epoch = args.nproc, args.nepoch
        
        cache = f"{output_path.replace('.txt', f'.{_from}.{_to}.tmp.cache')}"
        translated_input_path = f"{cache}/{os.path.basename(output_path)}.{_from}.txt"

        try:
            # Load Data
            spinner.start()
            spinner.text = "Loading datasets..."
            translate_data_files = {'translate': [],}
            translated_data_files = {'translated': [translated_input_path],}
            translation_data_files = {'translation': [output_path],}

            # Load all data to translate
            time_before = time.perf_counter()
            spinner.info("Loading all sentences...")
            spinner.text = ""
            spinner.start()
            txt_files = list(set(utils.glob_files_from_dir(source_path, suffix=".txt")) - set([output_path, f"{source_path}/{output_path}"]) - set(utils.glob_files_from_dir(cache, suffix="*")))
            _l = len(txt_files)
            if _l == 0:
                spinner.fail(f"No files to translate in \'{source_path}\'.")
                sys.exit(1)
            spinner.info(f"Found {_l} text file{'s' if _l > 1 else ''}.")
            spinner.stop()
            
            for t in txt_files: translate_data_files['translate'].append(t)
            
            mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            translate_dataset = load_dataset('text', data_files=translate_data_files, split="translate", cache_dir=cache)
            mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            spinner.info(f"RAM memory used by translate dataset: {(mem_after - mem_before):n} MB")
            _ds = translate_dataset.dataset_size
            spinner.info(f"Translating {_ds:n} sentences...")
            spinner.start()
            
            # Load already translated data if any
            time_before_1 = time.perf_counter()
            spinner.info("Loading translated sentences...")
            spinner.stop()
            if Path(translated_input_path).exists() and Path(translated_input_path).is_file() and Path(output_path).exists() and Path(output_path).is_file():
                mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                translated_dataset = load_dataset('text', data_files=translated_data_files, split="translated", cache_dir=cache)
                mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                spinner.info(f"RAM memory used by translated dataset: {(mem_after - mem_before):n} MB")
                _translated += translated_dataset['text']
                spinner.info(f"Translated {len(_translated):n} sentences already.")
                
                mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                translation_dataset = load_dataset('text', data_files=translation_data_files, split="translation", cache_dir=cache)
                mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                spinner.info(f"RAM memory used by translation dataset: {(mem_after - mem_before):n} MB")
                translations += translation_dataset['text']
                
                spinner.start()
            else:
                spinner.info("Not translated any sentences yet.")
                spinner.start()
            time_after_1 = time.perf_counter()
            _td_1 = time_after_1 - time_before_1
            spinner.info(f"Took {timedelta(seconds=_td_1)} second(s) to load {len(_translated):n} translated sentence(s).")
            spinner.start()

            # Filter translated data from all data to get untranslated data
            time_before_2 = time.perf_counter()
            spinner.stop()
            mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            if not _translated:
                untranslated_dataset = translate_dataset
            else:
                spinner.info("Filtering untranslated sentences...")
                #spinner.start()
                #spinner.text = "Please wait..."
                untranslated_dataset = translate_dataset.filter(lambda x: {'text': x['text'] if x['text'] not in _translated else ""}, num_proc=n_proc, batched=True, batch_size=batch_size)
                spinner.text = ""
            mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            spinner.info(f"RAM memory used by untranslated dataset: {(mem_after - mem_before):n} MB")
            time_after_2 = time.perf_counter()
            _td_2 = time_after_2 - time_before_2
            _ut_ds = untranslated_dataset.dataset_size # _ds - len(_translated)
            spinner.info(f"Took {timedelta(seconds=_td_2)} second(s) to compute {_ut_ds:n} untranslated sentence(s).")
            spinner.start()
            
            # Translate untranslated data
            time_before_3 = time.perf_counter()
            spinner.info("Translating untranslated sentences...")
            
            # def _translate_sentence(example):
            #     # os.environ["CUDA_VISIBLE_DEVICES"] = str(rank or 0 % torch.cuda.device_count())
            #     e = example['text']
            #     # _translated += e
            #     t = translate_sentence(e, translator)
            #     # translations += t
            #     return {'text': t}

            # translation_dataset = untranslated_dataset.map(_translate_sentence, num_proc=n_proc, batched=True, batch_size=batch_size, cache_file_name=f"{translated_input_path}")
            
            i, _i, _t = 0, 0, 0
            epoch_split = int(_ut_ds / n_epoch)
            spinner.info(f"Epoch size: {epoch_split:n}")
            spinner.start()
            spinner.text = f"Processing first epoch of {epoch_split:n} sentences by batch of {batch_size:n} ({_ut_ds:n} ({n_epoch:n} epochs) total)..."
            
            
            for epoch in untranslated_dataset.iter(epoch_split):
                _t = time.perf_counter()
                _epoch_text =  epoch['text']
                _translated += _epoch_text
                translations += translate_sentence(_epoch_text, translator)
                time_meanwhile = time.perf_counter()
                _td = time_meanwhile - _t
                _td2 = time_meanwhile - time_before_3
                i += 1
                _i += epoch_split
                _avg1 = epoch_split/_td
                _avg2 = _i/_td2
                _avg = (_avg1 + _avg2)/2
                _etr = (_ut_ds - _i) / _avg
                spinner.text = f"Epoch {i:n}/{n_epoch:n} | {_i:n}/{_ut_ds:n} ({_i/_ut_ds:.2%}) | ~{_avg:.2f} translation(s) / second | ETR: {timedelta(seconds=_etr)} | dT: {timedelta(seconds=_td)}"
            
            time_after_3 = time.perf_counter()
            _td_3 = time_after_3 - time_before_3
            spinner.text = ""
            spinner.succeed("Translation completed.")
            spinner.info(f"Took {timedelta(seconds=_td_3)} second(s) to translate {_ut_ds:n} sentences.")

            # Report translation
            time_after = time.perf_counter()
            _td = time_after - time_before
            spinner.succeed(f"All files in {source_path} have been translated from {_from} to {_to}.")
            _sgb = _ut_ds >> 30
            if _sgb > 0:
                spinner.info(f"Took {timedelta(seconds=_td)} second(s) to translate over {_sgb} GB (~ {float(_ut_ds >> 27)/_td:.1f} Gb/s).")
            else:
                spinner.info(f"Took {timedelta(seconds=_td)} second(s) to translate less than 1 GB.")

            if Path(cache).exists(): shutil.rmtree(cache)

        except UserWarning:
            pass
        except RuntimeError as re:
            spinner.warn("You are about to loose your progress!")
            if args.save and translations and _translated:
                with Path(translated_input_path) as p:
                    if not p.parent.exists():
                        p.parent.mkdir(parents=True, exist_ok=True)
                    if p.exists(): os.remove(p)
                    utils.save_txt(_translated, p)
                with Path(output_path) as _p:
                    if _p.exists():
                        os.remove(_p)
                    utils.save_txt(translations, _p)         
                spinner.succeed(f"Partial translation has been saved under {output_path}.")
            raise re
        except KeyboardInterrupt as e:
            spinner.warn("You are about to loose your progress!")
            if args.save and translations and _translated:
                with Path(translated_input_path) as p:
                    if not p.parent.exists():
                        p.parent.mkdir(parents=True, exist_ok=True)
                    if p.exists(): os.remove(p)
                    utils.save_txt(_translated, p)
                with Path(output_path) as _p:
                    if _p.exists(): os.remove(_p)
                    utils.save_txt(translations, _p)
                spinner.succeed(f"Partial translation has been saved under {output_path}.")
            sys.exit(1)
    else:
        translation = translate_sentence(_sentences, translator)
        for t in translation: print(t)
        translations.append(translation)
    
    if args.save:
        with Path(args.save) as p:
            if not p.exists():
                utils.save_txt(translations, p)
            else:
                spinner.warn(f"{args.save} exists already.")
                spinner.info("Translated sentences will be overwritten.")
                if p.exists(): os.remove(p)
                utils.save_txt(translations, p)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except NotImplementedError as e:
        print(str(e))
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(1)
