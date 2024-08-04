"""Module to connect to gemini API"""
import random
import time
from itertools import product
import logging
import google.generativeai as genai
#import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AiBot():
    """Bot"""
    def __init__(self):
        api_key = "AIzaSyApqVQhX0VZZaBV_Wg6mtQZB-rakgBtcKI"
        #genai.configure(api_key=os.environ["API_KEY"])
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        genai.configure(api_key=api_key)

    def get_best_deals(self, query: tuple[str], promos):
        """top 10 best deals based on preferences"""
        # promos = self.__get_promos()
        pref = f"a customer who has {query[0]} skin with {query[1]}, {query[2]} hair that is {query[3]}, and likes a {query[4]} makeup look"
        prompt = f"You are an expert at recommending beauty products to customers based on their needs. Identify the top 10 best makeup deals across Ulta and Beauty Bay based on {pref}. Here are the current promotions at both: {promos}"

        response = self.model.generate_content(prompt)
        logger.info(response.usage_metadata)

        return response.text

    def current_best_deals(self, promos):
        """Top 10 current best deals"""
        # promos = self.__get_promos()
        prompt = f"You are given a bunch of promotions at Ulta and Beauty Bay. Identify the best current deals based on value, savings and gifts with purchase. Promotions: {promos}"

        response = self.model.generate_content(prompt)
        logger.info(response.usage_metadata)

        return response.text

    def __create_permutations(self):
        """Creates and returns a list of permutations"""
        skin_types = ['Oily', 'Dry']
        skin_concerns = ['Acne and/or Dark Spots', 'Redness and/or Wrinkles']
        hair_types = ['Straight', 'Curly']
        hair_concerns = ['Damaged and/or Frizzy', 'Brittle and/or Color-treated']
        makeup_preferences = ['Light/Daily', 'Bold/Glam']

        categories = [
            skin_types,
            skin_concerns,
            hair_types,
            hair_concerns,
            makeup_preferences
        ]

        permutations = list(product(*categories))

        prefs = random.choice(permutations)
        return prefs, len(permutations)

    def __check_response_time(self, promos):
        """Check ai response time"""
        perm = self.__create_permutations()
        st = time.time()
        deals = self.get_best_deals(perm, promos)
        et = time.time()
        elapsed_time = et - st
        print(deals, "\n\n",f"Elapsed time: {elapsed_time}")

    def test(self, promos):
        """Testing private methods"""
        self.__check_response_time(promos)
