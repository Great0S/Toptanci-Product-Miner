import glob
import json
import logging
import math
import os
import random
import re
from logging import config

import requests
from tqdm import tqdm
import webcolors
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from progressbar import progressbar

from app.app import log_config
from app.tasks import poster
from extraction.dump_category import dump_categories

ts = GoogleTranslator(source="tr", target="en")
ts2 = GoogleTranslator(source="en", target="ar")

config.dictConfig(log_config)
logger = logging.getLogger('mainLog')


cookies = {
    'ticimax_PopupSettings': '{"desktop":false,"mobilApps":false}',
    '__zlcmid': '1DHlQZP5CRr4OeQ',
    'ticiPushNotification': '{"chromePush":false}',
    'TicimaxReferer': 'referer=https://www.ulusoyspor.com/toptan-erkek-ayakkabi-01',
    'SonZiyaretEdilenUrunler': 'strUrunID=44495,39295,44496,44296,9078,9093,9096,9103,9139,9140,9142,9176,9183,9200,9276,9277,9303,14775,18628,18631,18632,27350,27355,28166,28167,31535,31536,33815,34216,35336,35346,35359,35762,35799,35927,35928,35929,35931,35932,35940,35942,36062,36063,36215,36216,36338,36363,36434,36435,36437,36471,36576,36610,36612,36614,36651,36654,36655,36731,36732,36733,36735,36736,36740,36928,36929,36977,36978,37013,37080,37081,37148,37179,37215,37229,37246,37262,37553,37871,38285,38288,38303,38304,38309,38347,38392,38437,38545,38668,38839,38992,39020,39087,39191,39222,39242,39247,39249,39273,39277,39417,39425,39457,39476,39603,39606,39696,39702,39809,39811,39857,39870,39933,39937,39959,40004,40005,40006,40123,40126,40127,40229,40433,40517,40518,40539,40685,40686,40692,40694,40695,40734,40735,40762,40763,40766,40767,40809,40895,40917,40918,40919,40920,41017,41042,41043,41044,41046,41428,41483,41486,41550,41551,41557,41648,41649,41650,41651,41652,41692,41693,41696,41700,41704,41705,41716,41717,41718,41719,41741,41742,41743,41766,41768,41790,41791,41800,41801,41808,41809,41810,41811,27285,41812,41813,41814,41815,41816,41817,41818,41819,41820,41821,41827,41828,41841,41842,41981,41982,41983,42010,42011,42012,42013,42027,42028,42086,42091,42173,42174,42175,42181,42197,42281,42282,42308,42431,42463,42466,42467,42469,42470,42476,42479,42481,42482,42483,42523,42533,42538,42548,42577,42579,42619,42621,42636,43338,43337,43336,42639,42635,42634,42633,42629,42628,42627,42637,42638,42640,42641,42670,42673,42676,42721,42755,42757,42759,42760,42766,42767,42768,42828,42829,42830,42831,42833,42834,42835,42849,42850,42874,42912,42913,42914,42917,42944,42945,42946,42954,42958,42959,43011,43012,43016,43017,43018,43045,43100,43101,43104,43212,43213,43215,43216,43233,43235,43299,43352,43364,43457,43545,43546,43553,43554,43555,43556,43575,43737,43738,43753,43787,43792,43861,43863,43885,43889,43891,43901,43988,43989,43990,43991,43992,43993,43994,44093,44100,44104,44107,44135,44136,44137,44181,44188,44226,44262,44263,44264,44270,44276,44277,44279,44348,44350,44351,44353,44358,44359,44360,44361,44362,44388,44389,44396,44406,44407,44413,44414,44415,44421,44422,44423,44424,44425,44429,44430,44431,44432,44433,44438,44440,44441,44451,44457,44460,44461,44470,44473,44500,44501,35761,34381,34217,42752,42089,44499,44498,44395,44133,44085,43790,43098,44525,44526,42480&strKategoriID=242,229,256,244,267,232,233,280,255,265,247,230,248,268',
    'TcmxSID': 'dcq5ashvd1i1lbyfg4mkc4ad',
    '__cf_bm': 'Rkva610tSj21ulcPIL462tv7uiN9RLqSwRec5VRDM58-1670499974-0-AUPmiLKGGSolSinxDrCUFIt5w5fMztVqfGbb3UprZGpRnnkdchHJHZFy1At9AiC69iAuBuq0IQreO9P1qptVpeU=',
    'Ticimax_Cart_SessionID': '638060969710169946740E9DEB02CC43EA9D671477F54991E5',
    '.TicimaxAuthModule': 'A86BF86423AE321AA0819550D547F01FED0D3F622F1144309FD744BADBC9435AF959EE21AFB6CAEECA8A78D5BBF867EC651131E02FA4EB79FCD27598436B0EE8242B1EE26BDD88E941C80F0FC7AFEDDCBC9F8D2E8DD57DBA0EFE5E443BB2D3BA',
    'Ticimax_Member_Data': 'H4sIAAAAAAAEAA3Kx6JrQAAA0A+y0KItjegliDLs1BGjS67y9e+d9QkM8fbvwFhAJUFvcxmYLcMhd65Sgb4Xb/vE2DppmBeqTygCO47mpKCSmTt1bIZt/hDYByOCYquQ8fxqIt0TajrZW5Jjn74HIKwr35idNyfOX2qnIkeVGp2ags/kxLcSqQnxrGsRqKtj6jnpJGLk5LevjnmSfGIjwfmLbmlLCB+Coj3240ivY8U96TmMu/NxJG+cWT9zx1wjE5uZ/EVpVZsznfdpltLbX9XgOfd19jfSEsrRsBFSsD7RHcSRS9V/xzroBq1h4YQhi6a1Mx1H0usbLeb3a8gkmAL7sL4PFewTt6fILPlGjg7ea5LNRbYYWhRg3mtsjbb9lQu3VZ6vzC78wzs5iCbGR1HEPsTf/ibW8lAYfF5pidXs1QX0EoxNqv8i1hspULT+tqX09OdCl/9pHVdpOCj7ayLO1oBvCUgjTENchWS5Ny0HSnTxhcDUUsIsOZ+Iczd597AS6pJwZI1H6M27tSCe261NNLCMLdhV3Qu8RO4pA7niL76Ptq6vryn32MvT3+AuHle7hEEhCf3oSOHPE4ePFsQDknBnrlPxIq3Pb855jON4Slgn1exPuIaF/g7gSZYYXX+Z+lMFarKLcm6iK8hBHrde1nSElk0ZjGtpfRLZ++DDETgniTf2I+aUMCukS9djdrDJ8L+3YlNHvbGThHb8A3oPMWWgAgAA',
    'CultureSettings': 'H4sIAAAAAAAEAAXByYJDMAAA0A9yQGM99CAytVcaa92qjNIEUUzbr5%2f3vkkExaCz18E9wa2id0Uiw3YVDt77%2fHG4LUTcswhqLSdFHCexOBbAZCGm38fv05bTqsncF3jD3qnFPmKzrj%2fzIt9%2bbmX24dGw6orehG6ODXOjMZ41RhONwHU1i1cr3ILUFCxRUt%2by4ym1wsh0InE6E1MIwtH4NLW715JjF4enjtrwnXGnnJV98yV1ogS2aa8l42TTMpZ8sa6RbC0dsG1ZhqdAGzkv4326yry%2bwFndv8CYXfKH1QvrtW1FHpHNlFLj8mcjnYigNmBJEU7hDVUCXsRlxvdk4N1K%2fF4ZwcxA6C7AzSqwP8rXufGZSSo1P7B7KIjjiq9bAkMM1TJSu%2bPxH9chbwdYAQAA',
}
headers = {
    'path': '/api/member/Login',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en,ar;q=0.9,tr;q=0.8',
    'cache-control': 'no-cache',
    'content-type': 'application/json; charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}
params = {
    'c': 'entry0010',
    'FilterJson': '{"CategoryIdList":[0],"BrandIdList":[],"SupplierIdList":[],"TagIdList":[],"TagId":-1,"FilterObject":[],"MinStockAmount":-1,"IsShowcaseProduct":-1,"IsOpportunityProduct":-1,"FastShipping":-1,"IsNewProduct":-1,"IsDiscountedProduct":-1,"IsShippingFree":-1,"IsProductCombine":-1,"MinPrice":0,"MaxPrice":0,"Point":0,"SearchKeyword":"","StrProductIds":"","IsSimilarProduct":false,"RelatedProductId":0,"ProductKeyword":"","PageContentId":0,"StrProductIDNotEqual":"","IsVariantList":-1,"IsVideoProduct":-1,"ShowBlokVideo":-1,"VideoSetting":{"ShowProductVideo":-1,"AutoPlayVideo":-1},"ShowList":1,"VisibleImageCount":6,"ShowCounterProduct":-1,"ImageSliderActive":false,"ProductListPageId":0,"ShowGiftHintActive":false,"NonStockShowEnd":1}',
    'PagingJson': '{"PageItemCount":0,"PageNumber":1,"OrderBy":"uk.ID","OrderDirection":"DESC"}',
    'CreateFilter': 'true',
    'TransitionOrder': '0',
    'PageType': '1',
    'PageId': '228',
}

products = {"Men": [],
            "Women": [],
            "Kid": [],
            "Baby": []}

URL = "https://www.ulusoyspor.com/en"
URL2 = "https://www.ulusoyspor.com"
Login = 'https://www.ulusoyspor.com/UyeGiris'
colors = list(map(str, webcolors.CSS3_NAMES_TO_HEX.keys()))
switchLock = False


def ulusoyScraper():
    global switchLock
    with requests.Session() as s:
        s.cookies.clear()
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'

        page = s.get(URL)
        logger.info(
            f'New page request has been made | Response: {page.status_code}')
        soup = BeautifulSoup(page.content, "html.parser")
        result = soup.find(id='ResimliMenu1')
        page_element = result.find_all("li", recursive=False, limit=6)
        logger.info(f'Categories found: {len(page_element)}')

        for element in progressbar(page_element):

            # Category's Title and ID
            element_title = re.sub(
                r'\W\d+', '', element.find("a", target="_self").text)
            elemnt_id = re.sub(r'\/\w+\/\w+\-\d+\-\d+\-', '',
                               element.find("a", target="_self").attrs['href'])
            logger.info(
                f'Category being processed: {element_title} | ID: {elemnt_id}')

            # Updating Filter values
            params['FilterJson'] = re.sub(
                '"CategoryIdList":\[\d+\]', f'"CategoryIdList":[{elemnt_id}]', params['FilterJson'])
            params['PagingJson'] = re.sub(
                '"PageNumber":\d+,', f'"PageNumber":1,', params['PagingJson'])
            params['PageId'] = elemnt_id

            # Request to pull category products size
            logger.info(f'Retrieving products list size please wait!')
            ProductListResponse = requests.get(
                'https://www.ulusoyspor.com/api/product/GetProductList', params=params, headers=headers)
            jsonR = json.loads(ProductListResponse.content)
            total = round(jsonR['totalProductCount'] /
                          jsonR['productCountPerPage'])+1
            logger.info(
                f'Products size from {element_title} category with length of {jsonR["totalProductCount"]} has been requested successfully')

            # Setting initial values
            count = 1
            products_link = []

            logger.info(f'Products data scraping start')
            logger.info(f'Pulling products links')
            for offset in progressbar(range(0, total, 1)):
                try:
                    r2 = requests.get(
                        'https://www.ulusoyspor.com/api/product/GetProductList', params=params, headers=headers)
                    data = r2.json()
                except Exception as e:
                    logger.warning(
                        f'Request is not successfull | Status: {r2.status_code} | Reason: {r2.reason} | Error: {e}')
                    continue

                items_list = data['products']
                for product in items_list:
                    products_link.append(
                        f"https://www.ulusoyspor.com/en{product['url']}")

                count += 1
                params['PagingJson'] = re.sub(
                    '"PageNumber":\d+,', f'"PageNumber":{count},', params['PagingJson'])

            logger.info(f'Pulled products links total: {len(products_link)}')
            logger.info(f'Processing products start')
            for product in progressbar(products_link):

                try:
                    product_link = s.get(product, cookies=cookies)
                    product_soup = BeautifulSoup(
                        product_link.content, "html.parser")
                except Exception as e:
                    logger.error(
                        f"Product link error: {e} | Status: {product_link.status_code} | Reason: {product_link.reason}")
                    continue

                sub_category = re.sub(r'\s\d+\s\-\s\d+\W+|\s\d+\s\-\s\d+|\b\d+\-\d+\W+|\>', "", product_soup.find(
                    'div', class_='proCategoryTitle categoryTitleText').contents[1].contents[4].text).strip()
                product_code = re.sub("mpn:", "", product_soup.find(
                    id="divUrunKodu").attrs['content'])
                product_name = ts.translate(re.sub("\n|\d+|\-", "", product_soup.find(
                    class_="ProductName").contents[1].contents[1].string)).strip()
                age_range = re.sub(r'\D+[^\d+\s\-\s\d+\b]', "", product_soup.find(
                    'div', class_='proCategoryTitle categoryTitleText').contents[1].contents[4].text).strip()
                product_qty = int(product_soup.find(
                    "div", id="divToplamStokAdedi").contents[5].text)
                product_price = int(
                    re.sub('\₺|\,\d+', '', product_soup.find(class_="spanFiyat").text))
                product_brand = re.sub('\n', '', product_soup.find(
                    class_="right_line Marka").text)

                try:
                    product_sizes = re.sub('Asorti:', '', product_soup.find(
                        id="divOzelAlan3").text).strip()
                        
                except Exception as e:
                    product_sizes = 0

                try:
                    product_base = re.sub(
                        r'Taban:|\n', '', product_soup.find(id="divOzelAlan4").text)
                except Exception as e:
                    product_base = "Normal"

                try:
                    product_colors = product_name.split()
                    p_color = products_update = None
                    for color in product_colors:
                        color = color.lower()
                        if p_color:
                            if color in colors:
                                p_color = f'{p_color} and {color}'
                                p_color = p_color.capitalize()
                        elif color in colors:
                            p_color = color
                            p_color = p_color.capitalize()
                        elif color == 'ice':
                            if p_color:
                                p_color = f'{p_color} and white'
                                p_color = p_color.capitalize()
                            else:
                                p_color = 'white'
                                p_color = p_color.capitalize()
                    if p_color:
                        pass
                    else:
                        p_color = "Not set"
                except Exception or ValueError or AttributeError:
                    p_color = "Not set"

                CategoryID = None
                if re.search('Men', element_title):
                    CategoryID = 127508528
                elif re.search('Women', element_title):
                    CategoryID = 127508529
                elif re.search('Kid', element_title):
                    CategoryID = 136888060
                elif re.search('Baby', element_title):
                    CategoryID = 142990393

                products_update = {"category_id": CategoryID, "category": element_title, "sub-category": sub_category, "code": product_code, "name": product_name, "images": [], "qty": product_qty,
                                   "price": product_price, "brand": product_brand, "age": age_range, "sizes": product_sizes, "base": product_base, "color": p_color}

                product_image = product_soup.find_all(
                    "img", class_="cloudzoom-gallery")
                for image in product_image:
                    products_update['images'].append(
                        URL2 + re.sub("en/", '', re.sub("thumb", "buyuk", image.attrs['src'])))

                products[element_title].append(products_update)
            switchLock = True
            logger.info(element_title)
        logger.info("All data has been processed")
        return


def create_product(products):
    global ResContent, Main, body, seoNameEn, switchLock
    epayload = {}
    eheaders = {
        "Authorization": "Bearer secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7",
        "Content-Type": 'application/json;charset: utf-8'
    }
    while switchLock is False:
        time.sleep(300)

    # Checking message type
    for product in progressbar(products):
        switchLock = False
        product_list = products[product]
        MCategory = products[product][0]['category_id']
        # Dumping categories into a dict var
        categories = dump_categories(MCategory)
        try:
            for data in tqdm(product_list, desc=f'New product %d'):
                # Creating variables with ready to use data from telegram message
                name = f'{product} Shoes'
                nameAr = ts2.translate(f'{product} Shoes')
                size = data['sizes']
                pcQty = 0
                if type(size) == str:
                    processed_int = re.sub(r'\d\d:|Asorti:|\d\d.|Asorti :|=\d\W\w+\s\w+|=\d\W\w+|Asorti|\d\w+', '', size).strip()
                    processed_int = processed_int.replace(':', ' ')
                    pcQty = sum(map(int, processed_int.split()))
                    if pcQty <= 1:
                        pcQty = 8
                else:
                    pcQty = 8
                pcPrice = math.ceil(((data['price'] * 1.04) / 18) + 1.5)
                price = pcPrice * pcQty
                sku = f"BFA{data['code']}"
                color = data['color']
                colorAr = ts2.translate(color)
                age = data['age']
                base = data['base']
                baseAr = base
                gender = genderAr = None
                if re.search('Men|Kid', data['category']):
                    gender = 'Male'
                    genderAr = 'ذكر'
                elif re.search('Baby', data['category']):
                    gender = 'Unisex'
                    genderAr = 'للجنسين'   
                else:
                    gender = 'Female'
                    genderAr = 'أنثى'
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
                    "productClassId": 36100251,
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
                            "value": f"{pcQty}",
                            "valueTranslated": {
                                "ar": f"{pcQty}",
                                "en": f"{pcQty}"
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
                            "value": f"{pcPrice}",
                            "valueTranslated": {
                                "ar": f"{pcPrice}",
                                "en": f"{pcPrice}"
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
                    "googleProductCategory": 187,
                    "googleProductCategoryName": "Apparel & Accessories > Shoes",
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


def main():
    from threading import Thread
    new_thread = Thread(target=ulusoyScraper)
    new_thread.start()
    create_product(products)

# clearing the console from unnecessary


def cls(): return os.system("cls")


cls()

logger.info('New ULUSOYSPOR session has been started')

if __name__ == '__main__':
    import time
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    logger.info("Tasks executed in {elapsed:0.2f} seconds.")
    main()
