from pydantic import BaseModel
from typing import Optional, List
import yaml
import pathlib

class Scraper(BaseModel):
    """Defines how we query and store info related to a CPG source"""
    url: str = "https://www.bengans.com/en/artiklar/cd/index.html"
    category: str = "CD"

class Loader(BaseModel):
    """Defines how we query and store info related to a CPG source"""
    path: str

class BengansScraper(BaseModel):
    """Defines how we query and store info related to a CPG source"""
    Scraper: Scraper
    Loader: Loader


def load_config(config_path: pathlib.Path) -> BengansScraper:
    """Loads the yaml file with the cpg import config and returns it as dict ready to initialise a
    CprImportConfig class
    Args:
        config_path: string pointing to an existing config.yml
    """
    with open(config_path, encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)["cpg_import"]
        return BengansScraper(**data)