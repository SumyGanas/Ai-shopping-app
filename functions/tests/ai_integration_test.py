"""Integration tests"""
import os
import json
import pytest
from jsonschema import validate, ValidationError
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.fn_imports.ai import AiBot

load_dotenv() 
with open("./test_promos.txt","r", encoding="utf-8") as file:
    promos = file.read()

ai_bot = AiBot()

def test_gemini_prefs_response():
    """Prompt based on user query and promotions"""
    query = ("oily", "sensitive", "curly", "long", "natural")
    return ai_bot.get_pref_deals(promos, query)

def test_gemini_deals_response():
    """Prompt based on deals"""
    return ai_bot.get_top_deals()

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
        validate(instance=gemini_prefs_response, schema=ai_bot.pref_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")

def test_valid_deals_schema(gemini_deals_response):
    """Validating prompt response"""
    try:
        validate(instance=gemini_deals_response, schema=ai_bot.td_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")

@pytest.mark.json
def test_extract_valid_raw_json():
    raw = '{"foo": "bar", "baz": 42}'
    result = ai_bot.clean_json(raw)
    assert result == {"foo": "bar", "baz": 42}

@pytest.mark.json
def test_extract_json_from_markdown_block():
    wrapped = '''```json
{
  "foo": "bar",
  "baz": 42
}
```'''
    result = ai_bot.clean_json(wrapped)
    assert result == {"foo": "bar", "baz": 42}

@pytest.mark.json
def test_extract_json_from_markdown_block_without_language():
    wrapped = '''```
{
  "foo": "bar"
}
```'''
    result = ai_bot.clean_json(wrapped)
    assert result == {"foo": "bar"}

@pytest.mark.json
def test_extract_json_raises_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        ai_bot.clean_json("not a json string")

@pytest.mark.json
def test_extract_json_raises_on_markdown_invalid_json():
    bad = '''```json
this is not valid
```'''
    with pytest.raises(json.JSONDecodeError):
        ai_bot.clean_json(bad)