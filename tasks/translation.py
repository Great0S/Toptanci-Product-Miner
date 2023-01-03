import time
from config.settings import settings
from deep_translator import exceptions

logger = settings.logger
turk_translate = settings.turk_translate
arabic_translate = settings.arabic_translate
english_translate = settings.english_translate 

def translate_text(arg, ISO_Code: str):       
    while True: 
        try:                
            if type(arg) is str:
                if ISO_Code == 'ar':
                    arg = arabic_translate.translate(arg)
                    return arg
                if ISO_Code == 'en':
                    arg = english_translate.translate(arg)
                    return arg
                if ISO_Code == 'tr':
                    arg = turk_translate.translate(arg)
                    return arg
            else:
                return arg
        except exceptions.TooManyRequests as e:
            logger.error("Too many translation requests | Delaying for 1s")
            time.sleep(1)
            continue
        break