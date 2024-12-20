import requests
from bengans_scraper.extract import fetch_data
from . import loader, bigquery_connections


def generate_and_save_items(
    session: requests.sessions.Session,
    filter_parm: str,
    offset: int,
    price_min: int,
    price_max: int,
    genre: str,
    output_path: str,
    my_table: bigquery_connections.BigQueryTable
) -> GeneratorExit:
    while True:
        fetched_items = fetch_data.fetch_items(session, filter_parm, offset)

        if fetched_items:
            print(
                f"Fetched {len(fetched_items)} items with genre: {genre}, price range: {price_min} - {price_max}, offset: {offset}"
            )

            offset += 96 #TODO add this to config

        else:
            print(
                f"No more items found for genre: {genre}, price range: {price_min} - {price_max}"
            )
            break

        if fetched_items:
            # loader.save_items_to_csv(fetched_items, output_path)
            my_table.upload_data(fetched_items)
