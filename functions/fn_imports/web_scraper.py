"""Parser bot"""
import re
import requests
from bs4 import BeautifulSoup, Tag
from urllib3.exceptions import MaxRetryError
from urllib.parse import urlparse, parse_qs

class DealGenerator():
    """Contains methods to assist scraping brand pages"""
    def __init__(self):
        pass

    def __get_ulta_soup(self, url: str) -> BeautifulSoup:
        """Ulta soup using just bs4"""
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def __get_ulta_sales(self, item_category: str) -> list[dict]|None:
        """
        Returns a list of ulta makeup, skincare and haircare sales
        """ 
        if item_category == "makeup":
            url = "https://www.ulta.com/promotion/sale?category=makeup"
        elif item_category == "skincare":
            url = "https://www.ulta.com/promotion/sale?category=skin-care"
        else:
            url = "https://www.ulta.com/promotion/sale?category=hair"
        
        soup = self.__get_ulta_soup(url)
        promo_list = []
        card = "li.ProductListingResults__productCard a"
        items = soup.select(card)
        for item in items:
            if not isinstance(item, Tag):
                continue
            item_type = item.select_one("div.ProductCard__image")
            if item_type == None or item_type.text == "Sponsored":
                continue
            url = item.get("href")
            sku_id = None
            if url and isinstance(url, str):
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                sku_id = query_params.get("sku", [None])[0]

            first_child = next((child for child in item.children if isinstance(child, Tag)), None)
            if not first_child:
                continue
            sp = None
            lp = None
            alt_text = "Unknown Product"
            
            img_tag = first_child.find("img")
            if img_tag and isinstance(img_tag, Tag):
                alt_text = img_tag.get("alt", "Unknown Product")
            spans = first_child.select("div.ProductPricing span")
            if len(spans) > 2:
                s_text = spans[0].text.strip()
                l_text = spans[2].text.strip()

                if match_sp := re.search(r"\d+(?:\.\d+)?", s_text):
                    sp = float(match_sp.group())
                
                if match_lp := re.search(r"\d+(?:\.\d+)?", l_text):
                    lp = float(match_lp.group())  

            if sp is not None and lp is not None and lp > 0:
                obj = {
                    "sku": sku_id, 
                    "name": alt_text,
                    "sale_price": sp,
                    "list_price": lp,
                    "url": url,
                    "discount": int(((lp - sp) / lp) * 100),
                }

                promo_list.append(obj)
        
        pl = promo_list if len(promo_list) else None
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
        
        if isinstance(promo_list, list):
            return promo_list
        return []
    
    
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
        
        if isinstance(promo_list, list):
            return promo_list
        return []
    
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
        if isinstance(promo_list, list):
            return promo_list
        return []
    
    
    def get_sale_data(self, item_type: str) -> list[dict]:
        try:
            sale = self.__get_ulta_sales(item_type)
            if sale:
                return sale
            else:
                raise RuntimeError("Issue with beautiful soup instance")
        except (MaxRetryError, AttributeError) as exc:
            raise RuntimeError("Issue with beautiful soup instance") from exc

    def get_promotional_data(self) -> list[str]:
        gwp = self.__get_gwp()
        td = self.__get_td_promos()
        bmsm = self.__get_bmsm()

        return gwp + td + bmsm
x = DealGenerator()
data = x.get_promotional_data()
with open("./tmp.txt","w") as file:
    file.write(str(data))