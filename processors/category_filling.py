import logging
from logging import config
import re

from config.logger import log_config

config.dictConfig(log_config)
logger = logging.getLogger('mainLog')

# noinspection PyDictDuplicateKeys
def category_fill(jCatMain, jCatSec, CatName, CatId, MCategory):
    global secName
    secondCategoryID = None
    defaultCategoryID = None
    secondCategory = None
    defaultCategory = None
    secName = None
    for value in CatName:
        if re.match(jCatMain, value) and len(value) == len(jCatMain):
            secName = value
            defaultCategoryID = CatName.index(value)
            defaultCategory = CatId[defaultCategoryID]
            break

        elif re.match(jCatSec, value) and len(value) == len(jCatSec):
            secondCategoryID = int(CatName.index(value))
            secondCategory = CatId[secondCategoryID]
            break

        else:
            secondCategory = None
            defaultCategory = None
            secName = ''
            Category = []
            continue

    MainCategory = int(MCategory)

    # Validating category data
    try:
        if defaultCategory == MainCategory:
            if secondCategoryID is None:
                Category = [MainCategory]
                Cats = {"id": MainCategory,
                        "enabled": True}
            else:
                Category = [MainCategory, secondCategory]
                Cats = {"id": MainCategory,
                        "enabled": True}, {"id": secondCategory,
                                           "enabled": True}

        elif defaultCategory != MainCategory:
            if secondCategoryID is None:
                if defaultCategory is None:
                    Category = [MainCategory]
                    Cats = {"id": MainCategory,
                            "enabled": True}
                else:
                    Category = [MainCategory, defaultCategory]
                    Cats = {"id": MainCategory,
                            "enabled": True}, {"id": defaultCategory,
                                               "enabled": True}
            else:
                Category = [MainCategory, defaultCategory, secondCategory]
                # noinspection PyDictDuplicateKeys
                Cats = {"id": MainCategory,
                        "enabled": True, "id": defaultCategory}, {
                    "enabled": True, "id": secondCategory}, {
                    "enabled": True}

    except IndexError as e:
        logger.info(f"Category filling IndexError occurred: {e}")
        defaultCategory = secondCategory
        Category = [MainCategory, defaultCategory]
        # noinspection PyDictDuplicateKeys
        Cats = {"id": MainCategory,
                "enabled": True, "id": defaultCategory,
                "enabled": True}
    logger.info("Category filling is done")
    return secName, Category, MainCategory, Cats
