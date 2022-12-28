from __future__ import absolute_import

import json
import math
import os
import random
import re
import glob
import logging

from logging import config
import time
from progressbar import progressbar
import requests
from deep_translator import GoogleTranslator
import tqdm

from config.logger import log_config
from extraction.dump_category import check_category, dump_categories

# Declaring global variables
config.dictConfig(log_config)
logger = logging.getLogger('mainLog')
ts = GoogleTranslator(source="tr", target="en")
ts2 = GoogleTranslator(source="en", target="ar")
payload = {}
headers = {
    "Authorization": "Bearer secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7",
    "Content-Type": 'application/json;charset: utf-8'
}
eurl = "https://app.ecwid.com/api/v3/63690252/products"
GifFile = None
ResContent = content = VidFile = seoNameEn = None
count = 0
ProcessedMsgID = False
body = {}

# Creates a product and assign the main product image
def create_product(products):
    global ResContent, Main, body, seoNameEn, switchLock
    epayload = {}
    eheaders = {
        "Authorization": "Bearer secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7",
        "Content-Type": 'application/json;charset: utf-8'
    }
    {'sub-category': 'Name Necklace', 'sub-sub-category': None,  'images': {'color': [...], 'link': [...]}}
    while not products:
        time.sleep(60)
        
    # Dumping categories into a dict var    
    categories = dump_categories()
    
    # Checking message type
    for product in products:
        product_list = products[product]        
        MCategory = categories['id'][categories['nameEn'].index(product)]
        
        
        try:
            for data in product_list:
                # Creating variables with ready to use data from telegram message
                name = data['name']
                nameAr = ts2.translate(name)
                desc = data['descr']
                pc_quantity = []   
                pc_price = []
                color = []
                sku = []
                for pc in data['attrs']:
                    pc_quantity.append(data['attrs']['stock'])
                    pc_price.append(math.ceil(((data['attrs']['price'] * 1.3) / 18) + 1.5))
                    color.append(data['attrs']['color'])
                    sku.append(f"BFAK{data['attrs']['code']}")
                    
                price = pc_price * pc_quantity
                class_id = None
                atrributes = {
                            "id": 158400257,
                            "name": "UPC",
                            "nameTranslated": {
                                "ar": "رمز المنتج العالمي",
                                "en": "UPC"
                            },
                            "value": f"{sku}",
                            "valueTranslated": {
                                "ar": f"{sku}",
                                "en": f"{sku}"
                            },
                            "show": "DESCR",
                            "type": "UPC"
                        },
                
                true = True
                false = False

                # Assigning categories
                jCatMain = data['category_id']
                jCatSec = data['sub-category']
                jCatSecAr = ts2.translate(jCatSec)
                CatName = categories['nameEn']
                CatNameAr = categories['name']
                CatId = categories['id']
                if jCatSec == 'Bot':
                    jCatSec = 'Boots'
                elif jCatSec == 'Lighted Shoes':
                    jCatSec = 'Lighted Shoes'
                secondCategoryID = int(CatName.index(jCatSec))
                secondCategory = CatId[secondCategoryID]

                # Create a product request body
                if jCatSecAr in CatNameAr:
                    seoNameAr = CatNameAr[CatNameAr.index(
                        jCatSecAr)] + ' / ' + nameAr
                else:
                    seoNameAr = nameAr
                seoName = jCatSec + ' / ' + name

                body = {
                    "sku": sku,
                    "unlimited": true,
                    "inStovalue": true,
                    "name": name,
                    "nameTranslated": {
                        "ar": nameAr,
                        "en": name
                    },
                    "price": price,
                    "enabled": true,
                    "productClassId": class_id,
                    "description": "<b>Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish shoes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colors.</b>",
                    "descriptionTranslated": {
                        "ar": "<b>اختار/ي أفضل المنتجات من مئات الماركات الراقية التركية. نقدم لك/ي أكبر تشكيلة من الأحذية التركية واحدث الصيحات النسائية والرجالية والاطفال التي تناسب جميع الأذواق. بمقاسات وألوان مختلفة.</b>",
                        "en": "<b>Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish shoes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colors.</b>"
                    },
                    "categoryIds": [jCatMain, secondCategory],
                    "categories": [{"id": jCatMain,
                                    "enabled": True}, {"id": secondCategory,
                                                       "enabled": True}],
                    "defaultCategoryId": jCatMain,
                    "seoTitle": f'{seoName}',
                    "seoTitleTranslated": {
                        "ar": seoNameAr,
                        "en": seoName
                    },
                    "seoDescription": "<b>Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish shoes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colors.</b>",
                    "seoDescriptionTranslated": {
                        "ar": "<b>اختار/ي أفضل المنتجات من مئات الماركات الراقية التركية. نقدم لك/ي أكبر تشكيلة من الأحذية التركية واحدث الصيحات النسائية والرجالية والاطفال التي تناسب جميع الأذواق. بمقاسات وألوان مختلفة.</b>",
                        "en": "<b>Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish shoes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colors.</b>"
                    },
                    "attributes": [
                        {
                            "id": 158400257,
                            "name": "UPC",
                            "nameTranslated": {
                                "ar": "رمز المنتج العالمي",
                                "en": "UPC"
                            },
                            "value": f"{sku}",
                            "valueTranslated": {
                                "ar": f"{sku}",
                                "en": f"{sku}"
                            },
                            "show": "DESCR",
                            "type": "UPC"
                        },
                        {
                            "id": 158400258,
                            "name": "Brand",
                            "nameTranslated": {
                                "ar": "ماركة",
                                "en": "Brand"
                            },
                            "value": "Al Beyan Fashion™",
                            "valueTranslated": {
                                "ar": "Al Beyan Fashion™",
                                "en": "Al Beyan Fashion™"
                            },
                            "show": "DESCR",
                            "type": "BRAND"
                        },
                        {
                            "id": 158400259,
                            "name": "Gender",
                            "nameTranslated": {
                                "ar": "الجنس",
                                "en": "Gender"
                            },
                            "value": f"{gender}",
                            "valueTranslated": {
                                "ar": f"{genderAr}",
                                "en": f"{gender}"
                            },
                            "show": "DESCR",
                            "type": "GENDER"
                        },
                        {
                            "id": 158400260,
                            "name": "Age group",
                            "nameTranslated": {
                                "ar": "الفئة العمرية",
                                "en": "Age group"
                            },
                            "value": f"{age}",
                            "valueTranslated": {
                                "ar": f"{age}",
                                "en": f"{age}"
                            },
                            "show": "DESCR",
                            "type": "AGE_GROUP"
                        },
                        {
                            "id": 158816769,
                            "name": "Base",
                            "nameTranslated": {
                                "ar": "القاعدة",
                                "en": "Base"
                            },
                            "value": f"{base}",
                            "valueTranslated": {
                                "ar": f"{baseAr}",
                                "en": f"{base}"
                            },
                            "type": "CUSTOM",
                            "show": "DESCR"
                        },
                        {
                            "id": 158400261,
                            "name": "Color",
                            "nameTranslated": {
                                "ar": "اللون",
                                "en": "Color"
                            },
                            "value": f"{color}",
                            "valueTranslated": {
                                "ar": f"{colorAr}",
                                "en": f"{color}"
                            },
                            "show": "DESCR",
                            "type": "COLOR"
                        },
                        {
                            "id": 158400262,
                            "name": "Sizes",
                            "nameTranslated": {
                                "ar": "مقاسات",
                                "en": "Sizes"
                            },
                            "value": f"{size}",
                            "valueTranslated": {
                                "ar": f"{size}",
                                "en": f"{size}"
                            },
                            "show": "DESCR",
                            "type": "SIZE"
                        },
                        {
                            "id": 158400265,
                            "name": "Pieces count",
                            "nameTranslated": {
                                "ar": "عدد القطع",
                                "en": "Pieces count"
                            },
                            "value": f"{pc_quantity}",
                            "valueTranslated": {
                                "ar": f"{pc_quantity}",
                                "en": f"{pc_quantity}"
                            },
                            "show": "PRICE",
                            "type": "UNITS_IN_PRODUCT"
                        },
                        {
                            "id": 158400266,
                            "name": "Price per  piece",
                            "nameTranslated": {
                                "ar": "السعر للقطعة الواحدة",
                                "en": "Price per  piece"
                            },
                            "value": f"{pc_price}",
                            "valueTranslated": {
                                "ar": f"{pc_price}",
                                "en": f"{pc_price}"
                            },
                            "show": "PRICE",
                            "type": "PRICE_PER_UNIT"
                        }
                    ],
                    "googleItemCondition": "NEW",
                    "subtitle": "The displayed price is for the full set",
                    "subtitleTranslated": {
                        "ar": "السعر المعروض للسيري كامل",
                        "en": "The displayed price is for the full set"
                    },
                    "googleProductCategory": 16y7,
                    "googleProductCategoryName": "Apparel & Accessories > Clothing Accessories",
                    "productCondition": "NEW"
                }

                # Parsing collected data
                ResContent, resCode = poster(body)
                # Feedback and returning response and media_path new values
                if resCode == 200:
                    # Created product ID
                    if 'id' in ResContent:
                        ItemId = ResContent['id']
                        try:
                            Main_name = f'media/{random.randint(30000, 90000000)}.jpg'
                            with open(Main_name, 'wb') as Main_IMG:
                                Main_IMG.write(requests.get(data['images'][0], headers={
                                    "User-Agent": "Chrome/51.0.2704.103",
                                }, stream=True).content)
                            Main_IMG.close()
                            Main_IMG = open(Main_name, 'rb').read()                            
                            MainImgRes = requests.post(
                                f'https://app.ecwid.com/api/v3/63690252/products/{ItemId}/image?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7', data=Main_IMG, headers=eheaders)
                            if MainImgRes.status_code == 200:
                                logger.info(
                                f'Main image upload is successful | Status code: {MainImgRes.status_code} | Reason: { MainImgRes.reason} | Image name: {Main_name}')
                            elif MainImgRes.status_code == 422:
                                logger.warning(f"Main image upload is not successful | Reason: {MainImgRes.content} | Status: {MainImgRes.status_code} | URL: {data['images'][0]}")

                            del data['images'][0]

                            for img in data['images']:
                                file_name = f'media/{random.randint(300000, 90000000)}.jpg'
                                with open(file_name, 'wb') as file:
                                    file.write(requests.get(img, headers={
                                        "User-Agent": "Chrome/51.0.2704.103",
                                    }, stream=True).content)

                                file.close()
                                file = open(file_name, 'rb').read()
                                gallery_upload = requests.post(
                                    f'https://app.ecwid.com/api/v3/63690252/products/{ItemId}/gallery?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7',
                                    data=file,
                                    headers=eheaders)
                                if gallery_upload.status_code == 200:
                                    logger.info(
                                    f"Gallery image uploaded | Status code: {gallery_upload.status_code} | Reason: {gallery_upload.reason} | Filename: {file_name}"
                                )
                                elif gallery_upload.status_code == 422:
                                    logger.warning(f"Main image upload is not successful | Reason: {gallery_upload.content} | Status: {gallery_upload.status_code} | URL: {img}")
                        
                        except Exception as e:
                            logger.exception(e)

                        Files = glob.glob('media/*')
                        for file in Files:
                            os.remove(file)
                        logger.info(
                            f"Product created successfully with ID: {ItemId} | SKU: {sku}"
                        )
                        continue
                    else:
                        logger.error(
                            f"Product ID is empty?! | Response: {ResContent} | Sku: {sku}")
                        continue

                elif resCode == 400:
                    logger.error(
                        f"New product body request parameters are malformed | Sku: {sku} | Error Message: {ResContent['errorMessage']} | Error code: {ResContent['errorCode']}"
                    )
                    continue
                elif resCode == 409:
                    logger.warning(
                        f"SKU_ALREADY_EXISTS: {sku} | Error Message: {ResContent['errorMessage']} | Error code: {ResContent['errorCode']}"
                    )
                    continue
                else:
                    logger.critical(
                        f"Failed to create a new product")
                    continue

        # Errors handling
        except IndexError as e:
            logger.exception(e)
            continue

        except KeyError as e:
            logger.exception(e)
            continue

        except ValueError as e:
            logger.exception(e)
            continue

def poster(body):

    # Sending the POST request to create the products
    postData = json.dumps(body)
    response = requests.post(eurl, data=postData, headers=headers)
    resCode = int(response.status_code)
    response = json.loads(response.text.encode('utf-8'))
    logger.info("Body request has been sent")
    return response, resCode

# Uploads main image
def UploadMainIMG(ItemId, Main, headers):
    MainImgData = open(Main, 'rb').read()
    MainImgRes = requests.post(
        f'https://app.ecwid.com/api/v3/63690252/products/{ItemId}/image?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7',
        data=MainImgData,
        headers=headers)
    logger.info(
        f'Main image upload is successful | Status code: {MainImgRes.status_code} | Reason: { MainImgRes.reason} | Image name: {Main}'
    )

# Adding gallery images to the product
def uploader(media_path, ItemId, Main):
    global GifFile
    if GifFile:
        GifFile = None
    for img in media_path[0]['image']:
        if img is not None and img != Main:
            upload(ItemId, img)

def upload(ItemId, img):
    ImgFile = open(img, 'rb').read()
    r3 = requests.post(
        f'https://app.ecwid.com/api/v3/63690252/products/{ItemId}/gallery?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7',
        data=ImgFile,
        headers=headers)
    logger.info(
        f"Gallery image uploaded | Status code: {r3.status_code} | Reason: {r3.reason} | Filename: {img}"
    )
    os.remove(os.path.abspath(img))

def category_maker(sub, sub_link_title, category_list):
    url = "https://app.ecwid.com/api/v3/63690252/categories?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7"
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    ts = GoogleTranslator(source="tr", target="en")
    ts2 = GoogleTranslator(source="en", target="ar")
    sub_name = ts.translate(sub.text.strip())
    
    if sub_link_title not in category_list['nameEn']:
        main_id = category_list['id'][category_list['nameEn'].index(sub_name)]
        payload = {
            "parentId": main_id,
            "name": f"{sub_link_title}",
            "description": "",
            "enabled": True,
            "orderBy": 10,
            "nameTranslated": {
                    "ar": f"{ts2.translate(sub_link_title)}",
                    "en": f"{sub_link_title}"
            }
        }
        payload = json.dumps(payload)
        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
    else:
        print('Sub exists')

def clearMediaList(*args, clear=bool, files=bool):
    Files = glob.glob('media/*')
    if args:
        dicts = [arg for arg in args]
        for lists in dicts:
            if len(Files) != 0 and clear == True:
                if type(lists) is tuple:
                    for media_list in lists:
                        for media_file in media_list.values():
                            for file in Files:
                                if file == media_file:
                                    os.remove(file)
                else:
                    for media_file in lists.values():
                        for file in Files:
                            if file == media_file:
                                os.remove(file)
            elif len(Files) != 0 and files == True:
                for file in Files:
                    os.remove(file)

            if type(lists) is dict:
                for lis in lists.values():
                    lis.clear()
            else:
                for val in lists:
                    for lis in val.values():
                        lis.clear()
    else:
        if len(Files) != 0 and files == True:
            for file in Files:
                os.remove(file)
    logger.info(
        f"Media list is cleared | Media List: {args} "
    )

async def clear_all(media_path):
    media_path['image'].clear()
    media_path['grouped_id'].clear()
    Files = glob.glob('media/*')
    for file in Files:
        os.remove(file)
        
        
        
{
            "id": 520048199,
            "sku": "432fdf33",
            "unlimited": true,
            "inStock": true,
            "name": "acce",
            "nameTranslated": {
                "ar": "",
                "en": "acce"
            },
            "price": 0,
            "productClassId": 36317504,
            "enabled": true,
            "options": [
                {
                    "type": "RADIO",
                    "name": "color",
                    "nameTranslated": {
                        "ar": "",
                        "en": "color"
                    },
                    "choices": [
                        {
                            "text": "red",
                            "textTranslated": {
                                "ar": "",
                                "en": "red"
                            },
                            "priceModifier": 5,
                            "priceModifierType": "ABSOLUTE"
                        },
                        {
                            "text": "blue",
                            "textTranslated": {
                                "ar": "",
                                "en": "blue"
                            },
                            "priceModifier": 6,
                            "priceModifierType": "ABSOLUTE"
                        }
                    ],
                    "defaultChoice": 0,
                    "required": false
                },
                {
                    "type": "RADIO",
                    "name": "stok",
                    "nameTranslated": {
                        "ar": "",
                        "en": "stok"
                    },
                    "choices": [
                        {
                            "text": "54",
                            "textTranslated": {
                                "ar": "",
                                "en": "54"
                            },
                            "priceModifier": 0,
                            "priceModifierType": "ABSOLUTE"
                        },
                        {
                            "text": "23",
                            "textTranslated": {
                                "ar": "",
                                "en": "23"
                            },
                            "priceModifier": 0,
                            "priceModifierType": "ABSOLUTE"
                        }
                    ],
                    "defaultChoice": 0,
                    "required": false
                }
            ],
            "defaultCombinationId": 301940169,
            "description": "",
            "descriptionTranslated": {
                "ar": "",
                "en": ""
            },
            "categoryIds": [],
            "categories": [],
            "defaultCategoryId": 0,
            "seoTitle": "",
            "seoTitleTranslated": {
                "ar": "",
                "en": ""
            },
            "seoDescription": "",
            "seoDescriptionTranslated": {
                "ar": "",
                "en": ""
            },
            "attributes": [
                {
                    "id": 159588021,
                    "name": "UPC",
                    "nameTranslated": {
                        "ar": "",
                        "en": "UPC"
                    },
                    "value": "123123ad",
                    "valueTranslated": {
                        "ar": "",
                        "en": "123123ad"
                    },
                    "show": "DESCR",
                    "type": "UPC"
                },
                {
                    "id": 159588022,
                    "name": "Brand",
                    "nameTranslated": {
                        "ar": "",
                        "en": "Brand"
                    },
                    "value": "bfsd",
                    "valueTranslated": {
                        "ar": "",
                        "en": "bfsd"
                    },
                    "show": "DESCR",
                    "type": "BRAND"
                },
                {
                    "id": 159588023,
                    "name": "Gender",
                    "nameTranslated": {
                        "ar": "",
                        "en": "Gender"
                    },
                    "value": "women",
                    "valueTranslated": {
                        "ar": "",
                        "en": "women"
                    },
                    "show": "DESCR",
                    "type": "GENDER"
                },
                {
                    "id": 159588024,
                    "name": "Age group",
                    "nameTranslated": {
                        "ar": "",
                        "en": "Age group"
                    },
                    "value": "23",
                    "valueTranslated": {
                        "ar": "",
                        "en": "23"
                    },
                    "show": "DESCR",
                    "type": "AGE_GROUP"
                },
                {
                    "id": 159588025,
                    "name": "Color",
                    "nameTranslated": {
                        "ar": "",
                        "en": "Color"
                    },
                    "value": "red",
                    "valueTranslated": {
                        "ar": "",
                        "en": "red"
                    },
                    "show": "DESCR",
                    "type": "COLOR"
                },
                {
                    "id": 159588028,
                    "name": "Units in product",
                    "nameTranslated": {
                        "ar": "",
                        "en": "Units in product"
                    },
                    "value": "5",
                    "valueTranslated": {
                        "ar": "",
                        "en": "5"
                    },
                    "show": "PRICE",
                    "type": "UNITS_IN_PRODUCT"
                },
                {
                    "id": 159588029,
                    "name": "Price per unit",
                    "nameTranslated": {
                        "ar": "",
                        "en": "Price per unit"
                    },
                    "value": "12",
                    "valueTranslated": {
                        "ar": "",
                        "en": "12"
                    },
                    "show": "PRICE",
                    "type": "PRICE_PER_UNIT"
                }
            ],
            "googleItemCondition": "NEW",
            "googleProductCategory": 167,
            "googleProductCategoryName": "Apparel & Accessories > Clothing Accessories",
            "productCondition": "NEW"
        }