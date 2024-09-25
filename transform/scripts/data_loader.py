import requests
from datetime import datetime
from filter_parm_handler import create_filter_param
from extract.scripts.fetch_data import fetch_items, generate_url
from extract.scripts.web_driver import web_driver, get_genres_from_html
from load.scripts.orchestration import generate_and_save_items
from load.scripts.loader import save_items_to_csv
import os


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
