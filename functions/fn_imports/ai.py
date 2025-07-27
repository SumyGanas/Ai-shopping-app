"""Module to connect to gemini API"""
import logging
import os
import json
from google import genai
from google.genai import types
from jsonschema import validate, ValidationError
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv() 

class AiBot():
    """Bot"""
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
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

    def test_ai_conn(self):
        """Testing method"""
        model = genai.GenerativeModel('gemini-1.5-pro')
        api_key = self.api_key
        genai.configure(api_key=api_key)
        prompt = "Write me a very short story about a sentient strawberry"
        response = model.generate_content(prompt)
        logger.info(response.usage_metadata)
        return response.text
    
    def test_new_conn(self):
        """New test"""
        client = genai.Client(api_key=self.api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Write me a very short story about a sentient strawberry",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
            ),
        )
        print(response.text)
        

    def get_pref_deals(self, promos: str, query: tuple[str] | str):
        """
        Queries the AI for preference based sales or current best sales
        promos: str
        query: tuple for preferred_deals or str for todays_deals
        """
        client = genai.Client()
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="List a few popular cookie recipes, and include the amounts of ingredients.",
            config={
                "response_mime_type": "application/json",
                "response_schema": self.pref_schema,
            },
        )
            logger.info(response.usage_metadata)
            return json.loads(response.text)
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"
        
        """model = genai.GenerativeModel(
            'gemini-1.5-flash',generation_config={"response_mime_type": "application/json"}
            )
        genai.configure(api_key=self.api_key)

        prompt = f"As a beauty expert, recommend the top 3 products from each of the categories: makeup, skincare, and haircare from Ulta for a customer who has {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look. Use the given list of discounts and promotions: ({promos}). For each category, provide the following details for each product: product name, why each product is relevant for the customer's preferences, product link, original price, and sale price. Do not include price in the reason for relevancy. Do not include kit and value prices in your analysis. Return the recommendations with the given JSON schema: {self.pref_schema}."

        try:
            response = model.generate_content(prompt)
            logger.info(response.usage_metadata)

            return json.loads(response.text)

        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"""

    def get_top_deals(self, promos: str):
        """
        Queries the AI for the top 10 best deals
        """
        """api_key = self.api_key
        model = genai.GenerativeModel(
            'gemini-1.5-pro',generation_config={"response_mime_type": "application/json"}
            )
        genai.configure(api_key=api_key)

        prompt = f"As a savings expert, identify the top 10 best deals from the provided list of promotions: {promos}. For each deal, analyze discounts, gifts with purchase, and other promotions. Exclude kit prices and value prices. Provide the following details for each deal: product name, product link, original price, sale price, and a brief analysis of why the deal is worth purchasing. Return the recommendations with the given JSON schema: {self.td_schema}."

        try:
            response = model.generate_content(prompt)
            logger.info(response.usage_metadata)

            return json.loads(response.text)

        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"""
        client = genai.Client()
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
            return json.loads(response.text)
        except UnboundLocalError:
            return "Empty/incorrect prompt provided to the AI"


    def validate_response_schema(self, resp: dict, schema: str):
        """
        Validates accuracy of the AI JSON response
        schemas: "prefs", "td"
        """

        if schema == "prefs":
            expected_schema = self.pref_schema
        elif schema  == "td":
            expected_schema = self.td_schema
        else:
            return False

        try:
            validate(instance=resp, schema=expected_schema)
        except ValidationError:
            return False

        return True

