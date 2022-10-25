import base64
import certifi
import openai
import pymongo
import streamlit as st
from pymongo.server_api import ServerApi
from utils import long_test

openai.api_key = st.secrets["API_KEY"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
GPT_MODEL = "text-davinci-002"  # text-ada-001
PDF_FILES = ["ethics.pdf", "skala_assaf.pdf", "validation.pdf", "test.pdf"]
CA = certifi.where()

client = pymongo.MongoClient(f"mongodb+srv://DanielSkala:{DB_PASSWORD}@digistudydemo.ih5ikoh"
                             f".mongodb.net/?retryWrites=true&w=majority", tlsCAFile=CA)
db = client["users"]
col = db["usage"]

apptitle = 'Digistudy'

st.set_page_config(page_title=apptitle, page_icon=":eyeglasses:", layout="wide")

client = pymongo.MongoClient(f"mongodb+srv://DanielSkala:{DB_PASSWORD}@digistudydemo.ih5ikoh"
                             f".mongodb.net/?retryWrites=true&w=majority",
                             server_api=ServerApi('1'))
db = client.test

st.markdown("## Welcome to Digistudy (DEMO)")
st.markdown("##### World's most advanced AI-powered study tool")

# SIDEBAR #
st.sidebar.image('img/logo.png', width=250)

uploaded_file = st.sidebar.file_uploader("Upload a pdf file (not supported yet)", type="pdf")

st.sidebar.markdown("Needed for authentication")
name = st.sidebar.text_input("Name")
surname = st.sidebar.text_input("Surname")

pdf_file_name = st.sidebar.selectbox("Select a pdf file (not supported yet)", PDF_FILES)

col1, col3 = st.columns(2)

with col1:
    # with open(f"files/{pdf_file_name}", "rb") as f:
    #     base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" ' \
        #               F'height="800" type="application/pdf"></iframe>'
    #     pdf_display = """
    #     <embed src="https://drive.google.com/viewerng/
    #     viewer?embedded=true&url=https://www.cartercenter.org/resources/pdfs/health/ephti/library/lecture_notes/health_extension_trainees/ln_intro_psych_final.pdf" width="700" height="800">
    #     """
    #
    # st.markdown(pdf_display, unsafe_allow_html=True)

    st.text_area("label", long_test, height=800, label_visibility="hidden")


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

    if button and name != "" and surname != "":
        user_id = name.capitalize() + surname.capitalize()
        with st.spinner('Generating...'):

            # Retrieve the mac address
            try:
                user_id = col.find_one({"_id": user_id})["_id"]
            except Exception:
                col.insert_one({"_id": user_id, "num_tokens": 0})
                st.info("New user detected. Please submit again.")

            curr_tokens = col.find_one({"_id": user_id})["num_tokens"]
            print(f"Current tokens: {curr_tokens}")
            if curr_tokens < 1000:

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
                col.update_one({"_id": user_id},
                               {"$set": {"num_tokens": curr_tokens + tokens_amt}})
                st.write(response["choices"][0]["text"])

                print(response)
            else:
                st.error("You have reached your limit of 1000 tokens. Contact "
                         "danko.skala@gmail.com to get more tokens.")

    elif button and (name == "" or surname == ""):
        st.error("Please enter your name and surname.")

st.markdown("---")
