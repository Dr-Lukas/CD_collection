import requests
from datetime import datetime
from extract_genres import web_driver, get_genres_from_html
from parser import extract_items_from_html
import json
import csv
import urllib.parse
import yaml
import os


def create_filter_param(price_min: int, price_max: int, genre: str, label="") -> str:
    filter_dict = {
        "F85": genre,
        "FPris": f"{price_min:.2f}--{price_max:.2f}",
        "F69": label,
    }

    filter_json = json.dumps(filter_dict)

    return urllib.parse.quote(filter_json)


def generate_url(
    base_url: str, price_min: int, price_max: int, genre: str, label=""
) -> str:
    filter_params = create_filter_param(price_min, price_max, genre, label)
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

    items_from_html = extract_items_from_html(response.text)

    return items_from_html


def generate_and_save_items(
    session: requests.sessions.Session,
    items: list,
    filter_parm: str,
    offset: int,
    price_min: int,
    price_max: int,
    genre: str,
    output_path: str,
):
    while True:
        fetched_items = fetch_items(session, filter_parm, offset)

        if fetched_items:
            items.extend(fetched_items)
            print(
                f"Fetched {len(fetched_items)} items with genre: {genre}, price range: {price_min} - {price_max}, offset: {offset}"
            )

            offset += 96

        else:
            print(
                f"No more items found for genre: {genre}, price range: {price_min} - {price_max}"
            )
            break

        if items:
            save_items_to_csv(items, output_path)
            items.clear()


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
    genre_list = filters["Genre"]
    offset = 0
    items = []
    output_dir = os.path.join(output_dir, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(output_dir, exist_ok=True)

    initial_price_min = price_min
    initial_price_max = price_max

    for genre_item in genre_list:
        genre = genre_item["value"]
        match_count = int(genre_item["match_count"])
        genre_filename = f"{genre}_{filename}"
        output_path = os.path.join(output_dir, genre_filename)

        price_min = initial_price_min
        price_max = initial_price_max

        if match_count >= 96:
            while price_min < max_price_limit:
                max_offset = (max_items_per_range // 96) * 96
                filter_parm = create_filter_param(price_min, price_max, genre)

                test_items = fetch_items(session, filter_parm, max_offset)

                if len(test_items) == 96:
                    if price_min >= float(test_items[-1]["current_price"]) - 0.01:
                        price_max = price_min
                        url_filtered = generate_url(url, price_min, price_max, genre)
                        raw_html_filtered = web_driver(url_filtered, sleep_time=5)
                        filter_subset = get_genres_from_html(raw_html_filtered)
                        label_list = filter_subset["Label"]

                        for label_item in label_list:
                            label = label_item["value"]
                            filter_parm = create_filter_param(
                                price_min, price_max, genre, label
                            )
                            print(label)
                            generate_and_save_items(
                                session,
                                items,
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
                generate_and_save_items(
                    session,
                    items,
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

            if items:
                save_items_to_csv(items, output_path)
                items.clear()
        else:
            filter_parm = create_filter_param(price_min, price_max, genre)

            fetched_items = fetch_items(session, filter_parm, offset)

            if fetched_items:
                items.extend(fetched_items)
                print(
                    f"Fetched {len(fetched_items)} items with genre: {genre}, price range: {price_min} - {price_max}, offset: {offset}"
                )

            if items:
                save_items_to_csv(items, output_path)
                items.clear()


def save_items_to_csv(items: list, filename: str) -> None:
    csv_columns = [
        "product_name",
        "band_name",
        "discounted_price",
        "original_price",
        "current_price",
        "status",
        "media_format",
        "product_link",
    ]

    try:
        with open(filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=csv_columns)

            if file.tell() == 0:
                writer.writeheader()

            writer.writerows(items)
    except IOError:
        print("I/O error while writing to CSV")


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
    output_dir = "extract/data/raw"

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
