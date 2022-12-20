import logging
from logging import config
import re

from app.app import log_config

config.dictConfig(log_config)
logger = logging.getLogger('mainLog')


def category_processor(jCategory, jCatName, jCatSec, ca, jCatSecRev, jCatMain):
    try:
        if re.search(' و ', jCategory):
            for i in ca:
                jCatMain = ''
                if i == jCategory:
                    jCatMain = jCategory
                    break
                else:
                    continue

            if jCatMain != jCategory:
                jCatMain = ''
                for jc in range(len(jCatName)):
                    separator = 'و'
                    if jc < jCatName.index(separator):
                        jCatMain += ' ' + jCatName[jc]
                        jCatMain = jCatMain.strip()
                        for i in ca:
                            if i == jCatMain:
                                break
                        else:
                            continue
                        break
                    else:
                        continue
                else:
                    pass

            for s in range(len(jCatName)):
                if s > jCatName.index(separator):
                    jCatSec += ' ' + jCatName[s]
                    jCatSec = jCatSec.strip()
                    jSecMain = jCatName[0] + ' ' + jCatSec
                    for i in ca:
                        if i == jCatSec:
                            break
                        elif i == jSecMain:
                            jCatSec = jSecMain
                            break
                        else:
                            continue
                    else:
                        continue
                    break
            else:
                pass

        elif not re.search(' و ', jCategory):
            jCatMain = ''
            for j in range(len(jCatName)):
                jCatMain += ' ' + jCatName[j]
                jCatMain = jCatMain.strip()
                for i in ca:
                    if i == jCatMain:
                        break
                else:
                    continue
                break
            pre = jCatMain.split()
            res = list(set(jCatName).difference(pre))
            for n in res:
                jCatSec += ' ' + n
                jCatSec = jCatSec.strip()
                if len(jCatSec.split()) > 1:
                    jCatSecRev = jCatSec.split()
                    jCatSecRev = ' '.join(reversed(jCatSecRev))
                jSecMain = jCatName[0] + ' ' + jCatSec
                for i in ca:
                    if i == jCatSec:
                        break
                    elif i == jCatSecRev:
                        jCatSec = jCatSecRev
                        break
                    elif i == jSecMain:
                        jCatSec = jSecMain
                        break
                    else:
                        continue
                else:
                    continue
                break

        else:
            pass
        logger.info("Categories processed")
    except KeyError as e:
        logger.warning(f'Category processor KeyError occurred: {e}')
        pass
    except IndexError as e:
        logger.warning(f'Category processor ValueError occurred: {e}')
        pass
    return jCatMain, jCatSec
