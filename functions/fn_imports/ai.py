"""Module to connect to gemini API"""
import logging, os, re, json
from google import genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AiBot():
    """Bot"""
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.pref_schema = {
    "type": "object",
    "properties": {
        "makeup": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "product_relevance_for_customer": {"type": "string"},
                    "product_link": {"type": "string"},
                    "product_original_price": {"type": "string"},
                    "product_sale_price": {"type": "string"}
                },
                "required": [
                    "product_name",
                    "product_relevance_for_customer",
                    "product_link",
                    "product_original_price",
                    "product_sale_price"
                ]
            }
        },
        "skincare": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "product_relevance_for_customer": {"type": "string"},
                    "product_link": {"type": "string"},
                    "product_original_price": {"type": "string"},
                    "product_sale_price": {"type": "string"}
                },
                "required": [
                    "product_name",
                    "product_relevance_for_customer",
                    "product_link",
                    "product_original_price",
                    "product_sale_price"
                ]
            }
        },
        "hair": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "product_relevance_for_customer": {"type": "string"},
                    "product_link": {"type": "string"},
                    "product_original_price": {"type": "string"},
                    "product_sale_price": {"type": "string"}
                },
                "required": [
                    "product_name",
                    "product_relevance_for_customer",
                    "product_link",
                    "product_original_price",
                    "product_sale_price"
                ]
            }
        }
    },
    "required": ["makeup", "skincare", "hair"]
}
        self.td_schema = {
    "type": "object",
    "properties": {
        "deals": {
            "type": "array",
            "minItems": 10,
            "maxItems": 10,
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "product_link": {"type": "string"},
                    "product_original_price": {"type": "string"},
                    "product_sale_price": {"type": "string"},
                    "deal_analysis": {"type": "string"}
                },
                "required": [
                    "product_name",
                    "product_link",
                    "product_original_price",
                    "product_sale_price",
                    "deal_analysis"
                ]
            }
        }
    },
    "required": ["deals"]
}
        

    def get_pref_deals(self, promos: str, query: tuple[str] | str) -> dict:
        """
        Queries the AI for preference based sales or current best sales
        promos: str
        query: tuple for preferred_deals or str for todays_deals
        """
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"As a beauty expert, recommend the top 3 products from each of the categories: makeup, skincare, and haircare from Ulta for a customer who has {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look. Use the given list of discounts and promotions: ({promos}). For each category, provide the following details for each product: product name, why each product is relevant for the customer's preferences, product link, original price, and sale price. Do not include price in the reason for relevancy. Do not include kit and value prices in your analysis. Return the recommendations with the given JSON schema: {self.pref_schema}.",
            config={
                "response_mime_type": "application/json",
                "response_schema": self.pref_schema,
            },
        )
            logger.info(response.usage_metadata)
            clean_response = self.clean_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"
        except json.JSONDecodeError:
            return json.loads(response.text) 

    
    def clean_json(self, text) -> dict:
        """Clean json from markdown"""
        markdown_block = re.match(r"^```(?:json)?\s*\n(.+?)\n```$", text.strip(), re.DOTALL)
        if markdown_block:
            cleaned = markdown_block.group(1).strip()
        else:
            cleaned = text.strip()
        return json.loads(cleaned)


    def get_top_deals(self, promos: str) -> dict:
        """
        Queries the AI for the top 10 best deals
        """
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="As a savings expert, identify the top 10 best deals from the provided list of promotions: {promos}. For each deal, analyze discounts, gifts with purchase, and other promotions. Exclude kit prices and value prices. Provide the following details for each deal: product name, product link, original price, sale price, and a brief analysis of why the deal is worth purchasing.",
            config={
                "response_mime_type": "application/json",
                "response_schema": self.td_schema,
            },
        )
            logger.info(response.usage_metadata)
            clean_response = self.clean_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"
        except json.JSONDecodeError:
            return json.loads(response.text) 

