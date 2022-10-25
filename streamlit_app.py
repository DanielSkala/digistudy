import base64
import os
import uuid

import certifi
import matplotlib as mpl
import openai
import pymongo
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg
# Make Plotly work in your Jupyter Notebook
from plotly.offline import init_notebook_mode
from pymongo.server_api import ServerApi

openai.api_key = os.getenv("API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")
GPT_MODEL = "text-davinci-002"  # text-ada-001
PDF_FILES = ["ethics.pdf", "skala_assaf.pdf", "validation.pdf", "test.pdf"]
MAC_ADDRESS = str(hex(uuid.getnode()))
CA = certifi.where()

client = pymongo.MongoClient(f"mongodb+srv://DanielSkala:{DB_PASSWORD}@digistudydemo.ih5ikoh"
                             f".mongodb.net/?retryWrites=true&w=majority", tlsCAFile=CA)
db = client["users"]
col = db["usage"]

init_notebook_mode(connected=True)
# Use Plotly locally

mpl.use("agg")

_lock = RendererAgg.lock

apptitle = 'Digistudy'

st.set_page_config(page_title=apptitle, page_icon=":eyeglasses:", layout="wide")

client = pymongo.MongoClient(f"mongodb+srv://DanielSkala:{DB_PASSWORD}@digistudydemo.ih5ikoh"
                             f".mongodb.net/?retryWrites=true&w=majority",
                             server_api=ServerApi('1'))
db = client.test

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.markdown("## Welcome to Digistudy")
st.markdown("##### World's most advanced AI-powered study tool")

# SIDEBAR #
st.sidebar.image('img/logo.png', width=250)

uploaded_file = st.sidebar.file_uploader("Upload a pdf file", type="pdf")
pdf_file_name = st.sidebar.selectbox("Select a pdf file", PDF_FILES)

st.sidebar.image('img/sidebar.png', width=250)

col1, col2, col3 = st.columns(3)

with col1:
    with open(f"files/{pdf_file_name}", "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" ' \
                  F'height="800" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_payload(text):
    kwargs = {
        "Summarize": {
            "model": GPT_MODEL,
            "prompt": f"Summarize this in 1-3 short sentences:\n\n{text}",
            "temperature": 0.7,
            "max_tokens": len(text.split()),
            "top_p": 1,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        },
        "Bullet points": {
            "model": GPT_MODEL,
            "prompt": f"Summarize this into exactly 3 complete bullet points followed by a "
                      f"newline:\n\n{text}",
            "temperature": 0.7,
            "max_tokens": 100,
            "top_p": 1,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0},
        "Explain to a child": {
            "model": GPT_MODEL,
            "prompt": f"Summarize this for a second-grade student (using very "
                      f"simple language):\n\n{text}",
            "temperature": 0.8,
            "max_tokens": 100,
            "top_p": 1,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.0},
        "Give an example": {
            "model": GPT_MODEL,
            "prompt": f"Give a real world example on the following concept:\n\n{text}",
            "temperature": 0.7,
            "max_tokens": 100,
            "top_p": 1,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.0},
        "Chat with AI": {
            "model": GPT_MODEL,
            "prompt": f"The following is an intimate conversation between a student "
                      f"and AI:\n\n{text}",
            "temperature": 1.0,
            "max_tokens": 64,
            "top_p": 1,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.0
        }
    }
    return kwargs


with col3:
    functions = ["Summarize", "Bullet points", "Explain to a child", "Give an example",
                 "Chat with AI"]
    prompt = st.selectbox('Select a function', functions)

    # create a text input field
    text = st.text_area('Enter text', height=300, help="Copy-paste text from the pdf, select "
                                                       "a function to apply and click on submit.")

    # create a button
    button = st.button('Submit')

    if button:
        with st.spinner('Generating...'):

            # Retrieve the mac address
            try:
                address = col.find_one({"_id": MAC_ADDRESS})["_id"]
            except Exception:
                col.insert_one({"_id": MAC_ADDRESS, "num_tokens": 0})
                st.info("New user detected. Please submit again.")

            curr_tokens = col.find_one({"_id": address})["num_tokens"]
            print(f"Current tokens: {curr_tokens}")
            if curr_tokens < 100:

                kwargs = get_payload(text)[prompt]
                response = openai.Completion.create(
                    model=kwargs["model"],
                    prompt=kwargs["prompt"],
                    temperature=kwargs["temperature"],
                    max_tokens=kwargs["max_tokens"],
                    top_p=kwargs["top_p"],
                    frequency_penalty=kwargs["frequency_penalty"],
                    presence_penalty=kwargs["presence_penalty"]
                )
                tokens_amt = len(response["choices"][0]["text"].split())
                col.update_one({"_id": address},
                               {"$set": {"num_tokens": curr_tokens + tokens_amt}})
                st.write(response["choices"][0]["text"])

                print(response)
            else:
                st.error("You have reached your limit of 200 tokens.")

st.markdown("---")
