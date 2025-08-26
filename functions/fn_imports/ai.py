"""Module to connect to gemini API"""
import logging, os, re, json
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AiBot():
    """Bot"""
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model = "gemini-2.5-flash"
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
            model=self.model,
            contents=f"List of promos:\n{promos}\n\nExcluding deals with kit prices and value prices, recommend the **top 3 makeup, skincare, and haircare items** from these products for someone who has {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look.",
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.pref_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="You are an expert in recommending the best beauty products for specific concerns. Use only the provided product links in your response. Do not invent or suggest products that are not included in the given list. Tailor your recommendations to directly address the user’s stated beauty concerns. Respond with the product name, why each product is relevant for the customer's preferences, product ulta link, original price, and sale price."
            ))
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
            model=self.model,
            contents="List of promos:\n{promos}\n\n Identify the **top 10 best deals** on beauty products from the provided deals, gifts with purchase, and discounts.",
            
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.td_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="You are an expert in identifying good product deals and combining them to get the best value for purchase.Use only the provided product links in your response. Do not invent or suggest products that are not included in the given list. Exclude deals mentioning kit prices and value prices. Respond with the product name, product ulta link, original price, sale price, and a brief deal analysis for each deal."
            ))
            
            clean_response = self.clean_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"
        except json.JSONDecodeError:
            return json.loads(response.text) 