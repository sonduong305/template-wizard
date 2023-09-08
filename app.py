import ast
import json
import logging
from urllib.parse import urljoin, urlparse

import cssutils
import requests
import streamlit as st
import tiktoken
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from litellm import completion

cssutils.log.setLevel(logging.CRITICAL)

load_dotenv()
MODEL_NAME = "gpt-3.5-turbo"


def select_meaningful_css_files(files):
    prompt = "Above are css files of a website, return what should be the main style sheet, not any lib ones. Return in the list of css file urls in list format without any additional information"

    response = completion(
        messages=[
            {"role": "user", "content": str(files)},
            {"role": "user", "content": prompt},
        ],
        model=MODEL_NAME,
    )
    return ast.literal_eval(response["choices"][0]["message"]["content"])


def extract_meaningful_css_blocks(all_blocks):
    meaningful_block = []
    for blocks in all_blocks:
        prompt = "What is the primary color, secondary color, background color in the whole website, given a part of the css blocks, answer in the form of json with keys: primary_color, secondary_color, background_color, text_color, link_color with values being a hex code. If you find it's not in the given blocks, only return the found ones"

        response = completion(
            messages=[
                {"role": "user", "content": reduce_css(blocks)},
                {"role": "user", "content": prompt},
            ],
            model=MODEL_NAME,
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
        "border",
        "border-bottom-color",
        "border-color",
        "border-left-color",
        "border-right-color",
        "border-top-color",
        "box-shadow",
        "caret-color",
        "color",
        "column-rule",
        "column-rule-color",
        "filter",
        "opacity",
        "outline-color",
        "outline",
        "text-decoration",
        "text-decoration-color",
        "text-shadow",
    ]

    filtered_blocks = []

    for rule in css:
        if rule.type == rule.STYLE_RULE:
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
                color_block = f"{rule.selectorText} {{ {style_string} }}"
                filtered_blocks.append(color_block)

    return filtered_blocks


def parse_css(css_string):
    css_parser = cssutils.CSSParser()
    css = css_parser.parseString(css_string)
    original_blocks = []

    for rule in css:
        if rule.type == rule.STYLE_RULE:
            original_block = "{} {{{}}}".format(rule.selectorText, rule.style.cssText)
            original_blocks.append(original_block)
        elif rule.type == rule.MEDIA_RULE:
            media_rules = []
            for sub_rule in rule.cssRules:
                if sub_rule.type == sub_rule.STYLE_RULE:
                    media_rules.append(
                        "{} {{{}}}".format(
                            sub_rule.selectorText, sub_rule.style.cssText
                        )
                    )
            original_blocks.extend(media_rules)

    return original_blocks


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


def fetch_colors_from_url(url):
    response = requests.get(url)
    css_string = ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
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

    css_blocks = truncate_css_blocks(css_string=css_string, max_tokens=3600)
    dicts_to_merge = extract_meaningful_css_blocks(css_blocks)

    return merge_dict(dicts_to_merge=dicts_to_merge)


def display_colors(color_name, color_codes):
    st.write(f"{color_name}:")
    for color_code in color_codes:
        st.markdown(
            f"<div style='display: inline-block; width: 50px; height: 50px; background: {color_code};'></div>"
            f"<div style='display: inline-block; margin-left: 10px;'>{color_code}</div>",
            unsafe_allow_html=True,
        )


st.set_page_config(page_title="Template Wizard", page_icon=":art:")

st.title("Template Wizard")

col1, col2 = st.columns([2, 1])
url = col1.text_input("URL: ", "")
col2.markdown(
    """
    <style>
        div.stButton > button:first-child {
            margin-bottom: 0px;
            height: 53px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
process_button = col2.button("Process")


if process_button or url:
    with st.spinner("Processing..."):
        colors = fetch_colors_from_url(url)
        print(colors)

        if colors:
            for color_name, color_codes in colors.items():
                display_colors(color_name, color_codes)
        else:
            st.write("Couldn't fetch the colors. Make sure the URL is correct.")
