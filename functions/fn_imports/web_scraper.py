"""Parser bot"""
import re
import json
import requests
from bs4 import BeautifulSoup
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

    def __get_ulta_sales(self, item_type: str) -> list[dict]|None:
        """
        Returns a list of ulta makeup, skincare and haircare sales
        """ 
        if item_type == "makeup":
            url = "https://www.ulta.com/promotion/sale?category=makeup"
        elif item_type == "skincare":
            url = "https://www.ulta.com/promotion/sale?category=skin-care"
        else:
            url = "https://www.ulta.com/promotion/sale?category=hair"
        
        soup = self.__get_ulta_soup(url)
        promo_list = []
        card = "li.ProductListingResults__productCard a"
        items = soup.select(card)
        for i,item in enumerate(items):
            item_type = item.select_one("div.ProductCard__image")
            if item_type is not None and item_type.text != "Sponsored":
                s = item.contents[0].select(
                    "div.ProductPricing")[0].select(
                        "span")[0].text
                sp = re.search(r"\d+(?:\.\d+)?", s).group()
                l = item.contents[0].select("div.ProductPricing")[0].select("span")[2].text
                lp = re.search(r"\d+(?:\.\d+)?", l).group()
                obj = {
                        "sku": soup.select(
                            "li.ProductListingResults__productCard"
                            )[i].attrs["data-sku-id"],
                        "name": item.contents[0].find("img").attrs["alt"],
                        "sale_price": float(sp),
                        "list_price": float(lp),
                        "url": item.attrs["href"],
                        "discount": int(((float(lp)-float(sp))/float(lp))*100),
                    }
                promo_list.append(obj)
        
        pl = promo_list if len(promo_list) else ""
        return pl

    def __get_gwp(self) -> list[str]:
        """
        Returns a list of ulta gwp
        """
        soup = self.__get_ulta_soup("https://www.ulta.com/promotion/gift-with-purchase")
        promo_list = []
        items = soup.select("li.PromotionListingResults__compactDealCard div.CompactDealCard__gwpLine")
        for item in items:
            obj = item.select("div")[0].text + " " + item.select("div")[2].text     
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
        for item in items:
            obj = item.select("div.LargeDealCard__headline")[0].text +" "+ item.select("div.LargeDealCard__subtitle")[0].text 
            promo_list.append(obj)
        
        pl = promo_list if len(promo_list) else ""
        return pl
    
    def __get_bmsm(self) -> list[str]:
        """
        Returns a list of BOGO ulta promos
        """
        soup = self.__get_ulta_soup("https://www.ulta.com/promotion/buy-more-save-more")
        promo_list = []
        items = soup.select("li.PromotionListingResults__compactDealCard div.CompactDealCard__gwpLine")
        for i,item in enumerate(items):
            text = item.select("div")[2].text
            p1 = re.sub("Online only","",text)
            p2 = re.sub(r"\([^)]*?\)","",p1)   
            promo_list.append(p2)
        pl = promo_list if len(promo_list) else ""
        return pl
    
    def get_sale_data(self, item_type: str) -> list[dict]:
        try:
            sale = self.__get_ulta_sales(item_type)
            return sale
        except (MaxRetryError, AttributeError) as exc:
            raise RuntimeError("Issue with beautiful soup instance") from exc

    def get_promotional_data(self) -> list[str]:
        gwp = self.__get_gwp()
        td = self.__get_td_promos()
        bmsm = self.__get_bmsm()

        return gwp + td + bmsm

