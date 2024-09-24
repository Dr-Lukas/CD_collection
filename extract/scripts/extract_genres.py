from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import yaml


def web_driver(url: str, sleep_time: int = 2) -> str:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    time.sleep(sleep_time)

    page_raw_data = driver.page_source
    return page_raw_data


def get_genres_from_html(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    filter_section = soup.find_all("div", class_="FilterWrapper")
    filters = {}

    for section in filter_section:
        if "Filter_Slider" in section["class"]:
            continue

        title = section.find("span", class_="Filter_Titel").text.strip()
        options = []

        for label in section.find_all("label"):
            checkbox = label.find("input", class_="f-input")

            if checkbox.has_attr("disabled"):
                continue

            option_value = label.get("data-value")
            match_count = label.find("span", class_="match_count").text.strip()

            options.append({"value": option_value, "match_count": match_count})

        if options:
            filters[title] = options

    return filters


if __name__ == "__main__":
    with open("extract/config/config.yaml", "r") as yaml_file:
        config = yaml.safe_load(yaml_file)

    url = config["scraper"]["url"]

    raw_html = web_driver(url)

    filters = get_genres_from_html(raw_html)
