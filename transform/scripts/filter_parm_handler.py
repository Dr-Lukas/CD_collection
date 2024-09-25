import json
import urllib.parse


def create_filter_param(price_min: int, price_max: int, genre: str, label="") -> str:
    filter_dict = {
        "F85": genre,
        "FPris": f"{price_min:.2f}--{price_max:.2f}",
        "F69": label,
    }

    filter_json = json.dumps(filter_dict)

    return urllib.parse.quote(filter_json)
