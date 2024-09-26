import requests
from bengans_scraper.extract import web_driver, fetch_data
from bengans_scraper.transform import filter_parm_handler, item_parser
from datetime import datetime
from bengans_scraper.load import orchestration, loader
import os
import pathlib
import yaml
from decimal import Decimal

def dynamic_load_and_save(
    session: requests.sessions.Session,
    price_min: int,
    price_max: int,
    max_price_limit: int,
    max_items_per_range: int,
    filters: list,
    output_dir: str,
    filename: str,
    url: str,
) -> None:
    genre_list = filters.get("Genre")
    offset = 0
    output_dir = os.path.join(output_dir, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(output_dir, exist_ok=True)

    initial_price_min = price_min
    initial_price_max = price_max

    if genre_list is None:
        raise Exception("Genres were not retrieved")

    for genre_item in genre_list:
        genre = genre_item.get("value")
        match_count = int(genre_item["match_count"])
        genre_filename = f"{genre}_{filename}"
        output_path = os.path.join(output_dir, genre_filename)

        price_min = initial_price_min
        price_max = initial_price_max

        if match_count >= 96:
            while price_min < max_price_limit:
                max_offset = (max_items_per_range // 96) * 96
                filter_parm = filter_parm_handler.create_filter_param(price_min, price_max, genre)

                test_items = fetch_data.fetch_items(session, filter_parm, max_offset)

                if len(test_items) == 96:
                    if price_min >= float(test_items[-1]["current_price"]) - 0.01:
                        price_max = price_min
                        url_filtered = fetch_data.generate_url(url, price_min, price_max, genre)
                        raw_html_filtered = web_driver.web_driver(url_filtered, sleep_time=5)
                        filter_subset = item_parser.extract_items_from_html(raw_html_filtered)
                        label_list = filter_subset["Label"]

                        for label_item in label_list:
                            label = label_item["value"]
                            filter_parm = filter_parm_handler.create_filter_param(
                                price_min, price_max, genre, label
                            )
                            print(label)
                            orchestration.generate_and_save_items(
                                session,
                                filter_parm,
                                offset,
                                price_min,
                                price_max,
                                genre,
                                output_path,
                            )
                    else:
                        print(
                            f"Max offset {max_offset} returned 96 items, reducing price range."
                        )
                        price_max = float(test_items[-1]["current_price"]) - 0.01
                        offset = 0
                        continue
                else:
                    print(
                        f"Max offset {max_offset} returned no or less than 96 items, continuing to extraction."
                    )
                orchestration.generate_and_save_items(
                    session,
                    filter_parm,
                    offset,
                    price_min,
                    price_max,
                    genre,
                    output_path,
                )

                price_min = price_max + 0.01
                price_max += 10
                offset = 0

        else:
            filter_parm = filter_parm_handler.create_filter_param(price_min, price_max, genre)

            fetched_items = fetch_data.fetch_items(session, filter_parm, offset)

            if fetched_items:
                print(
                    f"Fetched {len(fetched_items)} items with genre: {genre}, price range: {price_min} - {price_max}, offset: {offset}"
                )

            if fetched_items:
                loader.save_items_to_csv(fetched_items, output_path)

def main(config_path: pathlib.Path) -> None:
    with open(config_path, "r") as yaml_file: # TODO rewrite to use config.py
        config = yaml.safe_load(yaml_file)

    url = config["scraper"]["url"]

    raw_html = web_driver.web_driver(url)

    filters = web_driver.get_genres_from_html(raw_html)

    price_min = 0.99
    price_max = 600.00
    max_price_limit = 600.00
    max_items_per_range = 9888
    filename = "fetched_products.csv"
    output_dir = "bengans_scraper/load/data/"

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


if __name__ == "__main__":
    main(pathlib.Path("config/config.yaml"))