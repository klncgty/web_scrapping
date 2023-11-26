

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

 
    """Belirli bir url'den html içeriğini çekmek için yazdığım fonksiyon. 
    eğer bir hata alırsak false değerini dndürür. Devam ederse htmlparser ile analiz edilmiş 
    bir html nesnesine çevirerek, html nesnesini return ediyor.
    """
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
    """ Arama sayfasındaki ürünleri listeleyen html'i tarar.
    li.VcGDfKKy_dvNbxUqm29K sınıfına sahip tüm liste öğelerini seçer. 
    her bür ürünün url'sini oluşturmak için urljon fonksiyonu kullanıldı.
    """
#ürün sınıfı 
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")
#ürün linklerine ulaşma
    for product in products:
        yield urljoin("https://www.rei.com", product.css_first("a").attributes["href"])
    


def parse_item_page(html):
    """ ürüne dair istediğimiz, isim, ürün numarası, fiyat ve puanlamayı bize htmlden bulur getirir.
    
    """
    new_item = Item(
        name=extract_text(html, "h1#product-page-title"),
        item_num=extract_text(html, "span#product-item-number"),
        price=extract_text(html, "span#buy-box-product-price"),
        rating=extract_text(html,"span-cdr-rating__number_13-5-3"),
    )
    return new_item

#istenilen çıktı alınamıyorsa None geçsin.
def extract_text(html, sel):
    """ css selectoru kullanarak html içeriğinden metin çıkarmak için fonksiyon.
        eğer bir öğe bulunamazsa None return eder.
    
    """
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None


def main():
    """Ana işlem fonksiyonu. Her sayfa için ayrı ayrı parse_search_page fonksiynunu kullanarak 
    ürün url'lerini çeker.
     Her bir ürün bağlantısı için parse_item_page fonk. kullanarak ürün bilgilerini alır ve
     products listesine ekler.
     Son olarak asdict fonksiyonu ile her bir ürünü sözlük olarak bastırır.
    """
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
    
