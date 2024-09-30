import requests
from bengans_scraper.extract import web_driver, fetch_data
from bengans_scraper.transform import filter_parm_handler, item_parser
from datetime import datetime
from bengans_scraper.load import orchestration, loader
from config import BengansScraper, load_config
import os
import pathlib
from decimal import Decimal

def dynamic_load_and_save(
    config: BengansScraper
) -> None:
    url = config["Scraper"]["url"]
    price_min = config["Scraper"]["price_min"]
    price_max = config["Scraper"]["price_max"]
    batch_size = config["Scraper"]["batch_size"]
    max_offset = config["Scraper"]["max_offset"]
    filename = config["Loader"]["filename"]
    output_dir = os.path.join(config["Loader"]["path"], datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(output_dir, exist_ok=True)

    raw_html = web_driver.web_driver(url)

    filters = web_driver.get_genres_from_html(raw_html)

    session = requests.session()

    genre_list = filters.get("Genre")
    
    if genre_list is None:
        raise Exception("Genres were not retrieved")
    
    offset = 0
    initial_price_min = price_min
    initial_price_max = price_max
    max_price_limit = price_max

    for genre_item in genre_list:
        genre = genre_item.get("value")
        match_count = int(genre_item["match_count"])
        genre_filename = f"{genre}_{filename}"
        output_path = os.path.join(output_dir, genre_filename)

        price_min = initial_price_min
        price_max = initial_price_max

        if match_count >= batch_size:
            while price_min < max_price_limit:
                filter_parm = filter_parm_handler.create_filter_param(price_min, price_max, genre)

                test_items = fetch_data.fetch_items(session, filter_parm, max_offset)

                if len(test_items) == batch_size:
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
                            f"Max offset {max_offset} returned {batch_size} items, reducing price range."
                        )
                        price_max = float(test_items[-1]["current_price"]) - 0.01
                        offset = 0
                        continue
                else:
                    print(
                        f"Max offset {max_offset} returned no or less than {batch_size} items, continuing to extraction."
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
    config = load_config(config_path)

    dynamic_load_and_save(config)


if __name__ == "__main__":
    main(pathlib.Path("config/config.yaml"))