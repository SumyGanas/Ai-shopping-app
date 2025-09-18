"""AI Module to connect to gemini API"""
import logging, os, json
import tolerantjson as tjson
from google import genai
from pydantic import BaseModel, ConfigDict, RootModel
from google.genai import types
from . import cloud_storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = ConfigDict(arbitrary_types_allowed=True)

class Product(BaseModel):
    product_sku: str
    reason_to_buy: str

class PrefProducts(RootModel[list[Product]]):
    model_config = config

class Preferences_Schema(BaseModel):
    makeup: PrefProducts
    skincare: PrefProducts
    haircare: PrefProducts
    model_config = config

class TodaysDeals_Schema(RootModel[list[Product]]):
    model_config = config

class AiBot(): 
    """Bot"""
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model = "gemini-2.5-flash"

    def __validate_json(self, text) -> str:
        """
        Validates the AI response's json schema
        """
        try:
            python_dict = tjson.tolerate(text)
            valid_json = json.dumps(python_dict)
            return valid_json
        except tjson.parser.ParseError as e:
            logger.error(f"Error compiling response to json string: {e}")
        except (ValueError, SyntaxError) as e:
            logger.error(f"Error cleaning json response from AI: {e}")

    def get_pref_deals(self, query: tuple[str] | str, TEST_PROMPT=None, TEST_FILE=None, TEST_PROMOS=None) -> str:
        """
        Queries the AI for preference based sales or current best sales\n
        Args:
        - query: tuple for preferred_deals or str for todays_deals
        """
        
        prompt = TEST_PROMPT or f"""Using the provided file of deals and the evidence, recommend three each of makeup, skincare, and haircare products for a person with the given concerns. Return the product id and a brief explanation of why each product is suitable. Do not hallucinate or invent products or product ids that don't exist in the data. Output valid JSON matching the schema 
        - Evidence: Named active ingredients (retinol etc.) or their synonyms are highest tier evidence. Marketing cues (hydrating, clarifying, barrier, etc.) are lower tier evidence.
        - Concerns: {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look
        """ 
        client = genai.Client(api_key=self.api_key)
        promos = TEST_PROMOS or cloud_storage.read_promos()

        with open("tmp.txt", "w") as file:
            file.write(promos)

        myfile = TEST_FILE or client.files.upload(file="tmp.txt")
        
        contents = [prompt, myfile]
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash", contents=contents,
            config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema= Preferences_Schema,
            system_instruction="""You are an expert in reccomending beauty products for specific concerns."""
             ))
            
            clean_response =  self.__validate_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"

    def get_top_deals(self, TEST_PROMPT=None, TEST_FILE=None, TEST_PROMOS=None) -> str:
        """
        Queries the AI for the top 10 best deals\n
        Args:
        - None
        """
        prompt = TEST_PROMPT or f"""Identify the **top 10 best deals** on beauty products from the provided data. Respond with the product id and a brief explanation of why each product provides good value. Output valid JSON matching the provided schema. Avoid echoing the product name in the reason to buy. **Do not hallucinate or invent products or product ids that don't exist in the data.** Never invent product details. Always return exactly 10 distinct items."""
        client = genai.Client(api_key=self.api_key)
        promos = TEST_PROMOS or cloud_storage.read_promos()

        with open("tmp.txt", "w") as file:
            file.write(promos)

        myfile = TEST_FILE or client.files.upload(file="tmp.txt")
        contents =  [prompt, myfile]
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash", contents=contents,
            config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema= TodaysDeals_Schema,
            system_instruction="""You are an expert deal analyzer that can combine different promotions and discounts to get the maximum value in a purchase."""
             ))
            clean_response = self.__validate_json(response.text)
            return clean_response
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"