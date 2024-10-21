from pydantic import BaseModel
import yaml
import pathlib

class Scraper(BaseModel):
    """Defines URL, category being scraped, price range, and offset values used for scraping the Bengans shop website.
    
    Due to websites limits:
    - batch_size: must not exceed 96.
    - max_items_per_range: dynamically calculated based on batch_size, ensuring the total number of items stays under 10,000.
    """
    url: str = "https://www.bengans.com/en/artiklar/cd/index.html"
    category: str = "CD"
    price_min: float = 0.99
    price_max: float = 600.00
    batch_size: int = 96
    max_offset: int = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.batch_size:
            n = (10000 // self.batch_size) - 1
            self.max_offset = self.batch_size * n

class Loader(BaseModel):
    """Defines path where data is being loaded"""
    filename: str = "fetched_products.csv"
    path: str = "bengans_scraper/load/data/"

class BengansScraper(BaseModel):
    """Defines how we query and store info related to a bengans website"""
    Scraper: Scraper
    Loader: Loader


def load_config(config_path: pathlib.Path) -> BengansScraper:
    """Loads the yaml file with the config and returns it as dict ready to initialise a
    CprImportConfig class
    Args:
        config_path: string pointing to an existing config.yml
    """
    with open(config_path, encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
        return BengansScraper(**data)