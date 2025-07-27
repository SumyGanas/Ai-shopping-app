"""Testing module"""
import unittest
#from functions.fn_imports import ai
from fn_imports import ai

class TestAIResponses(unittest.TestCase):
    """Testing Gemini responses"""
    def setUp(self) -> None:
        self.instance = ai.AiBot()


    def test_invalid_prefs_schema(self):
        """Testing invalid schema for preferred deals"""

        invalid_prefs_object = {
    "makeup": [
        {
            "product_name": "Laura Mercier Translucent Loose Setting Powder",
            "product_link": "https://www.example.com/product1",
            "product_original_price": "52.00",
            "product_sale_price": "48.00",
            "product_relevance_for_customer": "Great for a light makeup look, controls oil and blurs pores."
        },
        {
            "product_name": "Anastasia Beverly Hills Brow And Lash Styling Kit",
            "product_link": "https://www.example.com/product2",
            "product_original_price": "33.00",
            "product_sale_price": "29.00",
            "product_relevance_for_customer": "Includes brow gel and lash comb for a natural brow look."
        }
    ],
    "skincare": [
        {
            "product_name": "Aquaphor Lip Repair Stick SPF 30",
            "product_link": "https://www.example.com/product4",
            "product_original_price": "5.99",
            "product_sale_price": "4.99",
            "product_relevance_for_customer": "Lip balm with SPF 30 protection for dry lips."
        },
        {
            "product_name": "Neutrogena Hydro Boost Moisturizer",
            "product_link": "https://www.example.com/product5",
            "product_original_price": "26.99",
            "product_sale_price": "20.24",
            "product_relevance_for_customer": "Lightweight moisturizer for dry skin, reduces fine lines."
        },
        {
            "product_name": "Beautystat Universal C Skin Refiner",
            "product_link": "https://www.example.com/product6",
            "product_original_price": "125.00",
            "product_sale_price": "59.50",
            "product_relevance_for_customer": "Brightening serum for dry skin with redness."
        }
    ],
    "hair": [
        {
            "product_name": "Bondi Boost Rapid Repair Conditioner",
            "product_link": "https://www.example.com/product7",
            "product_original_price": "30.00",
            "product_sale_price": "12.00",
            "product_relevance_for_customer": "Repairs damaged hair, strengthens and prevents breakage."
        },
        {
            "product_name": "Drybar Detox Sensitive Scalp Dry Shampoo",
            "product_link": "https://www.example.com/product8",
            "product_original_price": "28.00",
            "product_sale_price": 19.60,
            "product_relevance_for_customer": "Absorbs oil, refreshes hair without stripping natural oils."
        },
        {
            "product_name": "Drybar Reserve Ultralight Blowdryer",
            "product_link": "https://www.example.com/product9",
            "product_original_price": "285.00",
            "product_sale_price": "199.50",
            "product_relevance_for_customer": "Lightweight, powerful blowdryer for frizz-prone hair."
        },
        {
            "product_name": "Extra Product",
            "product_link": "https://www.example.com/product10",
            "product_original_price": "50.00",
            "product_sale_price": "35.00",
            "product_relevance_for_customer": "Not required in this category."
        }
    ]
}

        result2 = self.instance.validate_response_schema(invalid_prefs_object, "prefs")
        self.assertFalse(result2)


    def test_valid_pref_schema(self):
        """Testing valid schema for preferred deals"""

        valid_prefs_object = {
    "makeup": [
        {
            "product_name": "Laura Mercier Translucent Loose Setting Powder",
            "product_relevance_for_customer": "Ideal for setting makeup with a matte finish.",
            "product_link": "https://www.ulta.com/p/translucent-loose-setting-powder",
            "product_original_price": "38.00",
            "product_sale_price": "34.00"
        },
        {
            "product_name": "Fenty Beauty Pro Filt'r Soft Matte Longwear Foundation",
            "product_relevance_for_customer": "Long-lasting foundation with a natural matte finish.",
            "product_link": "https://www.ulta.com/p/pro-filtr-soft-matte-longwear-foundation",
            "product_original_price": "36.00",
            "product_sale_price": "30.00"
        },
        {
            "product_name": "Urban Decay All Nighter Setting Spray",
            "product_relevance_for_customer": "Helps makeup last all day with a weightless feel.",
            "product_link": "https://www.ulta.com/p/all-nighter-setting-spray",
            "product_original_price": "33.00",
            "product_sale_price": "29.00"
        }
    ],
    "skincare": [
        {
            "product_name": "Neutrogena Hydro Boost Water Gel",
            "product_relevance_for_customer": "Provides intense hydration for dry skin.",
            "product_link": "https://www.ulta.com/p/hydro-boost-water-gel",
            "product_original_price": "23.99",
            "product_sale_price": "19.99"
        },
        {
            "product_name": "CeraVe Hydrating Facial Cleanser",
            "product_relevance_for_customer": "Gentle cleanser for dry and sensitive skin.",
            "product_link": "https://www.ulta.com/p/hydrating-facial-cleanser",
            "product_original_price": "15.99",
            "product_sale_price": "12.99"
        },
        {
            "product_name": "The Ordinary Niacinamide 10% + Zinc 1%",
            "product_relevance_for_customer": "Helps reduce blemishes and balance sebum activity.",
            "product_link": "https://www.ulta.com/p/niacinamide-10-zinc-1",
            "product_original_price": "5.90",
            "product_sale_price": "4.90"
        }
    ],
    "hair": [
        {
            "product_name": "Olaplex No. 3 Hair Perfector",
            "product_relevance_for_customer": "Repairs damaged and compromised hair.",
            "product_link": "https://www.ulta.com/p/no-3-hair-perfector",
            "product_original_price": "28.00",
            "product_sale_price": "24.00"
        },
        {
            "product_name": "Living Proof Perfect Hair Day Dry Shampoo",
            "product_relevance_for_customer": "Cleans hair and absorbs oil and odor.",
            "product_link": "https://www.ulta.com/p/perfect-hair-day-dry-shampoo",
            "product_original_price": "26.00",
            "product_sale_price": "22.00"
        },
        {
            "product_name": "Briogeo Don't Despair, Repair! Deep Conditioning Mask",
            "product_relevance_for_customer": "Intensive weekly treatment for dry, damaged hair.",
            "product_link": "https://www.ulta.com/p/dont-despair-repair-deep-conditioning-mask",
            "product_original_price": "36.00",
            "product_sale_price": "30.00"
        }
    ]
}

        result1 = self.instance.validate_response_schema(valid_prefs_object, "prefs")
        self.assertTrue(result1)


    def test_invalid_td_schema(self):
        """Testing invalid schema for top deals"""

        invalid_td_object = {
    "deals": [
        {
            "product_name": "Product 1",
            "product_link": "https://example.com/product1",
            "product_original_price": "50.00",
            "deal_analysis": "Great discount on a popular item."
        },
        {
            "product_name": "Product 2",
            "product_link": "https://example.com/product2",
        },
        {
            "product_name": "Product 3",
            "product_link": "https://example.com/product3",
            "product_original_price": "60.00",
            "product_sale_price": "45.00",
            "deal_analysis": "Good deal on a high-quality product."
        },
        {
            "product_name": "Product 4",
            "product_link": "https://example.com/product4",
            "product_original_price": "25.00",
            "product_sale_price": "18.00",
            "deal_analysis": "Affordable price for a top-rated item."
        },
        {
            "product_name": "Product 5",
            "product_link": "https://example.com/product5",
            "product_original_price": "40.00",
            "product_sale_price": "30.00",
            "deal_analysis": "Decent discount on a bestseller."
        },
        {
            "product_name": "Product 6",
            "product_link": "https://example.com/product6",
            "product_original_price": "70.00",
            "product_sale_price": "50.00",
            "deal_analysis": "Excellent value for a premium product."
        },
        {
            "product_name": "Product 7",
            "product_link": "https://example.com/product7",
            "product_original_price": "55.00",
            "product_sale_price": "42.00",
            "deal_analysis": "Good savings on a popular brand."
        },
        {
            "product_name": "Product 8",
            "product_link": "https://example.com/product8",
            "product_original_price": "80.00",
            "product_sale_price": "60.00",
            "deal_analysis": "Significant discount on a high-end item."
        },
        {
            "product_name": "Product 9",
            "product_link": "https://example.com/product9",
            "product_original_price": "35.00",
            "product_sale_price": "25.00",
            "deal_analysis": "Great price for a top-reviewed product."
        }
    ]
}

        result2 = self.instance.validate_response_schema(invalid_td_object, "td")
        self.assertFalse(result2)

    def test_valid_td_schema(self):
        """Testing valid schema for top deals"""
        valid_td_object = {
    "deals": [
        {
            "product_name": "Product 1",
            "product_link": "https://example.com/product1",
            "product_original_price": "50.00",
            "product_sale_price": "40.00",
            "deal_analysis": "Great discount on a popular item."
        },
        {
            "product_name": "Product 2",
            "product_link": "https://example.com/product2",
            "product_original_price": "30.00",
            "product_sale_price": "20.00",
            "deal_analysis": "Significant savings on a new arrival."
        },
        {
            "product_name": "Product 3",
            "product_link": "https://example.com/product3",
            "product_original_price": "60.00",
            "product_sale_price": "45.00",
            "deal_analysis": "Good deal on a high-quality product."
        },
        {
            "product_name": "Product 4",
            "product_link": "https://example.com/product4",
            "product_original_price": "25.00",
            "product_sale_price": "18.00",
            "deal_analysis": "Affordable price for a top-rated item."
        },
        {
            "product_name": "Product 5",
            "product_link": "https://example.com/product5",
            "product_original_price": "40.00",
            "product_sale_price": "30.00",
            "deal_analysis": "Decent discount on a bestseller."
        },
        {
            "product_name": "Product 6",
            "product_link": "https://example.com/product6",
            "product_original_price": "70.00",
            "product_sale_price": "50.00",
            "deal_analysis": "Excellent value for a premium product."
        },
        {
            "product_name": "Product 7",
            "product_link": "https://example.com/product7",
            "product_original_price": "55.00",
            "product_sale_price": "42.00",
            "deal_analysis": "Good savings on a popular brand."
        },
        {
            "product_name": "Product 8",
            "product_link": "https://example.com/product8",
            "product_original_price": "80.00",
            "product_sale_price": "60.00",
            "deal_analysis": "Significant discount on a high-end item."
        },
        {
            "product_name": "Product 9",
            "product_link": "https://example.com/product9",
            "product_original_price": "35.00",
            "product_sale_price": "25.00",
            "deal_analysis": "Great price for a top-reviewed product."
        },
        {
            "product_name": "Product 10",
            "product_link": "https://example.com/product10",
            "product_original_price": "45.00",
            "product_sale_price": "33.00",
            "deal_analysis": "Good deal with a reasonable discount."
        }
    ]
}  
        result1 = self.instance.validate_response_schema(valid_td_object, "td")
        self.assertTrue(result1)

if __name__ == '__main__':
    unittest.main()
