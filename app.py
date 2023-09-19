import logging

import streamlit as st
from dotenv import load_dotenv

from apply_writing_style import apply_writing_style
from get_design_from_source import fetch_colors_from_url, is_valid_url

load_dotenv()
logger = logging.getLogger(__name__)


def display_colors(color_name, color_codes):
    st.write(f"**{color_name}:**")

    col1, col2, col3, col4 = st.columns(4)

    for i, color_code in enumerate(color_codes):
        with [col1, col2, col3, col4][i % 4]:
            st.markdown(
                f"<div style='width: 70px; height: 70px; background: {color_code};'></div>"
                f"<div style='margin-left: 10px;'>{color_code}</div>",
                unsafe_allow_html=True,
            )


st.set_page_config(page_title="Template Wizard", page_icon=":art:")

st.title("Template Wizard")
st.header("Section 1: Design Analysis")


col1, col2 = st.columns([2, 1])
url = col1.text_input("URL: ")
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
process_button = col2.button("Analyze design")


if process_button or is_valid_url(url):
    with st.spinner("Processing..."):
        colors = fetch_colors_from_url(url)
        print("colors : ", colors)

        if colors:
            for color_name, color_codes in colors.items():
                if "color" in color_name:
                    display_colors(color_name, color_codes)

            st.write("**Primary font:**")
            st.write(colors.get("primary_font", ["Not available"])[0])

            st.write("**Secondary font:**")
            st.write(colors.get("secondary_font", ["Not available"])[0])

        else:
            st.write("Couldn't fetch the colors. Make sure the URL is correct.")


st.header("Section 2: Applying Writing Style")
email_to_rewrite_placeholder = """THE MOMENT MY CLIENTS DISCOVER THEIR TRUE POTENTIAL - THAT'S WHAT DRIVES ME
I recently spoke at the Modern Entrepreneur conference. The weeks leading up to the event were filled with preparation. I crafted the perfect presentation and memorized every word of my keynote. I was ready, or, so thought...

At the end of my session, I opened up the room for questions. A young lady in the front row stood up and asked "what inspires you?". Three words and such a simple question, right? I felt a rush of nerves run through me as scrambled to piece together an answer. The truth is, I've never asked myself this before. And in that moment I unveiled a disconnect between my passion and my pursuit. What fuels me to show up and help fellow business owners? put a kabosh on the rest of my plans for the week. No to-do list, no phone apps, all alarms off, and deadlines on the backburner. I dug deep, asking myself the tough questions. I realized it's not the paychecks, shiny reviews, or social media following that pulls me toward this path. The moment my clients discover their true potential-that's what drives me."""
email_to_rewrite = st.text_area(
    "Email to Rewrite:", email_to_rewrite_placeholder, height=300
)
url_for_writing_style = st.text_input("Your article URL")

rewrite_button = st.button("Apply writing style")

if rewrite_button and email_to_rewrite:
    with st.spinner("Processing..."):
        rewritten_email = apply_writing_style(email_to_rewrite, url_for_writing_style)
        st.write("Rewritten Email Template:")
        st.write(rewritten_email)
elif rewrite_button:
    st.write("Please enter an email to rewrite.")
