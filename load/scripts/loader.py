import csv


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