from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

class Translator:
    
    def __init__(self, source_language, target_language, max_length=500, model_id="facebook/nllb-200-distilled-600M", pipe_line="translation") -> None:
        self.model_id = model_id
        self.device = 0 if torch.cuda.is_available() else -1
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.translator = pipeline(
            "translation",
            model=self.model,
            tokenizer=self.tokenizer,
            src_lang=source_language,
            tgt_lang=target_language,
            max_length=max_length,
            device=self.device,
        )

    def translate(self, sentence: str):
        return self.translator(sentence)[0]['translation_text']


