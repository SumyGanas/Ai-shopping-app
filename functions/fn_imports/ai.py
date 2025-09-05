"""Module to connect to gemini API"""
import logging, os, re, json, ast
from google import genai
from google.genai import types
from . import cloud_storage

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
                    "product_id": {"type": "string"},
                    "reason_to_buy": {"type": "string"}
                },
                "required": [
                    "product_id",
                    "reason_to_buy",
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
                    "product_id": {"type": "string"},
                    "reason_to_buy": {"type": "string"}
                },
                "required": [
                    "product_id",
                    "reason_to_buy",
                ]
            }
        },
        "haircare": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "reason_to_buy": {"type": "string"}
                },
                "required": [
                    "product_id",
                    "reason_to_buy",
                ]
            }
        }
    },
    "required": ["makeup", "skincare", "haircare"]
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
                    "product_id": {"type": "string"},
                    "deal_analysis": {"type": "string"}
                },
                "required": [
                    "product_id",
                    "deal_analysis"
                ]
            }
        }
    },
    "required": ["deals"]
}


    def get_pref_deals(self, query: tuple[str] | str) -> dict:
        """
        Queries the AI for preference based sales or current best sales
        uri: str
        query: tuple for preferred_deals or str for todays_deals
        """
        
        prompt = f"""Using the provided file of deals, recommend three each of makeup, skincare, and haircare products for a person with {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look. Respond with the product id field and a brief explanation of why each product is a good fit. Do not hallucinate or invent products or product ids that don't exist in the data. Only respond with the product_id of the chosen product and a reason to buy.Output valid JSON matching the schema. Always return 3 items per category; if no perfect match, choose the best available and explain why.  
        Evidence:  
        - Actives if named or with clear synonyms are highest tier evidence: salicylic/BHA = acne, benzoyl peroxide = acne, retinol/retinal = anti-aging/acne, niacinamide = oil/redness/pigmentation, azelaic acid = acne/redness, vitamin C/ascorbic = pigmentation/anti-aging, hyaluronic/HA = dehydration, ceramides = dryness/barrier, SPF ## = suncare.  
        - Marketing cues (hydrating, plumping, brightening, clarifying, soothing, barrier) are lower tier evidence.Ranking: Direct active match (Best), Synonym match (Better),  3. Marketing descriptor (Good), 4. Discount percentage (Okay)"""
        client = genai.Client(api_key=self.api_key)
        promos = cloud_storage.read_promos()

        with open("tmp.txt", "w") as file:
            file.write(promos)

        myfile = client.files.upload(file="tmp.txt")
        
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash", contents=[prompt, myfile],
            config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.pref_schema,
            system_instruction="""You are an expert in beauty products."""
             ))
            clean_response = self.clean_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"

    def clean_json(self, text) -> dict:
        """Clean json from markdown"""
        try:
            python_dict = ast.literal_eval(text)
            valid_json_str = json.dumps(python_dict)
            return valid_json_str
        except json.JSONDecodeError as e:
            logger.error(f"Error compiling response to json string: {e}")
        except (ValueError, SyntaxError) as e:
            logger.error(f"Error cleaning json response from AI: {e}")

    def get_top_deals(self) -> dict:
        """
        Queries the AI for the top 10 best deals
        """
        prompt = f"""Identify the **top 10 best deals** on beauty products from the provided data. Respond with the product id and a brief explanation of why each product provides good value. Output valid JSON matching the provided schema. **Do not hallucinate or invent products or product ids that don't exist in the data.** Be concise and factual; never invent product details. Always return 10 items."""
        client = genai.Client(api_key=self.api_key)
        promos = cloud_storage.read_promos()

        with open("tmp.txt", "w") as file:
            file.write(promos)

        myfile = client.files.upload(file="tmp.txt")
        
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash", contents=[prompt, myfile],
            config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.td_schema,
            system_instruction="""You are an expert deal analyzer that can combine different promotions and discounts to get the maximum value in a purchase."""
             ))
            clean_response = self.clean_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"

