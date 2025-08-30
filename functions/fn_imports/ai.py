"""Module to connect to gemini API"""
import logging, os, re, json, io
from google import genai
from google.genai import types
import cloud_storage

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

    def upload_file(self, file_bytes_io: io.BytesIO) -> str:
        client = genai.Client()
        try:
            uploaded_file = client.files.upload(
                file=file_bytes_io,
            )
            return uploaded_file.uri
        
        except Exception as e:
            print(f"Error uploading file to Gemini File API: {e}")
            return None

    def get_pref_deals(self, query: tuple[str] | str) -> dict:
        """
        Queries the AI for preference based sales or current best sales
        uri: str
        query: tuple for preferred_deals or str for todays_deals
        """
        uri = cloud_storage.get_uri()
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_text(text=f'Recommend three each of makeup, skincare, and haircare products for a person with {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look. Respond with the product id and a brief explanation of why each product is a good fit.'),
                types.Part.from_uri(file_uri=uri)
            ],
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.pref_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="""You are a beauty product recommender.
                        Use only the fields provided: product_id, reason_to_buy. Do not fetch or invent data.  
                        Output valid JSON matching the schema. Always return 3 items per category; if no perfect match, choose the best available and explain why.  

                        Evidence:  
                        - Actives if named or with clear synonyms are highest tier evidence: salicylic/BHA = acne, benzoyl peroxide = acne, retinol/retinal = anti-aging/acne, niacinamide = oil/redness/pigmentation, azelaic acid = acne/redness, vitamin C/ascorbic = pigmentation/anti-aging, hyaluronic/HA = dehydration, ceramides = dryness/barrier, SPF ## = suncare.  
                        - Marketing cues (hydrating, plumping, brightening, clarifying, soothing, barrier) are lower tier evidence.  

                        Ranking:  
                        1. Direct active match  
                        2. Synonym match  
                        3. Marketing descriptor  
                        Tie-breakers: higher discount percentage, then lower sale price.  
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

    def get_top_deals(self) -> dict:
        """
        Queries the AI for the top 10 best deals
        """
        uri = cloud_storage.get_uri()
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_text(text='Identify the **top 10 best deals** on beauty products from the provided list. Combine the promotions with discounts to get the maximum value for each purchase. Respond with the product id and a brief explanation of why each product provides good value.'),
                types.Part.from_uri(file_uri=uri)
            ],
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.td_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="""
                    You are a beauty deal analyzer. Output valid JSON matching the provided schema. Do not fetch or invent data. Be concise and factual; never invent product details. Always return 10 items. If there are no good deals, choose the next best available deals and explain why.
                    """
            ))
            clean_response = self.clean_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"
        except json.JSONDecodeError:
            return json.loads(response.text)

        
x = AiBot()
uri = "https://generativelanguage.googleapis.com/v1beta/files/ce3fy1afv43r"
