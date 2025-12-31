"""Integration test module"""
import os, pytest, json
from jsonschema import validate, ValidationError
from google import genai
from dotenv import load_dotenv
from fn_imports.ai import AiBot

load_dotenv() 

@pytest.fixture
def promos():
    with open("local.test_promos.txt","r", encoding="utf-8") as file:
        promos = file.read()
    return promos

def load_json_schema(schema_path):
    with open(schema_path, 'r') as f:
        return json.load(f)

pref_schema = load_json_schema("schemas/pref_schema.json")
td_schema = load_json_schema("schemas/td_schema.json")

@pytest.fixture
def ai_bot():
    return AiBot()

def test_generate_prefs_works(ai_bot, promos):
    test_query = ("dry","acne and/or dark spots", "straight", "damaged and/or frizzy", "light/daily")
    resp = ai_bot.get_pref_deals(test_query, TEST_PROMOS=promos)
    try:
        data = json.loads(resp)
    except json.JSONDecodeError:
        raise
    validate(instance=data, schema=pref_schema)
    assert "product_sku" in data["makeup"][0]
    assert "reason_to_buy" in data["makeup"][0]

def test_generate_td_works(ai_bot, promos):
    resp = ai_bot.get_top_deals(TEST_PROMOS=promos)
    try:
        data = json.loads(resp)
    except json.JSONDecodeError:
        raise
    validate(instance=data, schema=td_schema)
    assert isinstance(data, list)
    assert "product_sku" in data[0]
    assert "reason_to_buy" in data[0]




