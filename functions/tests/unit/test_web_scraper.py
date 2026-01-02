import pytest
from unittest.mock import MagicMock, patch
from fn_imports.web_scraper import DealGenerator  # Ensure your file is named parser_bot.py
from urllib3.exceptions import MaxRetryError

VALID_SALES_HTML = """
<html>
    <body>
        <li class="ProductListingResults__productCard" data-test="products-list-item" data-sku-id="2629931"><div class="ProductCard" data-visible="true" data-item-id="2629931" role="group" aria-label="product"><a class="pal-c-Link pal-c-Link--primary pal-c-Link--default" target="_self" tabindex="0" href="https://www.ulta.com/p/pout-preserve-hydrating-peptide-lip-treatment-pimprod2042281?sku=2629931" aria-hidden="false"><span class="pal-c-Link__label"><div class="ProductCard__image ProductCard__image__full__small"><div class="Image"><img class="" alt="OLEHENRIKSEN Pout Preserve Hydrating Peptide Lip Treatment" aria-hidden="true" loading="lazy" src="https://media.ulta.com/i/ulta/2629931?w=600&amp;$ProductCardNeutralBGLight$&amp;h=600&amp;fmt=auto" width="480" height="480"></div><div class="ProductCard__badgeContainer"><div class="ProductCard__badgeContainer__tag"><p class="pal-c-Tag pal-c-Tag__default pal-c-Tag--customBackgroundColor pal-c-Tag--customTextColor" style="--tag-background-color: var( --pal-colors-default-background-default ); --tag-text-color: var( --pal-colors-default-content-default );"><span class="pal-c-Tag__message"><span class="pal-c-Tag__messageText">Sale</span></span></p></div></div><span class="ProductCard__variant"><p class="Text-ds Text-ds--body-3 Text-ds--left Text-ds--neutral-600">11 colors</p></span></div><div class="ProductCard__content"><h3 class="ProductCard__heading"><span class="ProductCard__brand"><span class="Text-ds Text-ds--titleXxs Text-ds--left Text-ds--black">OLEHENRIKSEN</span>&nbsp;</span><span class="ProductCard__product"><span class="Text-ds Text-ds--body-2 Text-ds--left Text-ds--black">Pout Preserve Hydrating Peptide Lip Treatment</span></span></h3><div class="ProductCard__rating"><div class="ReviewStarsCard"><svg class="pal-c-Icon pal-c-Icon--size-default" aria-hidden="true" focusable="false" role="img" height="12" width="12" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M11.998.75c.308 0 .59.172.73.446l3.345 6.629 6.44.638a.805.805 0 0 1 .5 1.374l-5.3 5.253 1.965 7.138a.813.813 0 0 1-.698 1.017l-.115.004a.811.811 0 0 1-.338-.086l-6.529-3.233-6.52 3.229a.812.812 0 0 1-.222.074l-.116.012a.813.813 0 0 1-.813-1.021l1.965-7.138L.988 9.833a.805.805 0 0 1 .5-1.374l6.44-.638 3.341-6.625A.819.819 0 0 1 12 .75Z" fill="inherit"></path></svg><svg class="pal-c-Icon pal-c-Icon--size-default" aria-hidden="true" focusable="false" role="img" height="12" width="12" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M11.998.75c.308 0 .59.172.73.446l3.345 6.629 6.44.638a.805.805 0 0 1 .5 1.374l-5.3 5.253 1.965 7.138a.813.813 0 0 1-.698 1.017l-.115.004a.811.811 0 0 1-.338-.086l-6.529-3.233-6.52 3.229a.812.812 0 0 1-.222.074l-.116.012a.813.813 0 0 1-.813-1.021l1.965-7.138L.988 9.833a.805.805 0 0 1 .5-1.374l6.44-.638 3.341-6.625A.819.819 0 0 1 12 .75Z" fill="inherit"></path></svg><svg class="pal-c-Icon pal-c-Icon--size-default" aria-hidden="true" focusable="false" role="img" height="12" width="12" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M11.998.75c.308 0 .59.172.73.446l3.345 6.629 6.44.638a.805.805 0 0 1 .5 1.374l-5.3 5.253 1.965 7.138a.813.813 0 0 1-.698 1.017l-.115.004a.811.811 0 0 1-.338-.086l-6.529-3.233-6.52 3.229a.812.812 0 0 1-.222.074l-.116.012a.813.813 0 0 1-.813-1.021l1.965-7.138L.988 9.833a.805.805 0 0 1 .5-1.374l6.44-.638 3.341-6.625A.819.819 0 0 1 12 .75Z" fill="inherit"></path></svg><svg class="pal-c-Icon pal-c-Icon--size-default" aria-hidden="true" focusable="false" role="img" height="12" width="12" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M11.998.75c.308 0 .59.172.73.446l3.345 6.629 6.44.638a.805.805 0 0 1 .5 1.374l-5.3 5.253 1.965 7.138a.813.813 0 0 1-.698 1.017l-.115.004a.811.811 0 0 1-.338-.086l-6.529-3.233-6.52 3.229a.812.812 0 0 1-.222.074l-.116.012a.813.813 0 0 1-.813-1.021l1.965-7.138L.988 9.833a.805.805 0 0 1 .5-1.374l6.44-.638 3.341-6.625A.819.819 0 0 1 12 .75Z" fill="inherit"></path></svg><svg class="pal-c-Icon pal-c-Icon--size-default" aria-hidden="true" focusable="false" role="img" height="12" width="12" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M4.602 23.068a.813.813 0 0 1-.273-.84l.872-3.172 1.087-3.966-5.3-5.253a.805.805 0 0 1 .385-1.356l.115-.018 6.44-.638L11.271 1.2a.819.819 0 0 1 .3-.325c.095-.06.203-.1.317-.117l.115-.008v.004l.11.008a.819.819 0 0 1 .616.438l3.346 6.629 6.44.638a.805.805 0 0 1 .5 1.374l-5.3 5.253 1.965 7.138a.813.813 0 0 1-1.151.935l-6.528-3.232-6.518 3.228a.816.816 0 0 1-.881-.095Zm7.401-19.975.001 15.341c.176 0 .352.032.52.094l.142.062 5.158 2.554-1.555-5.652a1.5 1.5 0 0 1 .291-1.355l.1-.108 4.25-4.214-4.983-.493a1.5 1.5 0 0 1-1.115-.684l-.076-.133-2.733-5.412Z" fill="inherit"></path></svg><span class="sr-only">4.5 out of 5 stars ; 889 reviews</span><span class="Text-ds Text-ds--body-3 Text-ds--left Text-ds--neutral-600" aria-hidden="true">(889)</span></div></div><div class="ProductCard__price"><div class="ProductPricing"><span class="sr-only">sale price $16.10 - $23.00</span><span class="Text-ds Text-ds--body-lg Text-ds--left Text-ds--magenta-500" aria-hidden="true">$16.10 - $23.00</span><span class="sr-only">list price $23.00</span><span class="Text-ds Text-ds--body-3 Text-ds--left Text-ds--neutral-600 Text-ds--line-through" aria-hidden="true">$23.00</span><div class="AfterPaySubsGroup"></div></div></div></div></span></a><div class="ProductCard__buttonContainer"><div class="ProductCard__addToBag"><button class="pal-c-Button pal-c-Button--primary pal-c-Button--compact" type="button" tabindex="0"><span class="pal-c-Button__text">Add to bag</span></button></div><div class="ProductCard__sponsoredText"></div></div></div></li>
    </body>
</html>
"""

VALID_GWP_HTML = """
<html>
    <li class="PromotionListingResults__compactDealCard">
        <div class="CompactDealCard__gwpLine">
            <div>Free Gift</div>
            <div>ignored middle div</div>
            <div>with $50 purchase</div>
        </div>
    </li>
</html>
"""

VALID_TODAYS_DEALS_HTML = """
<html>
    <div class="LargeDealCard__textContent">
        <div class="LargeDealCard__headline">50% Off</div>
        <div class="LargeDealCard__subtitle">Select Brands</div>
    </div>
</html>
"""

VALID_BMSM_HTML = """
<html>
    <li class="PromotionListingResults__compactDealCard">
        <div class="CompactDealCard__gwpLine">
            <div>Buy 1 Get 1</div>
            <div>ignored</div>
            <div>Online only Buy 2 Get 1 Free (excludes clearance)</div>
        </div>
    </li>
</html>
"""

@pytest.fixture
def generator():
    return DealGenerator()

@patch('requests.get')
def test_get_sale_data_success(mock_get, generator):
    """
    Test that sales data is correctly parsed, calculations are correct,
    and sponsored items are skipped.
    """

    mock_response = MagicMock()
    mock_response.content = VALID_SALES_HTML
    mock_get.return_value = mock_response


    results = generator.get_sale_data("makeup")


    assert len(results) == 1
    item = results[0]
    
    assert item["name"] == "OLEHENRIKSEN Pout Preserve Hydrating Peptide Lip Treatment"
    assert item["sku"] == "2629931"
    assert item["sale_price"] == 16.10
    assert item["list_price"] == 23.00
    assert item["discount"] == 29
    
    mock_get.assert_called_with("https://www.ulta.com/promotion/sale?category=makeup", timeout=5)

@patch('requests.get')
def test_get_sale_data_empty(mock_get, generator):
    """Test behavior when no items match criteria."""
    mock_response = MagicMock()
    mock_response.content = "<html><body></body></html>"
    mock_get.return_value = mock_response

    with pytest.raises(RuntimeError, match="Issue with beautiful soup instance"):
        generator.get_sale_data("skincare")

@patch('requests.get')
def test_get_sale_data_network_error(mock_get, generator):
    """Test behavior when requests raises an exception."""
    mock_pool = MagicMock()
    error_instance = MaxRetryError(pool=mock_pool, url="url")
    mock_get.side_effect = error_instance

    with pytest.raises(RuntimeError, match="Issue with beautiful soup instance"):
        generator.get_sale_data("hair")

@patch('requests.get')
def test_get_promotional_data_aggregation(mock_get, generator):
    """
    Test get_promotional_data correctly calls multiple URLs
    and aggregates the results from GWP, Today's Deals, and BMSM.
    """
    def side_effect(url, timeout=5):
        mock_resp = MagicMock()
        if "gift-with-purchase" in url:
            mock_resp.content = VALID_GWP_HTML
        elif "all" in url: # Today's deals
            mock_resp.content = VALID_TODAYS_DEALS_HTML
        elif "buy-more-save-more" in url:
            mock_resp.content = VALID_BMSM_HTML
        else:
            mock_resp.content = ""
        return mock_resp

    mock_get.side_effect = side_effect

    results = generator.get_promotional_data()

    assert len(results) == 3

    assert "Free Gift with $50 purchase" in results
    
    assert "50% Off Select Brands" in results

    expected_bmsm_part = " Buy 2 Get 1 Free "
    assert any(expected_bmsm_part in s for s in results)

def test_sku_extraction(generator):
    """SKU extraction logic"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.content = VALID_SALES_HTML
        mock_get.return_value = mock_response
        
        result = generator.get_sale_data("makeup")
        assert result[0]['sku'] == "2629931"