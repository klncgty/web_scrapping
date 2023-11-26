import httpx
from selectolax.parser import HTMLParser
import pandas as pd
import time
from urllib.parse import urljoin


def get_html(url,**kwargs):
#istemci olarak sunucuya kendimizi tanıttığımız bir http başlıktır user agent. 
    headers = {
        "User-Agent": "USERAGENT"
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
    



#istenilen çıktı alınamıyorsa None geçsin.
def extract_text(html, sel):
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None


def main():
    url= "https://www.rei.com/c/camping-and-hiking/f/scd-deals?page="
    for x in range(1,100):
        print(f" {x}.sayfa gösteriliyor  ")
        html=get_html(url,page=x)
        
        if html is False:
            break
        product_urls = parse_search_page(html)
        for url  in product_urls:
            print(url)
            html = get_html(url)
            print(html.css_first("title").text())
        time.sleep(1)
            
            
    

if __name__ == "__main__":
    main()
    
