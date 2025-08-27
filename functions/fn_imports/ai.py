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

    def generate_uri(self, json_str) -> str:
        client = genai.Client()
        f = client.files.upload_bytes(content=json_str.encode("utf-8"), mime_type="application/json")
        return f.uri

    def get_pref_deals(self, uri: str, query: tuple[str] | str) -> dict:
        """
        Queries the AI for preference based sales or current best sales
        promos: str
        query: tuple for preferred_deals or str for todays_deals
        """
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
            model=self.model,
            contents=[{"role":"user","parts":[
                {"text": f"Use only the attached JSON file to recommend the **top 3 makeup, skincare, and haircare items** from these products for someone who has {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look."},
                {"file_data": {"file_uri": uri, "mime_type": "application/json"}}
            ]}],
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.pref_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="""You are a beauty product recommender.
                        Use only the fields provided: product_name, product_link, product_original_price, product_sale_price, product_relevance_for_customer. Do not fetch or invent data.  
                        Output valid JSON matching the schema: 3 items each in makeup, skincare, hair. Always return 3 items per category; if no perfect match, choose the best available and explain why.  

                        Evidence:  
                        - Actives if named or with clear synonyms: salicylic/BHA = acne, benzoyl peroxide = acne, retinol/retinal = anti-aging/acne, niacinamide = oil/redness/pigmentation, azelaic acid = acne/redness, vitamin C/ascorbic = pigmentation/anti-aging, hyaluronic/HA = dehydration, ceramides = dryness/barrier, SPF ## = suncare.  
                        - Marketing cues (hydrating, plumping, brightening, clarifying, soothing, barrier) are weak evidence.  

                        Ranking:  
                        1. Direct active match  
                        2. Synonym match  
                        3. Marketing descriptor  
                        Tie-breakers: higher discount percentage, then lower sale price.  

                        For each product fill:  
                        - product_name: copy from input  
                        - product_relevance_for_customer: short sentence quoting evidence from name  
                        - product_link: copy from input
                        - product_original_price: copy from input  
                        - product_sale_price: copy from input  

                        """
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

    def get_top_deals(self, uri: str) -> dict:
        """
        Queries the AI for the top 10 best deals
        """
        client = genai.Client(api_key=self.api_key)
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
            model=self.model,
            contents=[{"role":"user","parts":[
                {"text": f"Use only the attached JSON file to identify the **top 10 best deals** on beauty products from the provided deals, gifts with purchase, and discounts."},
                {"file_data": {"file_uri": uri, "mime_type": "application/json"}}
            ]}],
            
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.td_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="""
                    You are a beauty deal analyzer.

                    Use only the fields provided: product_name, product_link, product_original_price, product_sale_price. Do not fetch or invent data.  
                    Output valid JSON matching the schema: an array of 10 items under "deals". Always return 10 items; if no perfect deal, choose the best available.  

                    For each item fill:  
                    - product_name: copy from input  
                    - product_link: copy from input  
                    - product_original_price: copy from input  
                    - product_sale_price: copy from input  
                    - deal_analysis: one short sentence explaining why this is a good deal, quoting evidence from name or discount (e.g. percent off, large saving, popular active).  

                    Ranking preference: higher discount percentage first, then lower sale price.  
                    Be concise and factual; never invent product details.  

                    """
            ))
            clean_response = self.clean_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"
        except json.JSONDecodeError:
            return json.loads(response.text) 
        
