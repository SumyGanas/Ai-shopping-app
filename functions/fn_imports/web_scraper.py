"""Parser bot"""
import re
import unicodedata
import json
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib3.exceptions import MaxRetryError

class DealGenerator():
    """Contains methods to assist scraping brand pages"""
    def __init__(self):
        pass

    def __get_ulta_soup(self, url: str) -> BeautifulSoup:
        """Ulta soup using just bs4"""
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def __get_ulta_sales(self, url: str) -> list[str]|None:
        """
        Returns a list of ulta makeup, skincare and haircare sales
        """ 
        soup = self.__get_ulta_soup(url)
        promo_list = []
        items = soup.select("li.ProductListingResults__productCard a")
        for i,item in enumerate(items):
            item_type = item.select_one("div.ProductCard__image")
            if item_type is not None and item_type.text != "Sponsored":
                obj = {
                        "id": soup.select("li.ProductListingResults__productCard")[i].attrs["data-sku-id"],
                        "n": item.contents[0].find("img").attrs["alt"],
                        "sp": item.contents[0].select("div.ProductPricing")[0].select("span")[0].text,
                        "lp": item.contents[0].select("div.ProductPricing")[0].select("span")[2].text,
                        "u": item.attrs["href"]
                    }
                promo_list.append(obj)
        
        pl = promo_list if len(promo_list) else ""
        return pl

    def __get_gwp(self) -> list[str]:
        """
        Returns a list of ulta promos from a category
        Args: "gwp", "bmsm
        """
        soup = self.__get_ulta_soup("https://www.ulta.com/promotion/gift-with-purchase")
        promo_list = []
        items = soup.select("li.PromotionListingResults__compactDealCard div.CompactDealCard__gwpLine")
        for i,item in enumerate(items):
            obj = {
                "h1": item.select("div")[2].text,
                "h2": item.select("div")[3].text
                }      
            promo_list.append(obj)
        
        pl = promo_list if len(promo_list) else ""
        return pl
    
    def __get_bmsm(self) -> list[str]:
        """
        Returns a list of ulta promos from a category
        Args: "gwp", "bmsm
        """
        soup = self.__get_ulta_soup("https://www.ulta.com/promotion/buy-more-save-more")
        promo_list = []
        items = soup.select("li.PromotionListingResults__compactDealCard div.CompactDealCard__gwpLine")
        for i,item in enumerate(items):
            text = item.select("div")[2].text
            p1 = re.sub("Online only","",text)
            p2 = re.sub(r"\([^)]*?\)","",p1)
            obj = {
                str(i): p2
                }      
            promo_list.append(obj)
        pl = promo_list if len(promo_list) else ""
        return pl
    
    def __get_td_promos(self) -> list[str]:
        """
        Returns a list of ulta promos from today's deals
        """
        soup = self.__get_ulta_soup("https://www.ulta.com/promotion/all")
        promo_list = []
        items = soup.select("div.LargeDealCard__textContent")
        for i,item in enumerate(items):
            obj = {
                "deal": item.select("div.LargeDealCard__headline")[0].text +" "+ item.select("div.LargeDealCard__subtitle")[0].text
                }  
            promo_list.append(obj)
        
        pl = promo_list if len(promo_list) else ""
        return pl
    
    def get_all_data(self):
        """Returns all promos as a string"""
        try:

            makeup = self.__get_ulta_sales("https://www.ulta.com/promotion/sale?category=makeup")
            
            skincare = self.__get_ulta_sales("https://www.ulta.com/promotion/sale?category=skin-care")
            
            haircare = self.__get_ulta_sales("https://www.ulta.com/promotion/sale?category=hair")
           
            gwp = self.__get_gwp()
             
            td = self.__get_td_promos()
            
            bmsm = self.__get_bmsm()

            products = {
                "discounts" : {
                "makeup":makeup,
                "skincare":skincare,
                "haircare":haircare
                },
                "Gift with purchase":gwp,
                "Daily Deals":td,
                "BOGO":bmsm
            }

            return json.dumps(products, ensure_ascii=False, separators=(',', ':'))

        except (MaxRetryError, AttributeError) as exc:
            raise RuntimeError("Issue with beautiful soup instance") from exc
        

x = DealGenerator()
print(x.get_all_data())