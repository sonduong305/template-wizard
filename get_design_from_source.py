import ast
import json
import logging
import os
from urllib.parse import urljoin, urlparse

import cssutils
import requests
import tiktoken
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from litellm import completion

from get_colors_from_favicon import get_top_k_colors_from_favicon

cssutils.log.setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

load_dotenv()
MODEL_NAME = os.environ.get("MODEL_NAME")
max_tokens = int(os.environ.get("MODEL_MAX_TOKENS"))


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def select_meaningful_css_files(files):
    prompt = "Above are css files of a website, return what should be the main style sheet, not any lib ones. Return in the list of css file urls in list format without any additional information"

    response = completion(
        messages=[
            {"role": "user", "content": str(files)},
            {"role": "user", "content": prompt},
        ],
        model=MODEL_NAME,
        temperature=0.1,
    )
    if not response["choices"][0]["message"]["content"].startswith("["):
        return []
    css_files = ast.literal_eval(response["choices"][0]["message"]["content"])
    valid_files = []
    for file in css_files:
        if is_valid_url(file):
            valid_files.append(file)
    return valid_files


def extract_meaningful_css_blocks(all_blocks, cta_element=None):
    meaningful_block = []

    if cta_element.get("id") or cta_element.get("class"):
        if cta_element.get("class"):
            selector_str = f"class: {cta_element.get('class')}"
        if cta_element.get("id"):
            selector_str = f"id: {cta_element.get('id')}"

        for blocks in all_blocks:
            prompt = 'Above are the CTA element and all css, what is the primary color of the cta element? Answer in format {"primary_color": ""}, if not found in the css, just return {}'

            response = completion(
                messages=[
                    {"role": "user", "content": blocks},
                    {"role": "user", "content": f"CTA {selector_str}"},
                    {"role": "user", "content": prompt},
                ],
                model=MODEL_NAME,
                temperature=0.1,
            )
            try:
                res = response["choices"][0]["message"]["content"]
                res_d = json.loads(res)
                print(res_d)
                if res_d.get("primary_color"):
                    return meaningful_block.append(res_d)
            except Exception as e:
                print(str(e))
                return

    for blocks in all_blocks:
        prompt = "What is the primary color, secondary color, background color in the whole website, given a part of the css blocks, answer in the form of json with keys: main_call_to_action_button_color, primary_color, secondary_color, background_color, text_color, link_color, primary_font, secondary_font with values being a hex code. If you find it's not in the given blocks, only return the found ones"

        response = completion(
            messages=[
                {"role": "user", "content": reduce_css(blocks)},
                {"role": "user", "content": prompt},
            ],
            model=MODEL_NAME,
            temperature=0.1,
        )
        try:
            res = response["choices"][0]["message"]["content"]
            meaningful_block.append(json.loads(res))
        except Exception:
            pass
    return meaningful_block


def reduce_css(css_string):
    parser = cssutils.CSSParser()
    parsed = parser.parseString(css_string)
    minimized_css = ""

    for rule in parsed:
        if rule.type == rule.STYLE_RULE:
            minimized_css += rule.selectorText + "{" + rule.style.cssText + "}"

    return minimized_css


def count_tokens(text):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    return sum(1 for _ in encoding.encode(text))


def filter_color_related_properties(css_string):
    css_parser = cssutils.CSSParser()
    css = css_parser.parseString(css_string)

    # List of properties related to colors
    color_properties = [
        "background-color",
        "background",
        "color",
        "text-decoration",
        "text-decoration-color",
        "font",
        "font-family",
        "font-weight",
    ]

    filtered_blocks = []
    css_variables = []

    for rule in css:
        if rule.type == rule.STYLE_RULE:
            if rule.selectorText == ":root":
                # Include the entire :root section
                filtered_blocks.append(rule.cssText)
                continue

            style = rule.style
            color_related_style = {}

            for prop in color_properties:
                if style.getPropertyValue(prop):
                    color_related_style[prop] = style.getPropertyValue(prop)

            if color_related_style:
                # Construct the CSS block with only color-related properties
                style_string = " ".join(
                    [f"{k}: {v};" for k, v in color_related_style.items()]
                )
                vars_string = " ".join(css_variables)
                color_block = f"{rule.selectorText} {{ {vars_string} {style_string} }}"
                filtered_blocks.append(color_block)
    return filtered_blocks


def truncate_css_blocks(css_string, max_tokens):
    original_blocks = filter_color_related_properties(css_string)
    truncated_blocks = []
    current_block = ""
    current_tokens = 0

    for block in original_blocks:
        block_tokens = count_tokens(block)

        if current_tokens + block_tokens <= max_tokens:
            if current_block:
                current_block += "\n" + block
            else:
                current_block = block
            current_tokens += block_tokens
        else:
            if current_block:
                truncated_blocks.append(current_block)
            current_block = block
            current_tokens = block_tokens

        if current_tokens >= max_tokens:
            truncated_blocks.append(current_block)
            current_block = ""
            current_tokens = 0

    if current_block:
        truncated_blocks.append(current_block)

    return truncated_blocks


def merge_dict(dicts_to_merge):
    merged_dict = {}

    for d in dicts_to_merge:
        for key, value in d.items():
            if value is None:
                continue

            if key in merged_dict:
                merged_dict[key].add(value.lower())
            else:
                merged_dict[key] = {value}

    for key in merged_dict:
        merged_dict[key] = list(merged_dict[key])
    return merged_dict


def truncate_to_max_tokens(text, max_tokens):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    return encoding.decode(encoding.encode(text)[:max_tokens])


def get_cta(html):
    prompt = 'Look at this html, what is the cta element for the primary color or something similar here? return in format {"primary_color_element": {"id": "", "class": ""}, "secondary_color_element": {"id": "", "class": ""}}, leave both blank if not found'
    response = completion(
        messages=[
            {"role": "user", "content": html},
            {"role": "user", "content": prompt},
        ],
        model=MODEL_NAME,
        temperature=0.1,
    )
    try:
        res = response["choices"][0]["message"]["content"]
        return json.loads(res)
    except Exception:
        return {}


def fetch_colors_from_url(url):
    response = requests.get(url)
    css_string = ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        html = truncate_to_max_tokens(soup.body.prettify(), max_tokens=max_tokens)
        cta_element = get_cta(html=html)

        # Extract and append CSS from <style> tags
        for style_tag in soup.find_all("style"):
            css_string += style_tag.string + "\n" if style_tag.string else ""

        css_links = []
        parsed_url = urlparse(url)
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href")
            if href:
                full_url = urljoin(url, href)
                parsed_full_url = urlparse(full_url)
                if parsed_full_url.netloc == parsed_url.netloc:
                    css_links.append(full_url)

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return
    for css in select_meaningful_css_files(css_links):
        res = requests.get(css)
        css_string += (reduce_css(res.text)) + "\n"

    css_blocks = truncate_css_blocks(css_string=css_string, max_tokens=max_tokens)
    dicts_to_merge = extract_meaningful_css_blocks(css_blocks, cta_element=cta_element)

    result = merge_dict(dicts_to_merge=dicts_to_merge)
    if "primary_color" not in result:
        result["primary_color"] = [get_top_k_colors_from_favicon(url, k=1)[0][0]]

    return result
