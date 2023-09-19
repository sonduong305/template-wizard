import json
import os

import requests
from litellm import completion
from trafilatura import extract
from trafilatura.settings import use_config

trafilatura_config = use_config()
trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")


scrape_it_api_key = os.environ.get("SCRAPE_IT_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME")
SCRAPING_SERVICE_TIMEOUT = 30
SCRAPE_IT_API_URL = "https://api.scrape-it.cloud/scrape"


def extract_text_from_url_scrape_it(url):
    try:
        headers = {"x-api-key": scrape_it_api_key, "Content-Type": "application/json"}
        payload = {
            "url": url,
            "block_resources": False,
            "wait": 0,
            "screenshot": False,
            "proxy_country": "US",
            "proxy_type": "datacenter",
        }
        r = requests.post(
            SCRAPE_IT_API_URL,
            json=payload,
            timeout=SCRAPING_SERVICE_TIMEOUT,
            headers=headers,
        )
        html = json.loads(r.text)["scrapingResult"]["content"]
        text = extract(html, config=trafilatura_config)

        return text
    except Exception as e:
        print(e)
        return ""


def apply_writing_style(original_content, url):
    text = extract_text_from_url_scrape_it(url)
    print(MODEL_NAME)
    prompt = f"""Read the above email and rewrite it in this writing style:
    Rules:
    - Only return the output email, no extra explanations
    - Try to keep the main content of the original email
    - just change the writing style, do not make up information,
    - ONLY APPLY THE WRITING STYLE, DO NOT LEARN ANYTHING ELSE FROM THE BELOW ARTICLE.
    ```
    {text}
    ```"""
    response = completion(
        messages=[
            {"role": "user", "content": original_content},
            {"role": "user", "content": prompt},
        ],
        model=MODEL_NAME,
        temperature=0.7,
    )
    try:
        res = response["choices"][0]["message"]["content"]
        return res
    except Exception:
        return {}
