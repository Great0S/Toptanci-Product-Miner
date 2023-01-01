import json

import requests
from config.settings import settings

def category_maker(sub, sub_link_title, category_list):
    url = settings.category_url
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    turk_translate = settings.turk_translate
    english_translate = settings.english_translate
    
    sub_name = turk_translate.translate(sub.text.strip())

    if sub_link_title not in category_list['nameEn']:
        main_id = category_list['id'][category_list['nameEn'].index(sub_name)]
        payload = {
            "parentId": main_id,
            "name": f"{sub_link_title}",
            "description": "",
            "enabled": True,
            "orderBy": 10,
            "nameTranslated": {
                    "ar": f"{english_translate.translate(sub_link_title)}",
                    "en": f"{sub_link_title}"
            }
        }
        payload = json.dumps(payload)
        response = requests.request(
            "POST", url, headers=headers, product=payload)

        print(response.text)
    else:
        print('Sub exists')