import requests
from extract.scripts.web_driver import web_driver, get_genres_from_html
from transform.scripts.data_loader import dynamic_load_and_save
import yaml

if __name__ == "__main__":
    with open("extract/config/config.yaml", "r") as yaml_file:
        config = yaml.safe_load(yaml_file)

    url = config["scraper"]["url"]

    raw_html = web_driver(url)

    filters = get_genres_from_html(raw_html)

    price_min = 0.99
    price_max = 600.00
    max_price_limit = 600.00
    max_items_per_range = 9888
    filename = "fetched_products.csv"
    output_dir = "load/data/"

    session = requests.session()

    dynamic_load_and_save(
        session,
        price_min,
        price_max,
        max_price_limit,
        max_items_per_range,
        filters,
        output_dir,
        filename,
        url,
    )