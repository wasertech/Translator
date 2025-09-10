import os, sys, psutil, time
import locale
import shutil
import torch
import logging
import questionary

from multiprocess import set_start_method
from datetime import timedelta
from pathlib import Path
from argparse import ArgumentParser
from datasets import load_dataset, Dataset
from halo import Halo
import pyarrow as pa
import pyarrow.compute as compute
from translator import Translator, utils, __version__
from translator.language import get_nllb_lang, get_sys_lang_format

logging.getLogger('transformers.pipelines.base').setLevel(logging.ERROR)
logger = logging.Logger(__file__)
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    # Ignore locale errors in minimal environments (e.g., Makefiles, containers)
    # Core functionality doesn't depend on locale setting
    pass

try:
    set_start_method("spawn")
except RuntimeError:
    pass

default_translator_model = "facebook/nllb-200-distilled-600M"
default_translator_pipeline = "translation"
max_translation_lenght = 500

please_wait_disclamer = """
[Loading...] If this is the first time you load a particular model, it may take a while depending on your hardware, your internet connection and the model size.
"""
please_wait_short = "Please be patient."

def parse_arguments():
    argument_parse = ArgumentParser(description="Translate [FROM one language] [TO another], [any SENTENCE you would like].")
    argument_parse.add_argument('-v', '--version', action='store_true', help="shows the current version of translator")
    argument_parse.add_argument('_from', nargs='?', default=[], help="Source language to translate from.")
    argument_parse.add_argument('_to', nargs='?', default=[], help="Target language to translate towards.")
    argument_parse.add_argument('sentences', nargs="*", default=[], help="Sentences to translate.")
    argument_parse.add_argument('-d', '--directory', type=str, help="Path to directory to translate in batch instead of unique sentence.")
    argument_parse.add_argument('--po', action='store_true', help="Translate PO (Portable Object) files instead of text files.")
    argument_parse.add_argument('--force', action='store_true', help="Force translation ignoring cache (text files) or translate all entries including translated ones (PO files).")
    argument_parse.add_argument('-S', '--save', type=str, help="Path to text file to save translations.")
    argument_parse.add_argument('-l', '--max_length', default=max_translation_lenght, type=int, help="Max length of output.")
    argument_parse.add_argument('-m', '--model_id', default=default_translator_model, help="HuggingFace model ID to use.")
    argument_parse.add_argument('-p', '--pipeline', default=default_translator_pipeline, help="Pipeline task to use.")
    argument_parse.add_argument('-b', '--batch_size', default=128, type=int, help="Number of sentences to batch for translation.")
    argument_parse.add_argument('-n', '--nproc', default=4, type=int, help="Number of process(es) to spawn for batch translation.")
    argument_parse.add_argument('-e', '--nepoch', default=1, type=int, help="Number of epoch(s) to translate batched sentences.")
    argument_parse.add_argument('-L', '--language_list', action='store_true', help="Show list of languages.")
    argument_parse.add_argument('-vv', "--debug", action='store_true', help="Show debug info")
    argument_parse.add_argument('-i', "--interactive", action='store_false', help="Deactivate interactiveness.")
    
    return argument_parse.parse_args(), argument_parse

def translate_sentence(sentence, translator):
    return translator.translate(sentence) or []

def _log(msg, logger=None, spinner=None, _type="info"):
    if not msg:
        return
    elif spinner and msg:
        if _type == 'warning':
            spinner.warn(msg)
        elif _type == 'error':
            spinner.fail(msg)
        elif _type == 'success':
            spinner.succeed(msg)
        else:
            spinner.info(msg)
    elif logger and msg:
        if _type == 'warn':
            logger.warn(msg)
        elif _type == 'error':
            logger.error(msg)
        elif _type in ['success', 'info']:
            logger.info(msg)
        else:
            logger.debug(msg)
    elif msg:
        print(msg)
    return msg

def print_version(version, prefix="Translator version:", _from="eng_Latn", _to=get_sys_lang_format(), is_interactive=False, spinner=None, logger=None, max_length=max_translation_lenght, model_id=default_translator_model, pipeline=default_translator_pipeline, batch_size=1, nproc=1):
    v = None

    if _to == _from:
        v = f"{prefix} {version}"
    else:
        try:
            _log("Preparing to translate...", logger, spinner, 'info')
                
            if is_interactive and spinner:
                _log(please_wait_disclamer, logger, spinner, 'info')
                spinner.start()
                spinner.text = please_wait_short

            translator = Translator(_from, _to, max_length, model_id, pipeline, batch_size=batch_size, n_proc=nproc)
            
            if is_interactive and spinner:
                spinner.text = ""
                spinner.stop()
            
            translated_version = translate_sentence(prefix, translator)
            if not translated_version:
                e = "Sorry could not translate version number.\nHere is the English version of Translator anyway:"
                _log(e, logger, spinner, 'warning')
                v = f"{prefix} {version}"
            else:
                v = f"{translated_version[0]} {version}"
        except RuntimeError as re:
            e = f"Sorry could not translate version number due to to the following runtime error:\n{str(re)}\nHere is the English version of Translator anyway:"
            _log(e, logger, spinner, 'error')
            v = f"{prefix} {version}"
    if v: return _log(v, logger, spinner, "info")
    return

def main():
    args, parser = parse_arguments()

    is_interactive = args.interactive

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('translator.translate').setLevel(logging.DEBUG)
    
    if is_interactive:
        spinner = Halo(spinner="dots12")
    else:
        spinner = None

    fetch_help = [
        "help",
        "h",
        "aide",
        "hilfe",
    ]
    
    # --help is handled by the argument parser
    if args._from in fetch_help: # we handle just help so we can drop --
        parser.print_help()
        sys.exit(0)

    fetch_version = [
        "version",
        "-version",
        "--v",
        "ver",
        "verzion",
        "--V",
        "VERSION",
        "V",
        "v",
    ]

    if args.version or args._from in fetch_version:
        print_version(__version__, _to="".join(args._to) or get_sys_lang_format(), is_interactive=is_interactive, spinner=spinner, logger=logger, max_length=args.max_length, model_id=args.model_id, pipeline=args.pipeline, batch_size=args.batch_size)
        sys.exit(0)

    fetch_languages = [
        "list",
        "language",
        "languages_list",
        "language_list",
        "languages",
        "LANG",
        "LANGUAGE",
        "LANGUAGES",
        "LANGUAGES_LIST",
        "LANGUAGE_LIST",
        "langues",
        "langue",
        "LANGUE",
        "LANGUES",
        "LIST",
    ]

    if args.language_list or args._from in fetch_languages:
        _log("Language list:", logger, spinner, 'info')
        if args.model_id == "facebook/nllb-200-distilled-600M":
            for l in get_nllb_lang(): print(f"- {l}")
        else:
            raise NotImplementedError(f"{args.model_id=} language list not implemented.")
        print()
        sys.exit(0)

    _from, _to, _sentences = "".join(args._from), "".join(args._to), args.sentences
    _directory, _save_path, _po_mode, _force = args.directory, args.save, args.po, args.force

    # Validate conflicting flags
    if _po_mode and _save_path:
        _log("Error: --po and --save flags cannot be used together. PO files are translated in-place.", logger, spinner, 'error')
        sys.exit(1)
    
    if _po_mode and not _directory:
        _log("Error: --po flag requires --directory to be specified.", logger, spinner, 'error')
        sys.exit(1)

    # Handle PO mode - determine source and target languages
    if _po_mode:
        if not _from and not _to:
            # Multi-language mode: translate all available target languages
            _from = "eng_Latn"  # Default source language
            _log(f"PO mode: Multi-language translation enabled. Source: {_from}, detecting all target languages.", logger, spinner, 'info')
        elif _to and not _from:
            # Single target language mode with default source
            _from = "eng_Latn"  # Default source language for PO translation
            _log(f"PO mode: Defaulting source language to {_from}", logger, spinner, 'info')
    
    # Normalize language codes (allow short codes like 'fr' to be converted to 'fra_Latn')
    if _po_mode:
        if _from:
            _from = utils.normalize_language_code(_from)
        if _to:
            _to = utils.normalize_language_code(_to)

    nepoch, nproc, batch_size = args.nepoch, args.nproc, args.batch_size

    if not _from and not _to and not _sentences and not _directory and is_interactive:
        _log("Welcome!", logger, spinner, 'info')
        print_version(__version__, prefix="I am Translator version:", _to="".join(args._to) or 'eng_Latn', is_interactive=is_interactive, spinner=spinner, logger=logger, max_length=args.max_length, model_id=args.model_id, pipeline=args.pipeline, batch_size=args.batch_size, nproc=args.nproc)
        _log("At your service.", logger, spinner, 'info')

        options = ["Manually typed sentences", "Stored sentences in file(s)", "Nothing, just exit"]

        options_map = {}
        for i, o in enumerate(options): options_map[o] = i

        # Prompt sentences input method
        translate_from = questionary.select(
            "What would you like to translate?",
            choices=options,
            use_shortcuts=True,
            use_arrow_keys=True,
        ).ask()
        if not translate_from:
            _log("Exiting.", logger, spinner, 'info')
            sys.exit(1)
        
        translate_from_choice, translate_from_name = options_map[translate_from], translate_from
        if translate_from_choice == 2:
            _log("Just exiting.", logger, spinner, 'info')
            sys.exit(0)
        
        _log(f"Translating from: {translate_from_name}", logger, spinner, 'info')
        
        # Prompt source language
        source_language = questionary.text("What language to translate from?").ask()
        if not source_language:
            _log("Exiting.", logger, spinner, 'info')
            sys.exit(1)
        
        _from = get_nllb_lang(source_language)
        _log(f"Translating from {_from}.", logger, spinner, 'info')
        
        # Prompt target language
        target_language = questionary.text("What language to translate to?", default=get_sys_lang_format()).ask()
        if not target_language:
            _log("Exiting.", logger, spinner, 'info')
            sys.exit(1)
        
        _to = get_nllb_lang(target_language)
        _log(f"Translating to {_to}.", logger, spinner, 'info')

        # Translate prompt loop
        if translate_from_choice == 0:
            try:
                _log("Preparing to translate...", logger, spinner, 'info')
                
                if is_interactive and spinner:
                    _log(please_wait_disclamer, logger, spinner, 'info')
                    spinner.start()
                    spinner.text = please_wait_short

                translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline, batch_size=batch_size, n_proc=nproc)
                
                if is_interactive and spinner:
                    spinner.text = ""
                    spinner.stop()
            except (
                RuntimeError,
                Exception,
                KeyboardInterrupt
            ) as exception:
                _log("Sorry could not load translator due to the following exception:", logger, spinner, 'error')
                raise exception
            
            _log("Type [Ctrl] + [C] to exit.")
            _log(" "*10)
            try:
                while True:
                    _log("What would you like to translate?")
                    sentence = questionary.text("Translate:").ask()
                    if sentence:
                        translation = translate_sentence(sentence, translator)
                        for t in translation: _log(f"{t}")
                        _log(" "*10)
                    else:
                        sys.exit(1)
            except KeyboardInterrupt:
                sys.exit(1)
        elif translate_from_choice == 1:
            # Or batch translate from directory
            _dir = Path("/nowhere/in/particular/")
            while not _dir.exists() and not _dir.is_dir():
                source_directory = questionary.path("Which directory contains text file(s) to translate?", default=".", only_directories=True).ask()
                if not source_directory:
                    sys.exit(1)
                _dir = Path(source_directory)
                if not _dir.exists(): _log(f"{source_directory} does not exists.", logger, spinner, 'error')
                if not _dir.is_dir(): _log(f"{source_directory} is not a directory.", logger, spinner, 'error')
            
            _directory = _dir.as_posix()

            _save = Path("/nowhere/in/particular/file.txt")
            while not _save.exists() and not _save.is_file():
                save_file = questionary.path("Which file translations shall be saved to?", default="./translations.txt").ask()
                if not save_file:
                    sys.exit(1)
                _save = Path(save_file)
                if not _save.exists(): _log(f"{save_file} does not exists.", logger, spinner, 'error')
                if not _save.is_file(): _log(f"{save_file} is not a file.", logger, spinner, 'error')
            
            _save_path = _save.as_posix()

        nepoch = int(questionary.text("How many epochs to translate?", default=str(nepoch)).ask()) or nepoch
        batch_size = int(questionary.text("How many sentences to batch together?", default=str(args.batch_size)).ask()) or batch_size
        nproc = int(questionary.text("How many processes to spawn for translation?", default=str(nproc)).ask()) or nproc


    if _from and _to and not _sentences:
        if _to not in get_nllb_lang() and _to == get_nllb_lang(_to):
            _sentences = [args._to]
            _to = get_sys_lang_format()
            _log(f"Target language was not provided. Translating to \'{_to}\'.", logger, spinner, 'info')
        elif not _directory:
            _log(f"Missing sentences to translate.", logger, spinner, 'error')
            sys.exit(1)
    
    if not _to and _from:
        if not _directory:
            _log(f"Missing \'_to\' argument.", logger, spinner, 'error')
            print("Please choose a target language or at least give a sentence or a directory to translate.")
            print("Type \'translate --help\' to get help.")
            sys.exit(1)
        else:
            _to = get_sys_lang_format()
            _log(f"Target language was not provided. Translating to \'{_to}\'.", logger, spinner, 'info')
    
    if not _from:
        _log(f"Missing \'_from\' argument.", logger, spinner, 'error')
        print("Please provide at least a source language.")
        sys.exit(1)

    for _lang in [_from, _to]:
        if _lang not in get_nllb_lang() and args.model_id == "facebook/nllb-200-distilled-600M":
            _log(f"Warning! {_lang} is not listed as supported language by the current model {args.model_id}.", logging, spinner, 'warning')
            print("There is a high probability translation will fail.")
            print("Type translate --language_list to get the full list of supported languages.")
            print("Or type \'translate --help\' to get help.")
            _nllb_lang = get_nllb_lang(_lang)
            if _lang == _from:
                _from = _nllb_lang
            elif _lang == _to:
                _to = _nllb_lang
            _log(f"Using {_nllb_lang} instead of {_lang}.", logger, spinner, 'info')
    
    if _from == _to and not _po_mode:
        _log(f"Warning! {_from=} == {_to=} ", logger, spinner, 'warning')
        print("Translating to the same language is computationally wasteful for no valid reason.")
        _log("Using Hitchens's razor to shortcut translation.", logger, spinner, 'info')
        if not _directory:
            if not _save_path:
                for sentence in _sentences: print(sentence)
            else:
                utils.save_txt(_sentences, Path(_save_path))
        else:
            if not _save_path:
                txt_files = utils.glob_files_from_dir(_directory, suffix=".txt")
            else:
                txt_files = list(set(utils.glob_files_from_dir(_directory, suffix=".txt")) - set([_save_path, f"{_directory}/{_save_path}"]) - set(utils.glob_files_from_dir(f"{_save_path.replace('.txt', f'.{_from}.{_to}.tmp.cache')}", suffix="*")))
            if not txt_files:
                _log(f"No files to translate in \'{args.directory}\'.", logger, spinner, 'error')
                sys.exit(1)
            if _save_path:
                with open(_save_path, 'w') as outfile:
                    for fname in txt_files:
                        with open(fname) as infile:
                            for line in infile:
                                outfile.write(line)
            else:
                for fname in txt_files:
                    with open(fname) as infile: print(infile.read())
        sys.exit(0)

    _log("Preparing to translate...", logger, spinner, 'info')
    if is_interactive and spinner:
        _log(please_wait_disclamer, logger, spinner, 'info')
        spinner.start()
        spinner.text = please_wait_short

    translator = Translator(_from, _to, args.max_length, args.model_id, args.pipeline, batch_size=batch_size, n_proc=nproc)

    translations = []
    _translated = []
    
    if is_interactive and spinner:
        spinner.text = ""
        spinner.stop()

    # Handle PO file translation
    if _po_mode and _directory and Path(_directory).exists():
        _log("PO file translation mode enabled.", logger, spinner, 'info')
        
        # Determine target languages to translate
        if _to:
            # Single target language mode
            target_languages = [_to]
            _log(f"Looking for PO files in target language directories for '{_to}' in directory '{_directory}'.", logger, spinner, 'info')
        else:
            # Multi-language mode: detect all target languages
            target_languages = utils.detect_target_languages_from_directory(_directory)
            if not target_languages:
                _log("No target languages found with Language metadata set in PO files.", logger, spinner, 'error')
                _log("Set the Language metadata in your PO files to enable auto-translation (e.g., Language: fr).", logger, spinner, 'info')
                sys.exit(1)
            _log(f"Multi-language mode: Found {len(target_languages)} target languages: {', '.join(target_languages)}", logger, spinner, 'info')
        
        overall_total_translated = 0
        overall_total_processed = 0
        overall_skipped_files = 0
        
        # Process each target language
        for target_lang in target_languages:
            _log(f"Processing target language: {target_lang}", logger, spinner, 'info')
            
            # Find PO files in target language directories only
            po_files = utils.glob_po_files_for_target_language(_directory, target_lang)
            _l = len(po_files)
            if _l == 0:
                target_short = utils.nllb_to_short_code(target_lang)
                _log(f"No PO files found in target language directories for {target_lang} (e.g., locale/{target_short}/, {target_short}/) in '{_directory}'.", logger, spinner, 'warning')
                continue
            _log(f"Found {_l} PO file{'s' if _l > 1 else ''} for {target_lang}.", logger, spinner, 'info')
            
            total_translated = 0
            total_processed = 0
            skipped_files = 0
            
            for po_file_path in po_files:
                _log(f"Processing {po_file_path}...", logger, spinner, 'info')
                
                # Read PO file
                po_file = utils.read_po_file(po_file_path)
                
                # Check if this PO file should be translated based on language metadata matching target
                if not utils.should_translate_po_file(po_file, target_lang):
                    po_language = utils.get_po_language(po_file)
                    target_short = utils.nllb_to_short_code(target_lang)
                    _log(f"Skipping {po_file_path} - language mismatch (PO language: {po_language or 'none'}, target: {target_short})", logger, spinner, 'info')
                    _log(f"Set Language metadata to '{target_short}' in PO file header to enable translation.", logger, spinner, 'info')
                    skipped_files += 1
                    continue
                
                # Extract entries based on force flag
                if _force:
                    texts_to_translate = utils.extract_all_from_po(po_file)
                    mode_msg = "all entries (force mode)"
                else:
                    texts_to_translate = utils.extract_untranslated_from_po(po_file)
                    mode_msg = "untranslated entries"
                
                if not texts_to_translate:
                    _log(f"No {mode_msg} in {po_file_path}.", logger, spinner, 'info')
                    continue
                    
                _log(f"Translating {len(texts_to_translate)} {mode_msg}...", logger, spinner, 'info')
                
                # Translate the texts
                translations = translate_sentence(texts_to_translate, translator)
                
                # Create mapping of original text to translation
                translation_dict = {}
                for i, original in enumerate(texts_to_translate):
                    if i < len(translations):
                        translation_dict[original] = translations[i]
                
                # Update PO file with translations
                utils.update_po_with_translations(po_file, translation_dict, force=_force)
                
                # Save the updated PO file
                utils.save_po_file(po_file, po_file_path)
                
                total_translated += len(translation_dict)
                total_processed += 1
                _log(f"Updated {po_file_path} with {len(translation_dict)} translations.", logger, spinner, 'success')
            
            # Add to overall totals
            overall_total_translated += total_translated
            overall_total_processed += total_processed
            overall_skipped_files += skipped_files
            
            _log(f"Completed {target_lang}: Translated {total_translated} entries across {total_processed} PO file{'s' if total_processed != 1 else ''} (processed {total_processed}/{_l}, skipped {skipped_files}).", logger, spinner, 'success')
        
        _log(f"Multi-language translation completed! Total: {overall_total_translated} entries across {overall_total_processed} PO files, {overall_skipped_files} files skipped.", logger, spinner, 'success')
        sys.exit(0)
    
    # Handle single PO file translation (when file path is passed as sentence)
    if _po_mode and _sentences and len(_sentences) == 1 and _sentences[0].endswith('.po'):
        po_file_path = _sentences[0]
        if not Path(po_file_path).exists():
            _log(f"PO file not found: {po_file_path}", logger, spinner, 'error')
            sys.exit(1)
            
        _log(f"Translating single PO file: {po_file_path}", logger, spinner, 'info')
        
        # Read PO file
        po_file = utils.read_po_file(po_file_path)
        
        # If no target language specified, detect from PO file metadata
        if not _to:
            po_language = utils.get_po_language(po_file)
            if po_language:
                _to = utils.normalize_language_code(po_language)
                _log(f"Detected target language from PO file metadata: {_to}", logger, spinner, 'info')
            else:
                _log(f"Cannot determine target language - no Language metadata in {po_file_path}", logger, spinner, 'error')
                _log("Set Language metadata in PO file header or specify target language explicitly.", logger, spinner, 'info')
                sys.exit(1)
        
        # Check if this PO file should be translated based on language metadata matching target
        if not utils.should_translate_po_file(po_file, _to):
            po_language = utils.get_po_language(po_file)
            target_short = utils.nllb_to_short_code(_to)
            _log(f"Cannot translate {po_file_path} - language mismatch (PO language: {po_language or 'none'}, target: {target_short})", logger, spinner, 'error')
            _log(f"Set Language metadata to '{target_short}' in PO file header to enable translation.", logger, spinner, 'info')
            sys.exit(1)
        
        # Extract entries based on force flag
        if _force:
            texts_to_translate = utils.extract_all_from_po(po_file)
            mode_msg = "all entries (force mode)"
        else:
            texts_to_translate = utils.extract_untranslated_from_po(po_file)
            mode_msg = "untranslated entries"
        
        if not texts_to_translate:
            _log(f"No {mode_msg} in {po_file_path}.", logger, spinner, 'info')
            sys.exit(0)
            
        _log(f"Translating {len(texts_to_translate)} {mode_msg}...", logger, spinner, 'info')
        
        # Translate the texts
        translations = translate_sentence(texts_to_translate, translator)
        
        # Create mapping of original text to translation
        translation_dict = {}
        for i, original in enumerate(texts_to_translate):
            if i < len(translations):
                translation_dict[original] = translations[i]
        
        # Update PO file with translations
        utils.update_po_with_translations(po_file, translation_dict, force=_force)
        
        # Save the updated PO file
        utils.save_po_file(po_file, po_file_path)
        
        _log(f"Translation completed! Updated {po_file_path} with {len(translation_dict)} translations.", logger, spinner, 'success')
        sys.exit(0)

    if _directory and Path(_directory).exists():
        _log("No sentence was given but directory was provided.", logger, spinner, 'info')
        _log(f"Translate sentences in {_from} to {_to} from {'PO' if _po_mode else 'text'} files in directory \'{_directory}\' by batches of size {batch_size}.", logger, spinner, 'info')
        source_path = _directory
        if not _save_path:
            _log("Translating sentences from directory without passing --save argument is forbbiden.", logger, spinner, 'error')
            print("Please choose where to store the translation as text file.")
            _log("Type \'!! --save translations.txt\' to append the --save flag to your last command.", logger, spinner, 'info')
            sys.exit(1)
        output_path = _save_path
        
        cache = f"{output_path.replace('.txt', f'.{_from}.{_to}.tmp.cache')}"
        translated_input_path = f"{cache}/{os.path.basename(output_path)}.{_from}.txt"

        try:
            # Load Data
            if is_interactive and spinner:
                spinner.start()
                spinner.text = "Loading datasets..."
            
            translate_data_files = {'translate': [],}
            translated_data_files = {'translated': [translated_input_path],}
            translation_data_files = {'translation': [output_path],}

            # Load all data to translate
            time_before = time.perf_counter()
            _log("Loading all sentences...", logger, spinner, 'info')
            
            if is_interactive and spinner:
                spinner.text = ""
                spinner.start()
            
            txt_files = list(set(utils.glob_files_from_dir(source_path, suffix=".txt")) - set([output_path, f"{source_path}/{output_path}"]) - set(utils.glob_files_from_dir(cache, suffix="*")))
            _l = len(txt_files)
            if _l == 0:
                _log(f"No files to translate in \'{source_path}\'.", logger, spinner, 'error')
                sys.exit(1)
            _log(f"Found {_l} text file{'s' if _l > 1 else ''}.", logger, spinner, 'info')
            if is_interactive and spinner: spinner.stop()
            
            for t in txt_files: translate_data_files['translate'].append(t)
            
            mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            translate_dataset = load_dataset('text', data_files=translate_data_files, split="translate", cache_dir=cache)
            mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            _log(f"RAM memory used by translate dataset: {(mem_after - mem_before):n} MB", logger, spinner, 'debug')
            to_translate = translate_dataset.unique('text')
            _ds = len(to_translate)
            _log(f"Translating {_ds:n} sentences...", logger, spinner, 'info')
            if is_interactive and spinner: spinner.start()
            
            # Load already translated data if any (skip if force mode is enabled)
            time_before_1 = time.perf_counter()
            if _force:
                _log("Force mode enabled - ignoring cache and retranslating all sentences.", logger, spinner, 'info')
                _t_ds = 0
            else:
                _log("Loading translated sentences...", logger, spinner, 'info')
                if is_interactive and spinner: spinner.stop()
                if Path(translated_input_path).exists() and Path(translated_input_path).is_file() and Path(output_path).exists() and Path(output_path).is_file():
                    mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                    translated_dataset = load_dataset('text', data_files=translated_data_files, split="translated", cache_dir=cache)
                    mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                    _log(f"RAM memory used by translated dataset: {(mem_after - mem_before):n} MB", logger, spinner, 'debug')
                    been_translated = translated_dataset.unique('text')
                    _t_ds = len(been_translated)
                    _translated += been_translated
                    _log(f"Translated {_t_ds:n} sentences already.", logger, spinner, 'info')
                    
                    mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                    translation_dataset = load_dataset('text', data_files=translation_data_files, split="translation", cache_dir=cache)
                    mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                    _log(f"RAM memory used by translation dataset: {(mem_after - mem_before):n} MB", logger, spinner, 'debug')
                    translations += translation_dataset.unique('text')
                    if is_interactive and spinner: spinner.start()
                else:
                    _t_ds = 0
                    _log("Not translated any sentences yet.", logger, spinner, 'info')
                    if is_interactive and spinner: spinner.start()
            time_after_1 = time.perf_counter()
            _td_1 = time_after_1 - time_before_1
            _log(f"Took {timedelta(seconds=_td_1)} second(s) to load {_t_ds:n} translated sentence(s).", logger, spinner, 'debug')
            if is_interactive and spinner: spinner.start()

            # Filter translated data from all data to get untranslated data (skip if force mode)
            time_before_2 = time.perf_counter()
            if is_interactive and spinner: spinner.stop()
            mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            if _force or not _translated:
                untranslated_dataset = translate_dataset
                if _force:
                    _log("Force mode: Translating all sentences regardless of cache...", logger, spinner, 'info')
            else:
                _log("Filtering untranslated sentences...", logger, spinner, 'info')

                if is_interactive and spinner:
                    spinner.start()
                    spinner.text = "Filtering translated sentences..."

                untranslated = { 'text': list( set(to_translate) - set(_translated) ) }
                untranslated_dataset = Dataset.from_dict(untranslated)

                if is_interactive and spinner:
                    spinner.stop()
                    spinner.text = ""

            mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            _log(f"RAM memory used by untranslated dataset: {(mem_after - mem_before):n} MB", logger, spinner, 'debug')
            time_after_2 = time.perf_counter()
            _td_2 = time_after_2 - time_before_2
            untranslated = untranslated_dataset.unique('text')
            _ut_ds = len(untranslated) # _ds - len(_translated)
            _log(f"Took {timedelta(seconds=_td_2)} second(s) to compute {_ut_ds:n} untranslated sentence(s).", logger, spinner, 'debug')
            
            # Lets be absolutely sure we have the right amount of sentences
            assert _ds - _t_ds == _ut_ds, _log(f"{_ds=} - {_t_ds=} ({_ds - _t_ds}) != {_ut_ds=}", logger, spinner, 'error')
            
            if is_interactive and spinner: spinner.start()
            
            # Translate untranslated data
            time_before_3 = time.perf_counter()
            _log("Translating untranslated sentences...", logger, spinner, 'debug')
            
            i, _i, _t = 0, 0, 0
            epoch_split = int(_ut_ds / nepoch)
            _log(f"Epoch size: {epoch_split:n}", logger, spinner, 'info')

            # Lets be absolutely sure epoch_split is not too small or too big
            assert epoch_split > 0, _log(f"Value for {epoch_split=} is too small! Must be greater than 0.", logger, spinner, 'error')
            assert epoch_split < _ut_ds, _log(f"Value for {epoch_split=} is too big! Must be smaller than the amount of sentences to translate ({_ut_ds}).", logger, spinner, 'error')

            if is_interactive and spinner:
                spinner.start()
                spinner.text = f"Processing first epoch of {epoch_split:n} sentences by batch of {batch_size:n} ({_ut_ds:n} ({nepoch:n} epochs) total)..."
            
            for epoch in untranslated_dataset.iter(epoch_split):
                _t = time.perf_counter()
                _epoch_text =  epoch['text']
                _translated += _epoch_text
                # Here we translate the epoch
                translations += translate_sentence(_epoch_text, translator)
                # Then we update statistics
                time_meanwhile = time.perf_counter()
                _td = time_meanwhile - _t
                #_td2 = time_meanwhile - time_before_3
                i += 1
                _i += epoch_split
                _avg1 = epoch_split/_td
                #_avg2 = _i/_td2
                #_avg = (_avg1 + _avg2)/2
                _etr = (_ut_ds - _i) / _avg1
                update = f"Epoch {i:n}/{nepoch:n} | {_i:n}/{_ut_ds:n} ({_i/_ut_ds:.2%}) | ~{_avg1:.2f} translation(s) / second | ETR: {timedelta(seconds=_etr)} | dT: {timedelta(seconds=_td)}"
                _log(update, logger, None, 'debug' if args.debug else 'info')
                if is_interactive and spinner: spinner.text = update
            
            time_after_3 = time.perf_counter()
            _td_3 = time_after_3 - time_before_3
            
            if is_interactive and spinner: spinner.text = "Please wait..."
            _log("Checking translation results...", logger, spinner, 'debug' if args.debug else 'info')
            
            if _ds != (_t_ds + _ut_ds) or _ds != len(translations):
                has_failed = True
                print(f"Loaded {_ds} sentences in {_from} for translation in {_to}.")
                if _ds == (_t_ds + _ut_ds):
                    print(f"Found {_t_ds} sentences already translated.")
                    print(f"So translation was done only on {_ut_ds} sentences.")
                    has_failed = False
                else:
                    _log(f"{_t_ds=} + {_ut_ds=} ({(_t_ds+_ut_ds)=}) != {_ds=}", logger, spinner, 'warning')
                if _ds == len(translations):
                    print(f"You have translated all {_ds} sentences.")
                    has_failed = False
                else:
                    length_translations = len(translations)
                    _log(f"{_ds=} != {length_translations=}", logger, spinner, 'error')
                    print(f"Not all {_ds} sentences have been translated.")
                    print(f"Only {length_translations} have been.")
                    has_failed = True
                if has_failed: sys.exit(1)
            
            _log("Translation completed.", logger, spinner, 'success')
            _log(f"Took {timedelta(seconds=_td_3)} second(s) to translate {_ut_ds:n} sentences.", logger, spinner, 'info')

            # Report translation
            time_after = time.perf_counter()
            _td = time_after - time_before
            _log(f"All files in {source_path} have been translated from {_from} to {_to}.", logger, spinner, 'sucess')
            _sgb = _ut_ds >> 30
            if _sgb > 0:
                _log(f"Took {timedelta(seconds=_td)} second(s) to translate over {_sgb} GB (~ {float(_ut_ds >> 27)/_td:.1f} Gb/s).", logger, spinner, 'info')
            else:
                _log(f"Took {timedelta(seconds=_td)} second(s) to translate less than 1 GB.", logger, spinner, 'info')

            if Path(cache).exists():
                if is_interactive and spinner:
                    spinner.text = "Please wait..."
                    spinner.start()
                shutil.rmtree(cache)
                if is_interactive and spinner: spinner.stop()
                _log("Removed cache...", logger, spinner, 'info')

        except (
            KeyboardInterrupt,
            RuntimeError,
            NotImplementedError,
            Exception,
        ) as exception:
            _log(str(exception), logger, spinner, 'error')
            _log("You are about to loose your progress!", logger, spinner, 'warning')
            if _save_path and translations and _translated:
                with Path(translated_input_path) as p:
                    if not p.parent.exists():
                        p.parent.mkdir(parents=True, exist_ok=True)
                    if p.exists(): os.remove(p)
                    utils.save_txt(_translated, p)
                with Path(output_path) as _p:
                    if _p.exists():
                        os.remove(_p)
                    utils.save_txt(translations, _p)         
                _log(f"Partial translation has been saved under {output_path}.", logger, spinner, 'success')
            #raise exception
            sys.exit(1)
    else:
        translation = translate_sentence(_sentences, translator)
        for t in translation: print(t)
        translations.append(translation)
    
    if _save_path:
        with Path(_save_path) as p:
            if not p.exists():
                utils.save_txt(translations, p)
            else:
                _log(f"{_save_path} exists already.", logger, spinner, 'warning')
                _log("Translated sentences will be overwritten.", logger, spinner, 'info')
                if p.exists(): os.remove(p)
                utils.save_txt(translations, p)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except NotImplementedError as exception:
        print(str(exception))
        sys.exit(2)
    except (Exception, RuntimeError) as exception:
        raise exception
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
