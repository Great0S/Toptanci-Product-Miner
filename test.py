import re
from bs4 import BeautifulSoup
import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
a = 'https://toptanci.com/xuping-kalp-zirkon-tasli-luks-kupe-u-223843'
b = 'https://toptanci.com/tasli-buyuk-tasli-ebruli-bros-u-3202'
c = 'https://toptanci.com/modelli-esarp-miknatisi-15-cm-u-221402'
d = 'https://toptanci.com/tasli-ort-boy-ebruli-bros-u-22901'
try:
    product_link = requests.get(a, headers=headers)
    product_soup = BeautifulSoup(product_link.content, "html.parser")
except Exception as e:
    print(
        f"Product link error: {e} | Status: {product_link.status_code} | Reason: {product_link.reason}")

select_sub = product_soup.select('ol.breadcrumb.text-truncate')[0]
select_sub2 = select_sub.select('li.breadcrumb-item')
if len(select_sub2) == 4:
    sub_main_category = re.sub('\n', '', select_sub2[2].text).strip()
else:
    sub_main_category = None
product_name = product_soup.find('div', class_='col-10').contents[1].text
attrs_list = product_soup.select('table.table.table-hover.table-sm')
atrributes = {"color": [], "price": [], "stock": [], "code": []}
if attrs_list:
    for attr in attrs_list:
        stok_yok = attr.find('div', text=re.compile("Stok Yok"))
        if stok_yok:
            continue
        color_attr = attr.find('td', attrs={'style': 'width:30%;'}).text
        price_attr = re.sub(',', '.', re.sub('\₺', '', attr.find(
            'div', text=re.compile(r'\₺')).text).strip())
        stock_attr = int(attr.find('strong', text=re.compile(r'\d+')).text)
        code_attr = int(attr.find('td', class_="",
                        text=re.compile(r'\s\d+\s|\d+')).text)
        
        atrributes['color'].append(color_attr)
        atrributes['price'].append(price_attr)
        atrributes['stock'].append(stock_attr)
        atrributes['code'].append(code_attr)
    product_desc = re.sub(r'\w+;', '', product_soup.select('div.p-3.bg-white.border.rounded-3')[0].contents[1].contents[0].text).strip()
    product_images = product_soup.select('img.img-fluid.btnVariantSmallImage')
else:
    attrs_list = product_soup.find('div',class_='col-md-6 p-4 bg-light')
    price_attr = float(re.sub(',', '.', re.sub('\₺', '', attrs_list.find(text=re.compile(r'\₺')).text).strip()))
    stock_attr = int(re.sub('Stok|\:|\s', '',attrs_list.find(text=re.compile(r'Stok|\:\d+')).text))
    code_attr = int(re.sub('Barkod|\:|\s', '',attrs_list.find(text=re.compile(r'Barkod|\:\d+')).text))
    
    product_desc = attrs_list.find(class_='p-3 bg-white border rounded-3').text.strip()
    product_images = product_soup.find_all('img', attrs={'width': 1000, 'height': 1000})
    
    atrributes['color'].append('Not set')
    atrributes['price'].append(price_attr)
    atrributes['stock'].append(stock_attr)
    atrributes['code'].append(code_attr)
    
    
images = {"color": [], "link": []}
for image in product_images:
    img_link = image.attrs['data-src']
    img_color = image.attrs['alt']

    images['link'].append(img_link)
    images['color'].append(img_color)
if any(atrributes.values()):
    print('s')
else:
    print('f')
