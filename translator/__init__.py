from translator.translate import Translator
# from translator.language import get_nllb_lang
from translator.language import get_m2m_lang

__version__ = "0.4.0b5"

# LANGS = get_nllb_lang()
LANGS = get_m2m_lang()