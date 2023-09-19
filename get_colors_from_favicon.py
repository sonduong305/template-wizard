from collections import Counter
from io import BytesIO
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup as bs
from PIL import Image


def fetch_favicon_url(website_url):
    try:
        response = requests.get(website_url)
        if response.status_code != 200:
            return None

        soup = bs(response.text, "html.parser")

        favicon_link = soup.find(
            "link",
            {
                "rel": lambda x: x
                and ("icon" in x.lower() or "shortcut icon" in x.lower())
            },
        )

        if favicon_link and "href" in favicon_link.attrs:
            favicon_url = favicon_link["href"]

            favicon_url = urljoin(website_url, favicon_url)

            return favicon_url
        else:
            return urljoin(website_url, "/favicon.ico")
    except Exception as e:
        print(f"An error occurred while fetching favicon URL: {e}")
        return None


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def get_top_k_colors_from_favicon(website_url, k=3):
    favicon_url = fetch_favicon_url(website_url)

    if not favicon_url:
        return "Failed to find or download the favicon."

    try:
        response = requests.get(favicon_url)
        if response.status_code != 200:
            return "Failed to download the favicon image."

        image = Image.open(BytesIO(response.content))
        image = image.convert("RGBA")

        pixels = list(image.getdata())
        pixels = [(r, g, b) for r, g, b, a in pixels]

        total_pixels = len(pixels)

        color_counter = Counter(pixels)
        sorted_colors = sorted(color_counter.items(), key=lambda x: x[1], reverse=True)

        top_k_colors = sorted_colors[:k]
        top_k_colors_hex = [
            (rgb_to_hex(color), freq / total_pixels * 100)
            for color, freq in top_k_colors
        ]

        return top_k_colors_hex

    except Exception as e:
        return f"An error occurred: {e}"
