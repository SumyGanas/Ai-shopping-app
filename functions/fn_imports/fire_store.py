import logging, json
import firebase_admin
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
import web_scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = firebase_admin.initialize_app()
db = firestore.client()

class Product:
    def __init__(self, sku, name, url, list_price, sale_price, discount):
        self.sku = sku
        self.name = name
        self.url= url
        self.list_price = list_price
        self.sale_price = sale_price
        self.discount = discount

    @staticmethod
    def from_dict(source):
        return Product(
            sku=source.get("sku"),
            name=source.get("name"),
            url=source.get("url"),
            list_price=source.get("list_price"),
            sale_price=source.get("sale_price"),
            discount=source.get("discount")
        )

    def to_dict(self):
        return {
            "sku": self.sku,
            "name":self.name,
            "url": self.url,
            "list_price": self.list_price,
            "sale_price": self.sale_price,
            "discount": self.discount
        }

    def __repr__(self):
        return f"Product(\
                sku={self.sku}, \
                name={self.name}, \
                url={self.url}, \
                list_price={self.list_price}, \
                sale_price={self.sale_price}\
                discount={self.discount} \
            )"

class Cache():
    def __init__(self) -> None:
        self.cache_name = "ai_data_cache"
        self.sale_collection = "promotional_data_sale"
        self.todays_date = str(datetime.now(timezone.utc)).split()[0]
    def check_if_cached(self, query: str):
        """
        checks if ai response data is cached in database.
        Returns data if true, or stores it and returns it if false.
        """
        doc_ref = db.collection(self.cache_name).document(self.todays_date)
        doc = doc_ref.get()

        if doc.exists:
            doc_data = doc.to_dict() or {}
            key = str(query)
            if key in doc_data:
                return doc_data[key]
        else:
            return False

class Cache_Handler(Cache):
    def __init__(self, response) -> None:
        super().__init__()
        self.response = response
    def __find_pref_item(self, category: str, sku: str, reason: str) -> dict:
        """
        Queries the firestore db using the skus provided by Gemini and returns product info for the relevant product
        """       
        coll_ref = db.collection(self.sale_collection
                                 ).document(self.todays_date).collection(category)
        doc_ref = coll_ref.document(sku)
        if doc_ref.get() is not None:
            doc_ref.set(
                {"product_relevance_for_customer":reason}, 
                merge=True
                )

            pref_item = doc_ref.get().to_dict()
            return pref_item
        else:
            raise firestore.error

    def __create_pref_list(self, category: str) -> list:
        """
        Builds a list of products from the response to a prefs query to be sent to the response cache
        """
        pref_list = []
        
        ls = json.loads(self.response)[category]
        for item in ls:
            sku = item["product_sku"]
            reason = item["reason_to_buy"]
            product = self.__find_pref_item(category, sku, reason)
            pref_list.append(product)
        return pref_list

    def __find_promo_items(self, category: str):
        """
        Finds the products from Gemini's response in the database in a given category and returns the products
        """
        coll_ref = db.collection(self.sale_collection
                                 ).document(self.todays_date).collection(category)
        promo_items = []
        products = json.loads(self.response)
        for product in products:
            print("\n\n\n",product,"\n\n\n")
            doc_ref = coll_ref.document(product["product_sku"])
            item = doc_ref.get().to_dict()
            if item is not None:    
                reason = product["reason_to_buy"]
                doc_ref.update(
                {"product_relevance_for_customer":reason}, 
                    )
                item = doc_ref.get().to_dict()
                promo_items.append(item)
        
        return promo_items

    def __create_promo_list(self) -> list[dict]:
        """
        Builds a list of products from the response to a td query to be sent to the response cache
        """

        makeup = self.__find_promo_items("makeup")
        skincare = self.__find_promo_items("skincare")
        haircare = self.__find_promo_items("haircare")

        promo_list = makeup+skincare+haircare
        return promo_list

    def add_to_cache(self, deal_type: str, query: tuple[str, str, str, str, str]):
        """
        adds new query data to the ai-response-cache
        """
        if deal_type == "todays_deals":
            doc_ref = db.collection(self.cache_name).document(self.todays_date)
            deals = self.__create_promo_list()
            data = {
                    "todays_deals":deals
                }

            doc_ref.set(data)
        else:
            data = {
                str(query) :
                    {"makeup": self.__create_pref_list("makeup"),
                    "skincare": self.__create_pref_list("skincare"),
                    "haircare": self.__create_pref_list("haircare")}
            }
            key = str(query)
            doc_ref = db.collection(self.cache_name).document(self.todays_date)
            
            doc_ref.set(data, merge=True)
    

class Promotions():
    def __init__(self) -> None:
        pass

   
    def __add_promotion_to_db(self, promotion_id, promotion_details):
        """
        Add a promotion and its details to firestore
        """
        document_date = str(datetime.now(timezone.utc)).split()[0]
        doc_ref = db.collection("promotional_data_gwp_bmsm_td").document(document_date)
        data = {
            str(promotion_id): promotion_details
        }
        doc_ref.set(data, merge=True)

    def __add_item_to_db(self, category, item_config: dict):
        """
        Add a sale item and its details to firestore
        """
        document_date = str(datetime.now(timezone.utc)).split()[0]
        doc_ref = db.collection("promotional_data_sale").document(document_date)
        product = Product(**item_config)
        doc_ref.collection(category).document(item_config["sku"]).set(product.to_dict())

    def __create_item_for_ai(self, item_config: dict) -> dict:
        """
        Returns a dictionary with relevant item information
        """
        sale_item = {
            "sku": item_config["sku"],
            "name": item_config["name"],
            "discount_percent": item_config["discount"]
        }
        return sale_item

    def update_sales(self) -> str:
        """
        Adds new discount data to the firestore promotional_data_sale collection and returns the discounts to add them to cloud storage
        """
        #Firestore
        scraper = web_scraper.DealGenerator()
        categories = ["makeup", "skincare", "haircare"]
        ai_product_list = []
        for category in categories:
            sales = scraper.get_sale_data(category)
            for item in sales:
                self.__add_item_to_db(category, item)
                ai_item = self.__create_item_for_ai(item)
                ai_product_list.append(ai_item)

        #Cloud Storage
        discounts = json.dumps(ai_product_list, ensure_ascii=False, separators=(',', ':'))
        return discounts

    def update_promotions(self) -> str:
        """
        Adds new promotions to the firestore promotional_data_gwp_bmsm_td collection and returns the promotions to add them to cloud storage
        """
        scraper = web_scraper.DealGenerator()
        promotions = scraper.get_promotional_data()
        ai_promo_list = []
        for i, promotion in enumerate(promotions):
            self.__add_promotion_to_db(i, promotion)
            promo = {
                "id": i,
                "promotion": promotion
            }
            ai_promo_list.append(promo)
        promos = json.dumps(ai_promo_list, ensure_ascii=False, separators=(',', ':'))
        return promos


