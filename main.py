

import httpx
from selectolax.parser import HTMLParser
import pandas as pd
import time
from urllib.parse import urljoin
from dataclasses import dataclass, asdict


@dataclass
class Item:
    name:str | None
    item_num:str | None
    price:str     | None
    rating:float   | None

 

def get_html(url,**kwargs):
#istemci olarak sunucuya kendimizi tanıttığımız bir http başlıktır user agent. 
    headers = {
        "User-Agent": "YOURAGENT"
        }
# siteden aldığımız geri dönüşleri resp'e depolarız
    if kwargs.get("page"):
        resp = httpx.get(url + str(kwargs.get("page")), headers=headers, follow_redirects=True)
    else:
        resp = httpx.get(url, headers=headers, follow_redirects=True)
    try:
        resp.raise_for_status()    
    except httpx.HTTPStatusError as exc:
        print(f" {exc.request.url} adresine ulaşılırken  {exc.resp.status_code} hatası alındı.")
        return False
    html = HTMLParser(resp.text)
    return html




def parse_search_page(html):
#ürün sınıfı 
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")
#ürün linklerine ulaşma
    for product in products:
        yield urljoin("https://www.rei.com", product.css_first("a").attributes["href"])
    


def parse_item_page(html):
    new_item = Item(
        name=extract_text(html, "h1#product-page-title"),
        item_num=extract_text(html, "span#product-item-number"),
        price=extract_text(html, "span#buy-box-product-price"),
        rating=extract_text(html,"span-cdr-rating__number_13-5-3"),
    )
    return new_item

#istenilen çıktı alınamıyorsa None geçsin.
def extract_text(html, sel):
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None


def main():
    products = []
    url= "https://www.rei.com/c/camping-and-hiking/f/scd-deals?page="
    for x in range(1,10):
        print(f" {x}.sayfa gösteriliyor  ")
        html=get_html(url,page=x)
        
        if html is False:
            break
        product_urls = parse_search_page(html)
        for url  in product_urls:
            print(url)
            html = get_html(url)
            products.append(parse_item_page(html))
            time.sleep(0.2)
       
    for product in products:
        print(asdict(product))     
            
    

if __name__ == "__main__":
    main()
    
