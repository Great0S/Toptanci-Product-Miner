import json
import logging
import os
import re
from logging import config

import requests
import webcolors
from bs4 import BeautifulSoup
from progressbar import progressbar

from config.logger import log_config
from app.tasks import ts


config.dictConfig(log_config)
logger = logging.getLogger('mainLog')
products = {"Men": [],
            "Women": [],
            "Kid": [],
            "Baby": []}

URL = 'https://toptanci.com/'
colors = list(map(str, webcolors.CSS3_NAMES_TO_HEX.keys()))

def ulusoyScraper():
    with requests.Session() as s:
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'

        page = s.get(URL)
        logger.info(
            f'New page request has been made | Response: {page.status_code}')
        soup = BeautifulSoup(page.content, "html.parser")
        result = soup.find('body')
        navBar = result.find(class_="navbar-nav")
        page_element = navBar.find_all("li", class_='darken-onshow')
        logger.info(f'Categories found count: {len(page_element)}')

        for element in progressbar(page_element):

            # Category's Title and ID
            main_element = element.find('a', class_='nav-link')
            element_title = ts.translate((main_element.text).strip())
            sub_element = element.find('div', class_='list-group')
            sub_categories = sub_element.find_all('a')
            logger.info(
                f'Category being processed: {element_title}')
            for sub in sub_categories:
                sub_link = URL+sub.attrs['href']      
                sub_name = ts.translate((sub.text).strip())         
        

                # Request to pull category products size
                logger.info(f'Retrieving products list size please wait!')
                ProductListResponse = s.get(sub_link)
                sub_soup = BeautifulSoup(ProductListResponse.content, "html.parser")
                sub_result = sub_soup.find('body')
                element_sub = sub_result.find(class_='col-md-10 col-12')                
                element_sub_links = element_sub.contents[7].find_all("div", class_='col')
                element_sub_page = element_sub.find_all('a')
                
            logger.info(
                f'Products size from {element_title} category with length of  has been requested successfully')

            # Setting initial values
            count = 1
            products_link = []

            logger.info(f'Products data scraping start')
            logger.info(f'Pulling products links')
            for offset in progressbar(range(0, 'total', 1)):
                try:
                    r2 = requests.get(
                        'https://www.ulusoyspor.com/api/product/GetProductList')
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

            logger.info(f'Pulled products links total: {len(products_link)}')
            logger.info(f'Processing products start')
            for product in progressbar(products_link):

                try:
                    product_link = s.get(product)
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
                        URL + re.sub("en/", '', re.sub("thumb", "buyuk", image.attrs['src'])))

                products[element_title].append(products_update)
            
            logger.info(element_title)
        logger.info("All data has been processed")
        return


def main():
    from threading import Thread
    new_thread = Thread(target=ulusoyScraper)
    new_thread.start()
    #create_product(products)

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
