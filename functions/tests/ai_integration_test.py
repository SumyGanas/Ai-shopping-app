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

@pytest.fixture
def promos():
    with open("./test_promos.txt","r", encoding="utf-8") as file:
        promos = file.read()
    return promos

@pytest.fixture
def ai_bot():
    return AiBot()

def test_generate_content_works(ai_bot):
    client = genai.Client(api_key=ai_bot.api_key)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Knock knock",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                max_output_tokens=3
            ),
        )
        assert response is not None
    except Exception:
        pytest.fail("generate_content() raised an exception unexpectedly.")

@pytest.fixture
def pref_deals(ai_bot, promos):
    query = ("oily", "sensitive", "curly", "long", "natural")
    return ai_bot.get_pref_deals(promos, query)

@pytest.fixture
def top_deals(ai_bot):
    return ai_bot.get_top_deals()

def test_pref_deals_is_dict(pref_deals):
    assert isinstance(pref_deals, dict), "pref_deals is not a dict"

def test_top_deals_is_dict(top_deals):
    assert isinstance(top_deals, dict), "top_deals is not a dict"

def test_validate_pref_deals_schema(pref_deals, ai_bot):
    try:
        validate(instance=pref_deals, schema=ai_bot.pref_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")

def test_validate_top_deals_schema(top_deals, ai_bot):
    try:
        validate(instance=top_deals, schema=ai_bot.td_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")

@pytest.mark.jsontest
def test_extract_valid_raw_json(ai_bot):
    raw = '{"foo": "bar", "baz": 42}'
    result = ai_bot.clean_json(raw)
    assert result == {"foo": "bar", "baz": 42}

@pytest.mark.jsontest
def test_extract_json_from_markdown(ai_bot):
    wrapped = '''```json
{
  "foo": "bar",
  "baz": 42
}
```'''
    result = ai_bot.clean_json(wrapped)
    assert result == {"foo": "bar", "baz": 42}

@pytest.mark.jsontest
def test_json_from_markdown_block_without_language(ai_bot):
    wrapped = '''```
{
  "foo": "bar"
}
```'''
    result = ai_bot.clean_json(wrapped)
    assert result == {"foo": "bar"}

@pytest.mark.jsontest
def test_raises_on_invalid_json(ai_bot):
    with pytest.raises(json.JSONDecodeError):
        ai_bot.clean_json("not a json string")

@pytest.mark.jsontest
def test_raises_on_markdown_invalid_json(ai_bot):
    bad = '''```json
this is not valid
```'''
    with pytest.raises(json.JSONDecodeError):
        ai_bot.clean_json(bad)