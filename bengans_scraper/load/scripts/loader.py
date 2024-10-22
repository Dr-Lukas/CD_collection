import csv
from bengans_scraper.models import data_model

def save_items_to_csv(items: list[data_model.BengansProducts], filename: str) -> None:
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
            for item in items:
                writer.writerow(item.model_dump())
    except IOError:
        print("I/O error while writing to CSV")
