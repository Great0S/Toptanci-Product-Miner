import logging
import requests
from logging import config

from app.app import log_config

config.dictConfig(log_config)
logger = logging.getLogger('mainLog')

def dump_categories(MCategory):
    eurl = "https://app.ecwid.com/api/v3/63690252/products"
    curl = "https://app.ecwid.com/api/v3/63690252/categories?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7"
    eheaders = {
        "Authorization": "Bearer secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7",
        "Content-Type": 'application/json;charset: utf-8'
    }

    # Creating a Get request for categories
    r1 = requests.get(eurl, headers=eheaders).json()
    pages = int(r1['total'])
    categories = {'id': [], 'name': [], 'nameEn': [], 'parentId': []}

    # Pulling categories data and storing them in a list
    for offset in range(0, pages, 100):
        r2 = requests.get(curl + '&offset=' + str(offset)).json()
        items_list = r2['items']

        # Loading primary categories info
        for value in items_list:
            try:
                if 'parentId' in value:
                    if value['parentId'] == MCategory:
                        categories['id'].append(value['id'])
                        categories['name'].append(value['nameTranslated']['ar'])                                          
                        categories['nameEn'].append(value['nameTranslated']['en'])
                        categories['parentId'].append(value['parentId'])
            except KeyError as e:
                logger.debug(f"Parent category dump KeyError: {e}")
                continue

        # Loading secondery categories info
        for va in items_list:
            for cg in categories['id']:
                try:
                    if 'parentId' in va:
                        if va['parentId'] == cg:
                            categories['id'].append(va['id'])
                            categories['name'].append(va['nameTranslated']['ar'])                                                     
                            categories['nameEn'].append(va['nameTranslated']['en'])
                            categories['parentId'].append(va['parentId'])
                except KeyError as e:
                    logger.debug(f"Secondry category dump KeyError: {e}")
                    continue
    logger.info("Category dump is successfull")
    return categories
