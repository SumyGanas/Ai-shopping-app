"""Module to connect to gemini API"""
import os
import logging
import google.generativeai as genai


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AiBot():
    """Bot"""
    def __init__(self):
        api_key = os.environ.get('API_KEY')
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        genai.configure(api_key=api_key)

    def get_best_deals(self, query: tuple[str], promos: str):
        """Returns the top 10 best deals based on provided preferences and a list of promotions"""

        pref = f"a customer who has {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look"

        prompt = f"You are an expert at recommending beauty products to customers based on their needs. Identify the best makeup, skincare and haircare products across Ulta and Beauty Bay based on {pref}. List the top 10. Here are the current promotions at both: {promos}"

        response = self.model.generate_content(prompt)
        logger.info(response.usage_metadata)

        return response.text

    def current_best_deals(self, promos):
        """Returns the top 10 current best deals when given a list of pomotions"""

        prompt = f"You are given a bunch of promotions at Ulta and Beauty Bay. Identify the top 10 best deals based on value, savings and gifts with purchase. Promotions: {promos}"

        response = self.model.generate_content(prompt)
        logger.info(response.usage_metadata)

        return response.text
