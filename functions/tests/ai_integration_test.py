"""Integration tests"""
import os
import json
import pytest
from jsonschema import validate, ValidationError
import google.generativeai as genai

with open("./test_promos.txt","r", encoding="utf-8") as file:
    promos = file.read()

prefs_schema = {
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

deals_schema = {
            "type": "object",
            "deals": {
                "type": "array",
                "minItems":10,
                "maxItems":10,
                "properties": {
                    "product_name": {"type": "string"},
                    "product_link": {"type": "string"},
                    "product_original_price": {"type": "string"},
                    "product_sale_price": {"type": "string"},
                    "deal_analysis": {"type": "string"}
                },
                "required": ["product_name", "product_link", "product_original_price", "product_sale_price", "deal_analysis"]
            },
            "required": ["deals"]
        }

def make_gemini_request(prompt, model_name="gemini-1.5-flash"):
    """Makes a request to the Gemini API and returns the JSON response."""
    model = genai.GenerativeModel(model_name, generation_config={
        "response_mime_type": "application/json",
    })
    genai.configure(api_key=os.environ.get('API_KEY'))
    response = model.generate_content(prompt)
    return json.loads(response.text)

@pytest.fixture
def gemini_prefs_response():
    """Prompt based on user query and promotions"""
    query = ["oily", "sensitive", "curly", "long", "natural"]
    pref = f"a customer who has {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look"
    prompt = f"As a beauty expert, recommend the top 3 products from the categories makeup, skincare, and haircare from Ulta for {pref}. Use the given list of discounts and promotions: ({promos}). For each category, provide: products' names, why each product is relevant for the customer's preferences, products' link, original prices, and sale prices excluding kit and value prices. Use the json schema: {prefs_schema}"
    
    return make_gemini_request(prompt)

@pytest.fixture
def gemini_deals_response():
    """Prompt based on deals"""
    prompt = f"As a savings expert, identify the top 10 best deals from the provided list of promotions: {promos}. Analyze the discounts excluding kit prices and value prices, gifts with purchase, and other promotions to find a brief reason why this deal is worth purchasing. Also provide the original and sale prices, and the product link. Use the json schema: {deals_schema}"
    
    return make_gemini_request(prompt)

def test_valid_prefs_type(gemini_prefs_response):
    """Validate pref response type"""
    if not isinstance(gemini_prefs_response,object):
        pytest.fail("Prefs response type is not an object")

def test_valid_deals_type(gemini_deals_response):
    """Validate deals response type"""
    if not isinstance(gemini_deals_response,object):
        pytest.fail("Deals response type is not an object")

def test_valid_prefs_schema(gemini_prefs_response):
    """Validating prompt response"""
    try:
        validate(instance=gemini_prefs_response, schema=prefs_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")

def test_valid_deals_schema(gemini_deals_response):
    """Validating prompt response"""
    try:
        validate(instance=gemini_deals_response, schema=deals_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")
