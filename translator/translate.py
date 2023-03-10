from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import logging

logger = logging.Logger(__file__)

class Translator:
    
    def __init__(self, source_language, target_language, max_length=500, model_id="facebook/nllb-200-distilled-600M", pipe_line="translation") -> None:
        logger.debug("Initializing Translator...")
        self.source = source_language
        logger.debug(f"{self.source}")
        self.target = target_language
        logger.debug(f"{self.target}")
        self.model_id = model_id
        logger.debug(f"{self.model_id}")
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logger.debug(f"{self.device}")
        logger.debug("Loading model...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        logger.debug("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        logger.debug("Setting up translation pipeline...")
        self.translator = pipeline(
            "translation",
            model=self.model,
            tokenizer=self.tokenizer,
            src_lang=source_language,
            tgt_lang=target_language,
            max_length=max_length,
            device=self.device,
        )
        logger.debug("Translator has been successfully loaded.")

    def translate(self, to_translate):
        try:
            return [x['translation_text'] for x in self.translator(to_translate)]
        except UserWarning:
            pass
        


