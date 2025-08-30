import logging, json
import firebase_admin
from firebase_admin import firestore
from datetime import datetime, timezone
import web_scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = firebase_admin.initialize_app()
db = firestore.client()

COLLECTION_NAME = "ai_data_cache"

class Product:
    def __init__(self, name, url, list_price, sale_price, discount):
        self.name = name
        self.url= url
        self.list_price = list_price
        self.sale_price = sale_price
        self.discount = discount

    @staticmethod
    def from_dict(source):
        return Product(
            name=source.get("name"),
            url=source.get("url"),
            list_price=source.get("list_price"),
            sale_price=source.get("sale_price"),
            discount=source.get("discount"),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "list_price": self.list_price,
            "sale_price": self.sale_price,
            "discount": self.discount
        }

    def __repr__(self):
        return f"Product(\
                name={self.name}, \
                url={self.url}, \
                list_price={self.list_price}, \
                sale_price={self.sale_price}\
            )"

def __find_pref_objs(resp_obj, category: str) -> list:
    """
    Finds the products from Gemini's response in the database and returns the products
    """
    ids = (str(resp_obj[category][0]["product_id"]),str(resp_obj[category][1]["product_id"]),str(resp_obj[category][2]["product_id"]))
    document_date = str(datetime.now(timezone.utc)).split()[0]
    coll_ref = db.collection("promotional_data_sale").document(document_date).collection(category)
    pref_objs = []
    for i in range(len(ids)):
        doc = coll_ref.document(ids[i]).get().to_dict()
        pref_objs.append(doc)
    return pref_objs

def __find_promo_objs(resp_obj: list[dict]):
    document_date = str(datetime.now(timezone.utc)).split()[0]
    promo_objs = []
    doc_ref = db.collection("promotional_data_gwp_bmsm_td").document(document_date)
    promos = doc_ref.get().to_dict()
    for i in range(len(resp_obj)):
        k = str(resp_obj[i]["product_id"])
        promo_objs.append(promos.get(k))

    return promo_objs

def __create_prefs_obj(resp_obj, category) -> list[dict]:
    products = __find_pref_objs(resp_obj, category)
    product_data = []
    for i in range(len(products)):
        product_data.append(
            {
                "product_name":products[i]["name"],
                "product_relevance_for_customer":str(resp_obj[category][i]["reason_to_buy"]),
                "product_link":products[i]["url"],
                "product_original_price":products[i]["list_price"],
                "product_sale_price":products[i]["sale_price"]
            }
        )
    return product_data

def __create_promo_obj(resp_obj) -> list[dict]:
    products = __find_promo_objs(resp_obj)
    product_data = []
    for i in products:
        product_data.append(
            {
                "product_name":products[i]["name"],
                "product_relevance_for_customer":str(resp_obj[i]["deal_analysis"]),
                "product_link":products[i]["url"],
                "product_original_price":products[i]["list_price"],
                "product_sale_price":products[i]["sale_price"]
            }
        )
    return product_data

def __add_sale(collection_name: str, product_id_sku, name, url, list_price, sale_price, discount):
    """
    Add discount data to the firestore promotional_data_sale collection
    """
    document_date = str(datetime.now(timezone.utc)).split()[0]
    doc_ref = db.collection("promotional_data_sale").document(document_date)
    product = Product(name=name, url=url, list_price=list_price, sale_price=sale_price, discount=discount)
    doc_ref.collection(collection_name).document(product_id_sku).set(product.to_dict())

def __add_promotion(promotion_id, promotion_details):
    """
    Add promotional data to the firestore promotional_data_gwp_bmsm_td collection
    """
    document_date = str(datetime.now(timezone.utc)).split()[0]
    doc_ref = db.collection("promotional_data_gwp_bmsm_td").document(document_date)
    data = {
        str(promotion_id): promotion_details
    }
    doc_ref.set(data, merge=True)

def __format_sale_data(category) -> list:
    x = web_scraper.DealGenerator()
    sales = x.get_sale_data(category)
    s = []
    for i,item in enumerate(sales):
        __add_sale(category,item[i]["id"],item[i]["name"],item[i]["url"],item[i]["list_price"],item[i]["sale_price"],item[i]["discount"])
        promo = {
            "id": item[i]["id"],
            "name": item[i]["name"],
            "discount_percent":item[i]["discount"]
        }
        s.append(promo)
    return s

def create_sale_data() -> str:
    discount = {"discounts":{
        "makeup_discounts":__format_sale_data("makeup"),
        "skincare_discounts":__format_sale_data("skincare"),
        "haircare_discounts":__format_sale_data("haircare")
        }
    }

    discounts = json.dumps(discount, ensure_ascii=False, separators=(',', ':'))
    return discounts

def create_promotional_data() -> str:
    x = web_scraper.DealGenerator()
    promotions = x.get_promotional_data()
    pl = []
    for i, item in enumerate(promotions):
        __add_promotion(i, item)
        promo = {
            "id": i,
            "promotion": item
        }
        pl.append(promo)
    p = {
        "promotions": pl
        }
    promos = json.dumps(p, ensure_ascii=False, separators=(',', ':'))
    return promos

def check_if_cached(query: str):
    """
    checks if ai response data is cached in database.
    Returns data if true, or stores it and returns it if false.
    """
    document_date = str(datetime.now(timezone.utc)).split()[0]
    doc_ref = db.collection(COLLECTION_NAME).document(document_date)
    doc = doc_ref.get()

    if doc.exists:
        doc_data = doc.to_dict()
        if str(query) in doc_data:
            return doc_data[str(query)]
    else:
        default_data = {
            'created_at': datetime.now(timezone.utc),
            query: {}
        }
        doc_ref.set(default_data)

    return False

def add_to_cache(deal_type: str, query: tuple[str], resp_obj):
    """
    adds new query data to the ai-response-cache
    """
    if deal_type == "todays_deals":
        deals = __create_promo_obj(resp_obj)
        document_date = str(datetime.now(timezone.utc)).split()[0]
        doc_ref = db.collection(COLLECTION_NAME).document(document_date)
        data = {
        key : {
                "todays_deals":deals
            }
        }
        doc_ref.set(data, merge=True)
    else:
        makeup_prefs = __create_prefs_obj(resp_obj, "makeup")
        skincare_prefs = __create_prefs_obj(resp_obj, "skincare")
        haircare_prefs = __create_prefs_obj(resp_obj, "haircare")

        key = str(query)
        document_date = str(datetime.now(timezone.utc)).split()[0]
        doc_ref = db.collection(COLLECTION_NAME).document(document_date)
        data = {
        key : {
                "makeup":makeup_prefs,
                "skincare":skincare_prefs,
                "haircare":haircare_prefs
            }
        }
        doc_ref.set(data, merge=True)