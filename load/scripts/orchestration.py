import requests
from extract.scripts.scraper import fetch_items
from loader import save_items_to_csv


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
