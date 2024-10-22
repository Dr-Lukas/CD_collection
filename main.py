import os
import pathlib
import requests
from typing import Tuple
from datetime import datetime
from bengans_scraper.extract import web_driver, fetch_data
from bengans_scraper.transform import filter_parm_handler
from bengans_scraper.models import data_model
from bengans_scraper.load import orchestration, loader
from config import BengansScraper, load_config



def handle_full_batch(
    items: list,
    price_min: float,
    price_max: float,
    session: requests.sessions.Session,
    genre: str,
    output_path: str,
    url: str,
) -> Tuple[float, bool]:
    """Handle the case where the number of fetched items matches the batch_size."""
    if price_min >= float(items[-1]["current_price"]) - 0.01:
        price_max = price_min
        url_filtered = fetch_data.generate_url(url, price_min, price_max, genre)
        raw_html_filtered = web_driver.web_driver(url_filtered, sleep_time=5)
        filter_subset = web_driver.get_filters_from_html(raw_html_filtered)
        label_list = filter_subset["Label"]

        for label_item in label_list:
            label = label_item["value"]
            filter_parm = filter_parm_handler.create_filter_param(
                price_min, price_max, genre, label
            )
            orchestration.generate_and_save_items(
                session, filter_parm, 0, price_min, price_max, genre, output_path
            )

    else:
        print(f"Max offset returned batch size items, reducing price range.")
        return float(items[-1]["current_price"]) - 0.01, False

    return price_max, True


def single_offset(
    price_min: float,
    price_max: float,
    genre: str,
    session: requests.sessions.Session,
    offset: int,
) -> list[data_model.BengansProducts]:
    filter_parm = filter_parm_handler.create_filter_param(price_min, price_max, genre)
    items = fetch_data.fetch_items(session, filter_parm, offset)

    return items


def process_genre(
    genre_item: dict,
    session: requests.sessions.Session,
    config: BengansScraper,
    output_dir: str,
) -> None:
    """Process each genre item and fetch/save data accordingly."""
    genre = genre_item.get("value")
    match_count = int(genre_item["match_count"])

    price_min = config.Scraper.price_min
    price_max = config.Scraper.price_max
    max_price_limit = price_max

    output_path = os.path.join(output_dir, f"{genre}_{config.Loader.filename}")

    if match_count < config.Scraper.batch_size:
        items = single_offset(price_min, price_max, genre, session, 0)

        if items:
            print(
                f"Fetched {len(items)} items with genre: {genre}, price range: {price_min} - {price_max}"
            )
            loader.save_items_to_csv(items, output_path)

        return

    while price_min < max_price_limit:
        test_items = single_offset(
            price_min, price_max, genre, session, config.Scraper.max_offset
        )

        if len(test_items) == config.Scraper.batch_size:
            price_max, set_new_price = handle_full_batch(
                test_items,
                price_min,
                price_max,
                session,
                genre,
                output_path,
                config.Scraper.url,
            )

        else:
            filter_parm = filter_parm_handler.create_filter_param(
                price_min, price_max, genre
            )
            orchestration.generate_and_save_items(
                session, filter_parm, 0, price_min, price_max, genre, output_path
            )

            set_new_price = True

        if set_new_price:
            price_min = price_max + 0.01
            price_max += 10


def dynamic_load_and_save(config: BengansScraper) -> None:
    url = config.Scraper.url
    output_dir = os.path.join(config.Loader.path, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(output_dir, exist_ok=True)

    raw_html = web_driver.web_driver(url)
    filters = web_driver.get_filters_from_html(raw_html)

    session = requests.session()
    genre_list = filters.get("Genre")

    if genre_list is None:
        raise Exception("Genres were not retrieved")

    for genre_item in genre_list:
        process_genre(genre_item, session, config, output_dir)


def main(config_path: pathlib.Path) -> None:
    config = load_config(config_path)
    dynamic_load_and_save(config)


if __name__ == "__main__":
    main(pathlib.Path("config/config.yaml"))
