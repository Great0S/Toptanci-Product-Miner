import glob
import json
import math
import os
import random

import requests

from config.settings import settings
from models.category_processor import category_processor
from models.dump_category import check_category

logger = settings.logger
turk_translate = settings.turk_translate
arabic_translate = settings.english_translate
headers = settings.ecwid_headers

# Creates a product and assign the main product image
def create_product(products):
    global ResContent, Main, body, seoNameEn
    main_category = main_category_ar = None
    categories = check_category()[0]
    
    # Checking message type
    for product in products:
        try:

            # Creating variables with ready to use data from telegram message            
            name = turk_translate.translate(product['name'])
            nameAr = arabic_translate.translate(name)
            desc = turk_translate.translate(product['descr'])
            desc_ar = arabic_translate.translate(desc)
            pc_quantity = [qty for qty in product['attrs']['stock']]
            pc_price = [math.ceil(float(pc) * 1.3 / 18 + 1.5) for pc in product['attrs']['price']]
            color = [turk_translate.translate(co) for co in product['attrs']['color']]
            colorAr = [arabic_translate.translate(coAr) for coAr in color]
            sku = [sk for sk in product['attrs']['code']]
            price = [pc_price[i] * pc_quantity[i] for i in range(len(pc_price))]
            
            true = True

            # Category values
            main_category = turk_translate.translate(product['main-category'])    
            second_category = turk_translate.translate(product['sub-category'])   
            
            # Assigning categories using a for loop and a condition to match stored category list
            main_category_ar, second_category_name_ar, categories_ids, main_category_id, categories_json = category_processor(main_category, second_category, categories)

            
            # Create a product request body   
            if second_category_name_ar:         
                seo_name_ar = main_category_ar + ' / ' + second_category_name_ar + ' / ' + nameAr
            else:
                seo_name_ar = main_category_ar + ' / ' + nameAr
                      
            seo_name = main_category + ' / ' + name           
            
            for attr in sku:
                body = {
                "sku": str(attr),
                "unlimited": False,
                "inStock": true,
                "inStovalue": true,
                "quantity": pc_quantity[sku.index(attr)],
                "name": name,
                "nameTranslated": {
                    "ar": nameAr,
                    "en": name
                },
                "price": price[sku.index(attr)],
                "enabled": true,
                "productClassId": 36317504,
                "description": desc,
                "descriptionTranslated": {
                    "ar": desc_ar,
                    "en": desc
                },
                "categoryIds": categories_ids,
                "categories": categories_json,
                "defaultCategoryId": main_category_id,
                "seoTitle": f'{seo_name}',
                "seoTitleTranslated": {
                    "ar": seo_name_ar,
                    "en": seo_name
                },
                "seoDescription": desc,
                "seoDescriptionTranslated": {
                    "ar": desc_ar,
                    "en": desc
                },
                "attributes": [
                    {
                        "id": 159588021,
                        "name": "UPC",
                        "nameTranslated": {
                            "ar": "رمز المنتج العالمي",
                            "en": "UPC"
                        },
                        "value": f"{attr}",
                        "valueTranslated": {
                            "ar": f"{attr}",
                            "en": f"{attr}"
                        },
                        "show": "DESCR",
                        "type": "UPC"
                    },
                    {
                        "id": 159588022,
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
                        "id": 159588025,
                        "name": "Color",
                        "nameTranslated": {
                            "ar": "اللون",
                            "en": "Color"
                        },
                        "value": f"{color[sku.index(attr)]}",
                        "valueTranslated": {
                            "ar": f"{colorAr[sku.index(attr)]}",
                            "en": f"{color[sku.index(attr)]}"
                        },
                        "show": "DESCR",
                        "type": "COLOR"
                    },
                    {
                        "id": 159588028,
                        "name": "Pieces count",
                        "nameTranslated": {
                            "ar": "عدد القطع",
                            "en": "Pieces count"
                        },
                        "value": f"{pc_quantity[sku.index(attr)]}",
                        "valueTranslated": {
                            "ar": f"{pc_quantity[sku.index(attr)]}",
                            "en": f"{pc_quantity[sku.index(attr)]}"
                        },
                        "show": "PRICE",
                        "type": "UNITS_IN_PRODUCT"
                    },
                    {
                        "id": 159588029,
                        "name": "Price per  piece",
                        "nameTranslated": {
                            "ar": "السعر للقطعة الواحدة",
                            "en": "Price per  piece"
                        },
                        "value": f"{pc_price[sku.index(attr)]}",
                        "valueTranslated": {
                            "ar": f"{pc_price[sku.index(attr)]}",
                            "en": f"{pc_price[sku.index(attr)]}"
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
                "googleProductCategory": 167,
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
                                Main_IMG.write(requests.get(product['images']['color'][sku.index(attr)], headers={
                                    "User-Agent": "Chrome/51.0.2704.103",
                                }, stream=True).content)
                            Main_IMG.close()
                            Main_IMG = open(Main_name, 'rb').read()                            
                            MainImgRes = requests.post(
                                f'https://app.ecwid.com/api/v3/63690252/products/{ItemId}/image?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7', data=Main_IMG, headers=headers)
                            if MainImgRes.status_code == 200:
                                logger.info(
                                f'Main image upload is successful | Status code: {MainImgRes.status_code} | Reason: { MainImgRes.reason} | Image name: {Main_name}')
                            elif MainImgRes.status_code == 422:
                                logger.warning(f"Main image upload is not successful | Reason: {MainImgRes.content} | Status: {MainImgRes.status_code} | URL: {product['images'][sku.index(attr)]}")

                            # del product['images'][0]

                            # for img in product['images']:
                            #     file_name = f'media/{random.randint(300000, 90000000)}.jpg'
                            #     with open(file_name, 'wb') as file:
                            #         file.write(requests.get(img, headers=headers, stream=True).content)

                            #     file.close()
                            #     file = open(file_name, 'rb').read()
                            #     gallery_upload = requests.post(
                            #         f'https://app.ecwid.com/api/v3/63690252/products/{ItemId}/gallery?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7',
                            #         data=file,
                            #         headers=headers)
                            #     if gallery_upload.status_code == 200:
                            #         logger.info(
                            #         f"Gallery image uploaded | Status code: {gallery_upload.status_code} | Reason: {gallery_upload.reason} | Filename: {file_name}"
                            #     )
                            #     elif gallery_upload.status_code == 422:
                            #         logger.warning(f"Main image upload is not successful | Reason: {gallery_upload.content} | Status: {gallery_upload.status_code} | URL: {img}")
                        
                        except Exception as e:
                            logger.exception(e)

                        Files = glob.glob('media/*')
                        for file in Files:
                            os.remove(file)
                            
                        logger.info(
                            f"Product created successfully with ID: {ItemId} | SKU: {sku}"
                        )
                    else:
                        logger.error(
                            f"Product ID is empty?! | Response: {ResContent} | Sku: {sku}")
                        

                elif resCode == 400:
                    logger.error(
                        f"New product body request parameters are malformed | Sku: {sku} | Error Message: {ResContent['errorMessage']} | Error code: {ResContent['errorCode']}"
                    )
                    break
                elif resCode == 409:
                    logger.warning(
                        f"SKU_ALREADY_EXISTS: {sku} | Error Message: {ResContent['errorMessage']} | Error code: {ResContent['errorCode']}"
                    )
                    continue
                else:
                    logger.info(
                        f"Failed to create a new product")
                    break

        # Errors handling
        except IndexError as e:
            logger.exception(e)
            continue

        except KeyError as e:
            logger.exception(e)
            continue

        except ValueError as e:
            logger.exception(e)
            break

def poster(body):

    # Sending the POST request to create the products
    postData = json.dumps(body)
    response = requests.post(settings.products_url, data=postData, headers=headers)
    resCode = int(response.status_code)
    response = json.loads(response.text.encode('utf-8'))
    logger.info("Body request has been sent")
    
    return response, resCode