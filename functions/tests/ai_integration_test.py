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

@pytest.fixture
def ai_bot():
    return AiBot()

def test_get_pref_deals():
    query = ("oily", "sensitive", "curly", "long", "natural")
    return ai_bot.get_pref_deals(promos, query)

def test_get_top_deals():
    return ai_bot.get_top_deals()

def test_validate_pref_deals(gemini_prefs_response):
    if not isinstance(gemini_prefs_response,object):
        pytest.fail("Prefs response type is not an object")

def test_validate_top_deals(gemini_deals_response):
    if not isinstance(gemini_deals_response,object):
        pytest.fail("Deals response type is not an object")

def test_validate_pref_deals_schema(gemini_prefs_response):
    try:
        validate(instance=gemini_prefs_response, schema=ai_bot.pref_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")

def test_validate_top_deals_schema(gemini_deals_response):
    try:
        validate(instance=gemini_deals_response, schema=ai_bot.td_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")

@pytest.mark.jsontest
def test_extract_valid_raw_json():
    raw = '{"foo": "bar", "baz": 42}'
    result = ai_bot.clean_json(raw)
    assert result == {"foo": "bar", "baz": 42}

@pytest.mark.jsontest
def test_extract_json_from_markdown():
    wrapped = '''```json
{
  "foo": "bar",
  "baz": 42
}
```'''
    result = ai_bot.clean_json(wrapped)
    assert result == {"foo": "bar", "baz": 42}

@pytest.mark.jsontest
def test_json_from_markdown_block_without_language():
    wrapped = '''```
{
  "foo": "bar"
}
```'''
    result = ai_bot.clean_json(wrapped)
    assert result == {"foo": "bar"}

@pytest.mark.jsontest
def test_raises_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        ai_bot.clean_json("not a json string")

@pytest.mark.jsontest
def test_raises_on_markdown_invalid_json():
    bad = '''```json
this is not valid
```'''
    with pytest.raises(json.JSONDecodeError):
        ai_bot.clean_json(bad)