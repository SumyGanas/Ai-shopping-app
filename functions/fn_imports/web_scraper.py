"""Parser bot"""
import re
import unicodedata
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
            if item_type is not None:
                if item_type.text != "Sponsored":
                    item_name = "Name: "+item.contents[0].find("img").attrs["alt"]+"; "
                    item_link = "Link: "+item.attrs["href"]+"; "
                    list_price = item.contents[0].select("div.ProductPricing")[0].select("span")[2].text+"; "
                    sale_price = item.contents[0].select("div.ProductPricing")[0].select("span")[0].text
                    
                    promo = str(i+1)+". "+item_name+item_link+list_price+sale_price
                    promo_list.append(promo)

        
        return promo_list

    def __get_ulta_promos(self, sale_type: str) -> list[str]:
        """
        Returns a list of ulta promos from a category
        Args: "gwp", "bmsm
        """
        if sale_type == "gwp":
            url = "https://www.ulta.com/promotion/gift-with-purchase"
        elif sale_type == "bmsm":
            url = "https://www.ulta.com/promotion/buy-more-save-more"

        soup = self.__get_ulta_soup(url)
        promo_list = []
        items = soup.select("li.PromotionListingResults__compactDealCard div.CompactDealCard__gwpLine")
        for i,item in enumerate(items):
            ls = []
            for tag in item.descendants:
                if tag.string is not None and isinstance(tag, NavigableString) is True:
                    ls.append(tag.string)
            promo = " ".join(ls)
            indexed_promo = str(i+1)+". "+promo.strip()
            index = indexed_promo.find("(valid thru")
            if index and index != -1:
                edited_promo = indexed_promo[:index]
            promo_list.append(edited_promo)

        promos = "\n".join(promo_list)
        return promos
    
    def __get_td_promos(self):
        """
        Returns a list of ulta promos from today's deals
        """
        url = "https://www.ulta.com/promotion/all"
        soup = self.__get_ulta_soup(url)
        promo_list = []
        items = soup.select("div.LargeDealRail__itemclass div.LargeDealCard__textContent")
        for i,item in enumerate(items):
            try:
                item.find("div.LargeDealCard__actions").extract()
            except AttributeError:
                pass
            ls = []
            for tag in item.descendants:
                if tag.string is not None and isinstance(tag, NavigableString) is True:
                    ls.append(tag.string)
            promo = " ".join(ls)
            indexed_promo = str(i+1)+". "+promo
            promo_list.append(indexed_promo)

            promos = "\n".join(promo_list)
            return "\nDaily deals:\n"+promos

    def get_all_data(self):
        """Returns all promos as a string"""
        try:
            makeup = self.__get_ulta_sales("https://www.ulta.com/promotion/sale?category=makeup")
            makeup_sales = "\n".join(makeup)
            
            skincare = self.__get_ulta_sales("https://www.ulta.com/promotion/sale?category=skin-care")
            skincare_sales = "\n".join(skincare)
            
            haircare = self.__get_ulta_sales("https://www.ulta.com/promotion/sale?category=hair")
            haircare_sales = "\n".join(haircare)

            ulta_sales = "Sales:\n"+"Makeup:\n"+makeup_sales+"\n\n"+"Skincare:\n"+skincare_sales+"\n\n"+"Haircare:\n"+haircare_sales

            gwp = self.__get_ulta_promos("gwp")
            if not gwp:
                gwp = ""
            
            td = self.__get_td_promos()
            if not td:
                td = ""
            
            bmsm = self.__get_ulta_promos("bmsm")
            if not bmsm:
                bmsm = ""

            promos = "Promotions:\n"+"\nGift with purchase:\n"+gwp+"\n"+td+"\n"+"\nBulk discounts:\n"+bmsm
            
            return f"{ulta_sales}\n{promos}"

        except (MaxRetryError, AttributeError) as exc:
            raise RuntimeError("Issue with beautiful soup instance") from exc
        

x = DealGenerator()
print(x.get_all_data())