"""Unit test module"""
import os, json, pytest
from jsonschema import validate, ValidationError
from unittest.mock import MagicMock
from google.genai.types import GenerateContentResponse
from dotenv import load_dotenv
from fn_imports.ai import AiBot
from fn_imports import ai as ai_module

load_dotenv() 

@pytest.fixture
def promos():
    with open("../local.test_promos.txt","r", encoding="utf-8") as file:
        promos = file.read()
    return promos

@pytest.fixture
def ai_bot():
    return AiBot()

def load_json_schema(schema_path):
    with open(schema_path, 'r') as f:
        return json.load(f)

pref_schema = load_json_schema("../schemas/pref_schema.json")
td_schema = load_json_schema("../schemas/td_schema.json")


@pytest.fixture
def mock_td_client(mocker):
    """
    Fixture to mock the Gemini client with td response
    """
    client = mocker.Mock()
    response = mocker.Mock()
    response.text = json.dumps([
    {"product_sku": "123", "reason_to_buy": "Hydrating"}
])


    client.models.generate_content.return_value = response
    mocker.patch.object(ai_module.genai, "Client", return_value=client)
    mocker.patch.object(ai_module.os.environ, "get", return_value="fake_api_key")
    return client

@pytest.fixture
def mock_prefs_client(mocker):
    """
    Fixture to mock the Gemini client with prefs response
    """
    client = mocker.Mock()
    response = mocker.Mock()
    response.text = json.dumps({
        "makeup": [{"product_sku": "sku123", "reason_to_buy": "Great color"}],
        "skincare": [{"product_sku": "sku456", "reason_to_buy": "Hydrating"}],
        "haircare": [{"product_sku": "sku789", "reason_to_buy": "Adds shine"}]
    })
    client.models.generate_content.return_value = response
    mocker.patch.object(ai_module.genai, "Client", return_value=client)
    mocker.patch.object(ai_module.os.environ, "get", return_value="fake_api_key")
    return client

def test_pref_schema_matches(ai_bot, promos, mock_prefs_client):
    api_response_text = ai_bot.get_pref_deals("","Give me a beauty product in JSON format.","",promos)
    data = json.loads(api_response_text)
    validate(instance=data, schema=pref_schema)
    assert "product_sku" in data["makeup"][0]
    assert "reason_to_buy" in data["makeup"][0]

def test_td_schema_matches(ai_bot, promos, mock_td_client):
    api_response_text = ai_bot.get_top_deals("Give me a beauty product in JSON format.","", promos)
    data = json.loads(api_response_text)
    validate(instance=data, schema=td_schema)
    assert isinstance(data, list)
    assert "product_sku" in data[0]
    assert "reason_to_buy" in data[0]

@pytest.fixture
def mock_invalid_client(mocker):
    """
    Fixture to mock the Gemini client with an invalid JSON response
    """
    client = mocker.Mock()
    response = mocker.Mock()
    # Invalid: product_sku and reason_to_buy are numbers, not strings
    response.text = json.dumps([{"product_sku": 123, "reason_to_buy": 456}])
    client.models.generate_content.return_value = response
    mocker.patch("fn_imports.ai.genai.Client", return_value=client)
    mocker.patch("fn_imports.ai.os.environ.get", return_value="fake_api_key")
    return client

def test_pref_schema_with_invalid_data(ai_bot, mock_invalid_client, promos):
    with pytest.raises(ValidationError):
        api_response_text = ai_bot.get_pref_deals("","Give me a beauty product in JSON format.","",promos)
        data = json.loads(api_response_text)
        validate(instance=data, schema=pref_schema)


def test_td_schema_with_invalid_data(ai_bot, mock_invalid_client, promos):
    with pytest.raises(ValidationError):
        api_response_text = ai_bot.get_top_deals("Give me a beauty product in JSON format.","", promos)
        data = json.loads(api_response_text)
        validate(instance=data, schema=td_schema)
