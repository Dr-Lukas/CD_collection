import requests
from bengans_scraper.transform import item_parser, filter_parm_handler


def generate_url(
    base_url: str, price_min: int, price_max: int, genre: str, label=""
) -> str:
    filter_params = filter_parm_handler.create_filter_param(
        price_min, price_max, genre, label
    )
    complete_url = f"{base_url}#{filter_params}"
    return complete_url


def fetch_items(
    session: requests.sessions.Session, filter_parm: str, offset: int
) -> list:
    response = session.post(
        "https://www.bengans.com/shop",
        data={
            "filter_params": filter_parm,
            "funk": "get_filter",
            "limits": "96",
            "category_id": "6",
            "brand_id": None,
            "campaign_id": None,
            "property_value_id": None,
            "offset": str(offset),
            "Visn": "Std",
            "Sort": "Pris",
            "is_start": "1",
            "is_search": "0",
            "outlet": "0",
            "search_list": None,
            "sok_term": None,
            "campaign_type": None,
            "product_list": None,
        },
    )

    items_from_html = item_parser.extract_items_from_html(response.text)

    return items_from_html
