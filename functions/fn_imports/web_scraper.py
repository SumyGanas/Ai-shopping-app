"""Parser bot"""
import re
import unicodedata
import requests
import time
from bs4 import BeautifulSoup, NavigableString
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from urllib3.exceptions import MaxRetryError

class DealGenerator():
    """Contains methods to assist scraping brand pages"""
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("media.peerconnection.enabled", False)
        options.set_preference("privacy.trackingprotection.enabled", True)
        options.set_preference("dom.webnotifications.enabled", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        self.driver = webdriver.Firefox(options=options)

    def get_ulta_soup_bs(self, url:str) -> BeautifulSoup:
        """Ulta Soup"""
        try:
            self.driver.get(url)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(2)
        except TimeoutException as exc:
            self.driver.quit()
            raise RuntimeError("Timeout continues") from exc
        try:
            alert_button = self.driver.find_element(By.XPATH, "/html/body/div[7]/div[3]/div/div/div[3]/button")
            alert_button.click()
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        try:
            footer = self.driver.find_element(By.CSS_SELECTOR, "footer.Footer")
            self.driver.execute_script("arguments[0].scrollIntoView();", footer)
            time.sleep(1)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        finally:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    def get_ulta_soup(self, url) -> BeautifulSoup:
        """Ulta soup using just bs4"""
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def get_beautybay_soup_bs(self, url) -> BeautifulSoup:
        """Beauty Bay soup"""
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(2)
        except TimeoutException as exc:
            self.driver.quit()
            raise RuntimeError("Timeout continues") from exc
        try:
            alert_button = (By.XPATH, "/html/body/div[1]/div[1]/div/span/div[2]/button")
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(alert_button)).click()
        except (StaleElementReferenceException, TimeoutException):
            pass
        try:
            footer = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, "footer")))
            self.driver.execute_script("arguments[0].scrollIntoView();", footer)
            time.sleep(1)
        except (TimeoutException, StaleElementReferenceException):
            pass
        finally:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup
    
    def get_beautybay_soup(self, url) -> BeautifulSoup:
        """beautybasy soup with bs4"""
        page = requests.get(url, timeout=5)
        time.sleep(3)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def clean_data(self, deals: list[str]) -> list[str]:
        """Cleans and normalizes data"""
        clean_list = []
        for deal in deals:
            stripped_deal = deal.lower().strip()
            normalized_deal = unicodedata.normalize('NFKD', stripped_deal)
            reg = re.sub(r'[!"#%&\'()*+,\-/:;<=>?@[\\\]^_`{|}~]', '', normalized_deal)
            clean_deal = re.sub(r'\s+', ' ', reg).strip()

            clean_list.append(clean_deal)

        return clean_list

    def get_beautybay_promos(self, item_type: str) -> list:
        """
        Returns a list of beautybay promos from a category
        Args: "makeup", "skincare", "hair", "gwp
        """
        #Sales
        match item_type:
            case "makeup":
                url = "https://www.beautybay.com/l/sale/?f_filter_category=Makeup"
            case "skincare":
                url = "https://www.beautybay.com/l/sale/?f_filter_category=Skincare"
            case "hair":
                url = "https://www.beautybay.com/l/sale/?f_filter_category=Haircare"
            case "gwp":
                url = "https://www.beautybay.com/l/beauty-bay-offers/"
                soup = self.get_beautybay_soup(url)
                sale_items = soup.select("article")
                promo_list = []
                for item in sale_items:
                    ls = []
                    item.select_one("div").extract()
                    for tag in item.descendants:
                        if tag.string is not None and isinstance(tag, NavigableString) is True:
                            ls.append(tag.string)
                    promo = " ".join(ls)
                    promo_list.append(promo)

                promo_list = self.clean_data(promo_list)
                return promo_list

        soup = self.get_beautybay_soup(url)
        sale_items = soup.select("div.lister-tile-container")
        promo_list = []
        for idx, item in enumerate(sale_items):
            ls = []
            trash_elems = item.select("div.product-rating,div.image-wrapper,div.media-container, div.button-container")
            if trash_elems:
                for elem in trash_elems:
                    elem.extract()
            for tag in item.descendants:
                if tag.string is not None and isinstance(tag, NavigableString) is True:
                    ls.append(tag.string)
            promo = " ".join(ls)
            promo_list.append(promo)
            if idx >= 20:
                break

        promo_list = self.clean_data(promo_list)
        return promo_list


    def get_ulta_promos(self, sale_type: str) -> list[str]:
        """
        Returns a list of ulta promos from a category
        Args: "makeup", "skincare", "hair", "gwp", "td"
        """

        match sale_type:
            case "makeup":
                url = "https://www.ulta.com/promotion/sale?category=makeup"
            case "skincare":
                url = "https://www.ulta.com/promotion/sale?category=skin-care"
            case "hair":
                url = "https://www.ulta.com/promotion/sale?category=hair"
            case sale if sale in ["gwp","bmsm"]:
                if sale == "gwp":
                    url = "https://www.ulta.com/promotion/gift-with-purchase"
                if sale == "bmsm":
                    url = "https://www.ulta.com/promotion/buy-more-save-more"

                soup = self.get_ulta_soup(url)
                promo_list = []
                items = soup.select("li.PromotionListingResults__compactDealCard div.CompactDealCard__gwpLine")
                for item in items:
                    ls = []
                    for tag in item.descendants:
                        if tag.string is not None and isinstance(tag, NavigableString) is True:
                            ls.append(tag.string)
                    promo = " ".join(ls)
                    promo_list.append(promo)

                promo_list = self.clean_data(promo_list)
                return promo_list

            case "td":
                url = "https://www.ulta.com/promotion/all"

                soup = self.get_ulta_soup(url)
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

                    promo_list = self.clean_data(promo_list)
                    return promo_list

        soup = self.get_ulta_soup(url)
        promo_list = []
        items = soup.select("li.ProductListingResults__productCard a")
        for idx,item in enumerate(items):
            item_type = item.select_one("div.ProductCard__badge p").text
            if item_type != "Sponsored":
                trash_elems = item.select("div.ProductCard__rating,div.ProductCard__image,div.ProductCard__offers,span[aria-hidden='true']")
                if trash_elems:
                    for elem in trash_elems:
                        elem.extract()
                ls = []
                for tag in item.descendants:
                    if tag.string is not None and isinstance(tag, NavigableString) is True:
                        ls.append(tag.string)
                promo = " ".join(ls)
                promo_list.append(promo)
            if idx >= 20:
                break

        promo_list = self.clean_data(promo_list)
        return promo_list

    def get_all_data(self):
        """Writes the promos to a file for the AI cache"""
        #Sales
        try:
            ulta_sales = self.get_ulta_promos("makeup") + self.get_ulta_promos("skincare") + self.get_ulta_promos("hair")
            ulta_gwp_promos = self.get_ulta_promos("gwp") + self.get_ulta_promos("td") + self.get_ulta_promos("bmsm")

            beautybay_sales = self.get_beautybay_promos("makeup") + self.get_beautybay_promos("skincare") + self.get_beautybay_promos("hair")
            beautybay_gwp_promos = self.get_beautybay_promos("gwp")

        except (MaxRetryError, ElementClickInterceptedException, AttributeError, NoSuchElementException) as exc:
            self.driver.quit()
            raise RuntimeError("Issue with webdriver instance") from exc

        finally:
            self.driver.quit()

        ulta_str = " , ".join(ulta_sales)
        bb_str = " , ".join(beautybay_sales)

        ulta_gwp_str = " , ".join(ulta_gwp_promos)
        bb_gwp_str = " , ".join(beautybay_gwp_promos)

        return f"Ulta Sales: ({ulta_str})\n\nUlta GWP: ({ulta_gwp_str})\n\nBeauty Bay Sales: ({bb_str})\n\nBeauty Bay GWP: ({bb_gwp_str})"

d = DealGenerator()
p = d.get_beautybay_promos("makeup")
c = d.get_beautybay_promos("gwp")
print(p, "\n\n", c)
