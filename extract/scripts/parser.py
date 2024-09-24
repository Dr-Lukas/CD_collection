from bs4 import BeautifulSoup


def extract_items_from_html(html_text: str) -> list:
    soup = BeautifulSoup(html_text, "html.parser")

    product_wrappers = soup.find_all("div", class_="PT_Wrapper")

    items = []

    for product in product_wrappers:
        product_name_tag = product.find("div", class_="PT_Beskr").find("a")
        product_name = (
            product_name_tag.get_text(strip=True) if product_name_tag else None
        )

        band_name_tag = product.find("div", class_="brand").find("a")
        band_name = band_name_tag.get_text(strip=True) if band_name_tag else None

        price_tag = product.find("div", class_="PT_Pris")
        discounted_price_tag = price_tag.find("span", class_="PT_PrisKampanj")
        original_price_tag = price_tag.find("span", class_="PT_PrisOrdinarie")
        normal_price_tag = price_tag.find("span", class_="PT_PrisNormal")

        discounted_price = (
            discounted_price_tag.get_text(strip=True).replace("€", "")
            if discounted_price_tag
            else None
        )
        original_price = (
            original_price_tag.get_text(strip=True).replace("€", "")
            if original_price_tag
            else None
        )
        price = (
            normal_price_tag.get_text(strip=True).replace("€", "")
            if normal_price_tag
            else original_price
        )

        status_tag = product.find("div", class_="buy-button")
        if status_tag:
            status = status_tag.find("span", class_="label").get_text(strip=True)
        else:
            status_tag = product.find("a", class_="buy-button")
            status = status_tag.get_text(strip=True) if status_tag else None

        media_format_tag = product.find("span", class_="mediaformat")
        media_format = (
            media_format_tag.get_text(strip=True) if media_format_tag else None
        )

        product_link_tag = product.find("a", class_="info-link")
        product_link = product_link_tag["href"] if product_link_tag else None

        items.append(
            {
                "product_name": product_name,
                "band_name": band_name,
                "discounted_price": discounted_price,
                "original_price": original_price,
                "current_price": discounted_price if discounted_price else price,
                "status": status,
                "media_format": media_format,
                "product_link": product_link,
            }
        )

    return items
