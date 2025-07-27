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

    def __get_ulta_soup(self, url) -> BeautifulSoup:
        """Ulta soup using just bs4"""
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def __clean_data(self, deals: list[(str,str)] | list[str], ls_type: str) -> list[str]:
        """Cleans and normalizes data"""
        clean_list = []
        for deal in deals:
            if ls_type == "sale":
                link = deal[1]
                deal = deal[0]
            stripped_deal = deal.lower().strip()
            normalized_deal = unicodedata.normalize('NFKD', stripped_deal)
            reg = re.sub(r'[!"#%&\'()*+,\-/:;<=>?@[\\\]^_`{|}~]', '', normalized_deal)
            clean_deal = re.sub(r'\s+', ' ', reg).strip().title()
            if ls_type == "sale":
                clean_list.append((clean_deal,link))
            elif ls_type == "promo":
                clean_list.append(clean_deal)

        return clean_list

    def __get_ulta_sales(self, url) -> list[str]:
        """
        Returns a list of ulta makeup, skincare and haircare sales
        """ 
        soup = self.__get_ulta_soup(url)
        promo_list = []
        items = soup.select("li.ProductListingResults__productCard a")
        for item in items:
            item_type = item.select_one("div.ProductCard__badge p").text
            if item_type != "Sponsored":
                item_link = item.attrs["href"]
                trash_elems = item.select("div.ProductCard__rating,div.ProductCard__image,div.ProductCard__offers") #span[aria-hidden='true']
                if trash_elems:
                    for elem in trash_elems:
                        elem.extract()
                ls = []
                for tag in item.descendants:
                    if tag.string is not None and isinstance(tag, NavigableString) is True:
                        ls.append(tag.string)
                promo = " ".join(ls)
                promo_list.append((promo,item_link))

        promo_list = self.__clean_data(promo_list, "sale")
        return promo_list

    def __get_ulta_promos(self, sale_type: str) -> list[str]:
        """
        Returns a list of ulta promos from a category
        Args: "gwp", "td", "bmsm
        """

        match sale_type:
            case sale if sale in ["gwp","bmsm"]:
                if sale == "gwp":
                    url = "https://www.ulta.com/promotion/gift-with-purchase"
                if sale == "bmsm":
                    url = "https://www.ulta.com/promotion/buy-more-save-more"

                soup = self.__get_ulta_soup(url)
                promo_list = []
                items = soup.select("li.PromotionListingResults__compactDealCard div.CompactDealCard__gwpLine")
                for item in items:
                    ls = []
                    for tag in item.descendants:
                        if tag.string is not None and isinstance(tag, NavigableString) is True:
                            ls.append(tag.string)
                    promo = " ".join(ls)
                    promo_list.append(promo)

                promo_list = self.__clean_data(promo_list, "promo")
                return promo_list

            case "td":
                url = "https://www.ulta.com/promotion/all"

                soup = self.__get_ulta_soup(url)
                promo_list = []
                items = soup.select("div.LargeDealRail__itemclass div.LargeDealCard__textContent")
                for item in items:
                    try:
                        item.find("div.LargeDealCard__actions").extract()
                    except AttributeError:
                        pass
                    ls = []
                    for tag in item.descendants:
                        if tag.string is not None and isinstance(tag, NavigableString) is True:
                            ls.append(tag.string)
                    promo = " ".join(ls)
                    promo_list.append(promo)

                    promo_list = self.__clean_data(promo_list, "promo")
                    return promo_list

    def get_all_data(self):
        """Returns all promos as a string"""
        try:
            sale_urls = ["https://www.ulta.com/promotion/sale?category=makeup", "https://www.ulta.com/promotion/sale?category=skin-care", "https://www.ulta.com/promotion/sale?category=hair"]
            ulta_sales_list = list(map(self.__get_ulta_sales, sale_urls))
            flattened_list = [item for sublist in ulta_sales_list for item in sublist]
            formatted_list = [f"{item[0]}: {item[1]}" for item in flattened_list]
            ulta_sales = ' , '.join(formatted_list)
            
            promo_list = [(self.__get_ulta_promos("gwp")), self.__get_ulta_promos("td"), self.__get_ulta_promos("bmsm")]

            str_ls = [" , ".join(promo) for promo in promo_list if promo is not None]
            ulta_gwp_str = " , ".join(str_ls)
            return f"Ulta Sales: ({ulta_sales})\n\nUlta GWP: ({ulta_gwp_str})"

        except (MaxRetryError, AttributeError) as exc:
            raise RuntimeError("Issue with beauiful soup instance") from exc
