import pathlib
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO
import base64
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
import subprocess
import streamlit_antd_components as sac
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text

# Page configuration
st.set_page_config(
    page_title="Grammar Guide", 
    layout="wide",
    page_icon="🧊",
    initial_sidebar_state="expanded"
    )

CURRENT_THEME = "dark"
IS_LIGHT_THEME = False
EXPANDER_TEXT = """
    This is Streamlit's default *Light* theme. It should be enabled by default 🎈
    If not, you can enable it in the app menu (☰ -> Settings -> Theme).
    """

THEMES = [
    "light",
    "dark",
]


# Function to load CSS from the 'assets' folder
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Load the external CSS
css_path = pathlib.Path("assets/styles.css")
load_css(css_path)

hide_st_style = """
<style>
[data-testid="stAppViewContainer"]{
 
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center center;
  background-repeat: repeat;
  background-image: url("data:image/svg+xml;utf8,%3Csvg viewBox=%220 0 2000 1125%22 xmlns=%22http:%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cmask id=%22b%22 x=%220%22 y=%220%22 width=%222000%22 height=%221125%22%3E%3Cpath fill=%22url(%23a)%22 d=%22M0 0h2000v1125H0z%22%2F%3E%3C%2Fmask%3E%3Cpath d=%22M0 0h2000v1125H0z%22%2F%3E%3Cg mask=%22url(%23b)%22%3E%3Cg style=%22transform-origin:center center%22%3E%3Ccircle cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff0a%22%2F%3E%3Ccircle cx=%2275%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffea%22%2F%3E%3Ccircle cx=%22150%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff0e%22%2F%3E%3Ccircle cx=%22225%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff5f%22%2F%3E%3Ccircle cx=%22300%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffda%22%2F%3E%3Ccircle cx=%22375%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff95%22%2F%3E%3Ccircle cx=%22450%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffe0%22%2F%3E%3Ccircle cx=%22525%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff2c%22%2F%3E%3Ccircle cx=%22600%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffc9%22%2F%3E%3Ccircle cx=%22675%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffa0%22%2F%3E%3Ccircle cx=%22750%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff97%22%2F%3E%3Ccircle cx=%22825%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffb5%22%2F%3E%3Ccircle cx=%22900%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffff%22%2F%3E%3Ccircle cx=%22975%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffc9%22%2F%3E%3Ccircle cx=%221050%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffae%22%2F%3E%3Ccircle cx=%221125%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff6e%22%2F%3E%3Ccircle cx=%221200%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffbf%22%2F%3E%3Ccircle cx=%221275%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff99%22%2F%3E%3Ccircle cx=%221350%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23fffffff7%22%2F%3E%3Ccircle cx=%221425%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff4d%22%2F%3E%3Ccircle cx=%221500%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff03%22%2F%3E%3Ccircle cx=%221575%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff4e%22%2F%3E%3Ccircle cx=%221650%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff05%22%2F%3E%3Ccircle cx=%221725%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff11%22%2F%3E%3Ccircle cx=%221800%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff53%22%2F%3E%3Ccircle cx=%221875%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffa7%22%2F%3E%3Ccircle cx=%221950%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffffb7%22%2F%3E%3Ccircle cx=%222025%22 cy=%2237.5%22 r=%222.8%22 fill=%22%23ffffff09%22%2F%3E%3Ccircle cx=%2237.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffffe5%22%2F%3E%3Ccircle cx=%22112.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffffe2%22%2F%3E%3Ccircle cx=%22187.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff54%22%2F%3E%3Ccircle cx=%22262.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff37%22%2F%3E%3Ccircle cx=%22337.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffffe8%22%2F%3E%3Ccircle cx=%22412.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff67%22%2F%3E%3Ccircle cx=%22487.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff3b%22%2F%3E%3Ccircle cx=%22562.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff5f%22%2F%3E%3Ccircle cx=%22637.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffffc3%22%2F%3E%3Ccircle cx=%22712.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff1d%22%2F%3E%3Ccircle cx=%22787.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff61%22%2F%3E%3Ccircle cx=%22862.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff0e%22%2F%3E%3Ccircle cx=%22937.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff3c%22%2F%3E%3Ccircle cx=%221012.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff3d%22%2F%3E%3Ccircle cx=%221087.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23fffffffd%22%2F%3E%3Ccircle cx=%221162.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff6b%22%2F%3E%3Ccircle cx=%221237.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffffe0%22%2F%3E%3Ccircle cx=%221312.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff67%22%2F%3E%3Ccircle cx=%221387.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff64%22%2F%3E%3Ccircle cx=%221462.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff3e%22%2F%3E%3Ccircle cx=%221537.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff1b%22%2F%3E%3Ccircle cx=%221612.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffffe4%22%2F%3E%3Ccircle cx=%221687.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff3e%22%2F%3E%3Ccircle cx=%221762.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffffa6%22%2F%3E%3Ccircle cx=%221837.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff50%22%2F%3E%3Ccircle cx=%221912.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff93%22%2F%3E%3Ccircle cx=%221987.5%22 cy=%22112.5%22 r=%222.8%22 fill=%22%23ffffff6a%22%2F%3E%3Ccircle cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffdf%22%2F%3E%3Ccircle cx=%2275%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffa7%22%2F%3E%3Ccircle cx=%22150%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff57%22%2F%3E%3Ccircle cx=%22225%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff5c%22%2F%3E%3Ccircle cx=%22300%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffe9%22%2F%3E%3Ccircle cx=%22375%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffcf%22%2F%3E%3Ccircle cx=%22450%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffa1%22%2F%3E%3Ccircle cx=%22525%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff29%22%2F%3E%3Ccircle cx=%22600%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffef%22%2F%3E%3Ccircle cx=%22675%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffa2%22%2F%3E%3Ccircle cx=%22750%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff50%22%2F%3E%3Ccircle cx=%22825%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23fffffffc%22%2F%3E%3Ccircle cx=%22900%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff32%22%2F%3E%3Ccircle cx=%22975%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffc5%22%2F%3E%3Ccircle cx=%221050%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff67%22%2F%3E%3Ccircle cx=%221125%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffcc%22%2F%3E%3Ccircle cx=%221200%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffc8%22%2F%3E%3Ccircle cx=%221275%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffc5%22%2F%3E%3Ccircle cx=%221350%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff7d%22%2F%3E%3Ccircle cx=%221425%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffeb%22%2F%3E%3Ccircle cx=%221500%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff63%22%2F%3E%3Ccircle cx=%221575%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff84%22%2F%3E%3Ccircle cx=%221650%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff19%22%2F%3E%3Ccircle cx=%221725%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffea%22%2F%3E%3Ccircle cx=%221800%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffff16%22%2F%3E%3Ccircle cx=%221875%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffa1%22%2F%3E%3Ccircle cx=%221950%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffd2%22%2F%3E%3Ccircle cx=%222025%22 cy=%22187.5%22 r=%222.8%22 fill=%22%23ffffffa0%22%2F%3E%3Ccircle cx=%2237.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff38%22%2F%3E%3Ccircle cx=%22112.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff06%22%2F%3E%3Ccircle cx=%22187.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff6b%22%2F%3E%3Ccircle cx=%22262.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff46%22%2F%3E%3Ccircle cx=%22337.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff95%22%2F%3E%3Ccircle cx=%22412.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffc6%22%2F%3E%3Ccircle cx=%22487.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff3c%22%2F%3E%3Ccircle cx=%22562.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff19%22%2F%3E%3Ccircle cx=%22637.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffb9%22%2F%3E%3Ccircle cx=%22712.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffa3%22%2F%3E%3Ccircle cx=%22787.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff30%22%2F%3E%3Ccircle cx=%22862.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffdd%22%2F%3E%3Ccircle cx=%22937.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffd9%22%2F%3E%3Ccircle cx=%221012.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffc8%22%2F%3E%3Ccircle cx=%221087.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff80%22%2F%3E%3Ccircle cx=%221162.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff9d%22%2F%3E%3Ccircle cx=%221237.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffa3%22%2F%3E%3Ccircle cx=%221312.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffd7%22%2F%3E%3Ccircle cx=%221387.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffc9%22%2F%3E%3Ccircle cx=%221462.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff30%22%2F%3E%3Ccircle cx=%221537.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffb4%22%2F%3E%3Ccircle cx=%221612.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff83%22%2F%3E%3Ccircle cx=%221687.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffff99%22%2F%3E%3Ccircle cx=%221762.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffb0%22%2F%3E%3Ccircle cx=%221837.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffc5%22%2F%3E%3Ccircle cx=%221912.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23ffffffe7%22%2F%3E%3Ccircle cx=%221987.5%22 cy=%22262.5%22 r=%222.8%22 fill=%22%23fffffffd%22%2F%3E%3Ccircle cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff28%22%2F%3E%3Ccircle cx=%2275%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff6d%22%2F%3E%3Ccircle cx=%22150%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffa8%22%2F%3E%3Ccircle cx=%22225%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff2d%22%2F%3E%3Ccircle cx=%22300%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff38%22%2F%3E%3Ccircle cx=%22375%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffd4%22%2F%3E%3Ccircle cx=%22450%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffe1%22%2F%3E%3Ccircle cx=%22525%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffad%22%2F%3E%3Ccircle cx=%22600%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff76%22%2F%3E%3Ccircle cx=%22675%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff4e%22%2F%3E%3Ccircle cx=%22750%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff08%22%2F%3E%3Ccircle cx=%22825%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffae%22%2F%3E%3Ccircle cx=%22900%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff80%22%2F%3E%3Ccircle cx=%22975%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff35%22%2F%3E%3Ccircle cx=%221050%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffaa%22%2F%3E%3Ccircle cx=%221125%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffd5%22%2F%3E%3Ccircle cx=%221200%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffd2%22%2F%3E%3Ccircle cx=%221275%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff42%22%2F%3E%3Ccircle cx=%221350%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23fffffff8%22%2F%3E%3Ccircle cx=%221425%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff6f%22%2F%3E%3Ccircle cx=%221500%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff28%22%2F%3E%3Ccircle cx=%221575%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff24%22%2F%3E%3Ccircle cx=%221650%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff81%22%2F%3E%3Ccircle cx=%221725%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff6c%22%2F%3E%3Ccircle cx=%221800%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffa2%22%2F%3E%3Ccircle cx=%221875%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffc8%22%2F%3E%3Ccircle cx=%221950%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffff76%22%2F%3E%3Ccircle cx=%222025%22 cy=%22337.5%22 r=%222.8%22 fill=%22%23ffffffd0%22%2F%3E%3Ccircle cx=%2237.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23fffffffc%22%2F%3E%3Ccircle cx=%22112.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff7c%22%2F%3E%3Ccircle cx=%22187.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff1c%22%2F%3E%3Ccircle cx=%22262.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff29%22%2F%3E%3Ccircle cx=%22337.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff45%22%2F%3E%3Ccircle cx=%22412.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffffea%22%2F%3E%3Ccircle cx=%22487.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff76%22%2F%3E%3Ccircle cx=%22562.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffffd8%22%2F%3E%3Ccircle cx=%22637.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff2b%22%2F%3E%3Ccircle cx=%22712.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffffcd%22%2F%3E%3Ccircle cx=%22787.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff64%22%2F%3E%3Ccircle cx=%22862.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff72%22%2F%3E%3Ccircle cx=%22937.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff98%22%2F%3E%3Ccircle cx=%221012.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff50%22%2F%3E%3Ccircle cx=%221087.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff53%22%2F%3E%3Ccircle cx=%221162.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff00%22%2F%3E%3Ccircle cx=%221237.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffffdc%22%2F%3E%3Ccircle cx=%221312.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff58%22%2F%3E%3Ccircle cx=%221387.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffffdb%22%2F%3E%3Ccircle cx=%221462.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff32%22%2F%3E%3Ccircle cx=%221537.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff6d%22%2F%3E%3Ccircle cx=%221612.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff73%22%2F%3E%3Ccircle cx=%221687.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff75%22%2F%3E%3Ccircle cx=%221762.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffff5b%22%2F%3E%3Ccircle cx=%221837.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23fffffff0%22%2F%3E%3Ccircle cx=%221912.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffffce%22%2F%3E%3Ccircle cx=%221987.5%22 cy=%22412.5%22 r=%222.8%22 fill=%22%23ffffffed%22%2F%3E%3Ccircle cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff49%22%2F%3E%3Ccircle cx=%2275%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff21%22%2F%3E%3Ccircle cx=%22150%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff87%22%2F%3E%3Ccircle cx=%22225%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff82%22%2F%3E%3Ccircle cx=%22300%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff7d%22%2F%3E%3Ccircle cx=%22375%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffb6%22%2F%3E%3Ccircle cx=%22450%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23fffffff3%22%2F%3E%3Ccircle cx=%22525%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff0a%22%2F%3E%3Ccircle cx=%22600%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff5f%22%2F%3E%3Ccircle cx=%22675%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff66%22%2F%3E%3Ccircle cx=%22750%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff1f%22%2F%3E%3Ccircle cx=%22825%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff57%22%2F%3E%3Ccircle cx=%22900%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffdc%22%2F%3E%3Ccircle cx=%22975%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff04%22%2F%3E%3Ccircle cx=%221050%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffa5%22%2F%3E%3Ccircle cx=%221125%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff7c%22%2F%3E%3Ccircle cx=%221200%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff04%22%2F%3E%3Ccircle cx=%221275%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffd7%22%2F%3E%3Ccircle cx=%221350%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffb0%22%2F%3E%3Ccircle cx=%221425%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffc9%22%2F%3E%3Ccircle cx=%221500%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffeb%22%2F%3E%3Ccircle cx=%221575%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff53%22%2F%3E%3Ccircle cx=%221650%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffb2%22%2F%3E%3Ccircle cx=%221725%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffb8%22%2F%3E%3Ccircle cx=%221800%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff7c%22%2F%3E%3Ccircle cx=%221875%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff51%22%2F%3E%3Ccircle cx=%221950%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffffa2%22%2F%3E%3Ccircle cx=%222025%22 cy=%22487.5%22 r=%222.8%22 fill=%22%23ffffff0e%22%2F%3E%3Ccircle cx=%2237.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffe7%22%2F%3E%3Ccircle cx=%22112.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff24%22%2F%3E%3Ccircle cx=%22187.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffb2%22%2F%3E%3Ccircle cx=%22262.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff98%22%2F%3E%3Ccircle cx=%22337.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff61%22%2F%3E%3Ccircle cx=%22412.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff72%22%2F%3E%3Ccircle cx=%22487.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff7f%22%2F%3E%3Ccircle cx=%22562.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff69%22%2F%3E%3Ccircle cx=%22637.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff32%22%2F%3E%3Ccircle cx=%22712.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffc7%22%2F%3E%3Ccircle cx=%22787.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff6c%22%2F%3E%3Ccircle cx=%22862.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffce%22%2F%3E%3Ccircle cx=%22937.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff15%22%2F%3E%3Ccircle cx=%221012.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff8b%22%2F%3E%3Ccircle cx=%221087.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff4c%22%2F%3E%3Ccircle cx=%221162.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffd4%22%2F%3E%3Ccircle cx=%221237.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff72%22%2F%3E%3Ccircle cx=%221312.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff88%22%2F%3E%3Ccircle cx=%221387.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffcd%22%2F%3E%3Ccircle cx=%221462.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff6d%22%2F%3E%3Ccircle cx=%221537.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffec%22%2F%3E%3Ccircle cx=%221612.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffffdc%22%2F%3E%3Ccircle cx=%221687.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff94%22%2F%3E%3Ccircle cx=%221762.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff7b%22%2F%3E%3Ccircle cx=%221837.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff2d%22%2F%3E%3Ccircle cx=%221912.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff1b%22%2F%3E%3Ccircle cx=%221987.5%22 cy=%22562.5%22 r=%222.8%22 fill=%22%23ffffff9f%22%2F%3E%3Ccircle cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff69%22%2F%3E%3Ccircle cx=%2275%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffc1%22%2F%3E%3Ccircle cx=%22150%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23fffffff2%22%2F%3E%3Ccircle cx=%22225%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff01%22%2F%3E%3Ccircle cx=%22300%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff46%22%2F%3E%3Ccircle cx=%22375%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffcb%22%2F%3E%3Ccircle cx=%22450%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffd7%22%2F%3E%3Ccircle cx=%22525%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffb5%22%2F%3E%3Ccircle cx=%22600%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff4b%22%2F%3E%3Ccircle cx=%22675%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffec%22%2F%3E%3Ccircle cx=%22750%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffbe%22%2F%3E%3Ccircle cx=%22825%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffba%22%2F%3E%3Ccircle cx=%22900%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23fffffffd%22%2F%3E%3Ccircle cx=%22975%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff22%22%2F%3E%3Ccircle cx=%221050%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff85%22%2F%3E%3Ccircle cx=%221125%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff2f%22%2F%3E%3Ccircle cx=%221200%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff0b%22%2F%3E%3Ccircle cx=%221275%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff87%22%2F%3E%3Ccircle cx=%221350%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffa2%22%2F%3E%3Ccircle cx=%221425%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff53%22%2F%3E%3Ccircle cx=%221500%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff6b%22%2F%3E%3Ccircle cx=%221575%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff23%22%2F%3E%3Ccircle cx=%221650%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff75%22%2F%3E%3Ccircle cx=%221725%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff7f%22%2F%3E%3Ccircle cx=%221800%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffd6%22%2F%3E%3Ccircle cx=%221875%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff13%22%2F%3E%3Ccircle cx=%221950%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffffb8%22%2F%3E%3Ccircle cx=%222025%22 cy=%22637.5%22 r=%222.8%22 fill=%22%23ffffff0c%22%2F%3E%3Ccircle cx=%2237.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffa0%22%2F%3E%3Ccircle cx=%22112.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffec%22%2F%3E%3Ccircle cx=%22187.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff54%22%2F%3E%3Ccircle cx=%22262.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffd0%22%2F%3E%3Ccircle cx=%22337.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffa0%22%2F%3E%3Ccircle cx=%22412.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff72%22%2F%3E%3Ccircle cx=%22487.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff36%22%2F%3E%3Ccircle cx=%22562.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffa3%22%2F%3E%3Ccircle cx=%22637.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23fffffffb%22%2F%3E%3Ccircle cx=%22712.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff64%22%2F%3E%3Ccircle cx=%22787.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff3f%22%2F%3E%3Ccircle cx=%22862.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff96%22%2F%3E%3Ccircle cx=%22937.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff92%22%2F%3E%3Ccircle cx=%221012.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff77%22%2F%3E%3Ccircle cx=%221087.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffc8%22%2F%3E%3Ccircle cx=%221162.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff46%22%2F%3E%3Ccircle cx=%221237.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23fffffffd%22%2F%3E%3Ccircle cx=%221312.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff4f%22%2F%3E%3Ccircle cx=%221387.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffca%22%2F%3E%3Ccircle cx=%221462.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23fffffff0%22%2F%3E%3Ccircle cx=%221537.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffb8%22%2F%3E%3Ccircle cx=%221612.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff08%22%2F%3E%3Ccircle cx=%221687.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffbb%22%2F%3E%3Ccircle cx=%221762.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff2c%22%2F%3E%3Ccircle cx=%221837.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff57%22%2F%3E%3Ccircle cx=%221912.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffffab%22%2F%3E%3Ccircle cx=%221987.5%22 cy=%22712.5%22 r=%222.8%22 fill=%22%23ffffff42%22%2F%3E%3Ccircle cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff69%22%2F%3E%3Ccircle cx=%2275%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffc7%22%2F%3E%3Ccircle cx=%22150%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff5d%22%2F%3E%3Ccircle cx=%22225%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff23%22%2F%3E%3Ccircle cx=%22300%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff8e%22%2F%3E%3Ccircle cx=%22375%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23fffffffa%22%2F%3E%3Ccircle cx=%22450%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff19%22%2F%3E%3Ccircle cx=%22525%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23fffffffc%22%2F%3E%3Ccircle cx=%22600%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffb2%22%2F%3E%3Ccircle cx=%22675%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffc1%22%2F%3E%3Ccircle cx=%22750%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffd7%22%2F%3E%3Ccircle cx=%22825%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffab%22%2F%3E%3Ccircle cx=%22900%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff43%22%2F%3E%3Ccircle cx=%22975%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffcd%22%2F%3E%3Ccircle cx=%221050%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff2a%22%2F%3E%3Ccircle cx=%221125%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffed%22%2F%3E%3Ccircle cx=%221200%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff1e%22%2F%3E%3Ccircle cx=%221275%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffa0%22%2F%3E%3Ccircle cx=%221350%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff76%22%2F%3E%3Ccircle cx=%221425%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff64%22%2F%3E%3Ccircle cx=%221500%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffc5%22%2F%3E%3Ccircle cx=%221575%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff95%22%2F%3E%3Ccircle cx=%221650%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffda%22%2F%3E%3Ccircle cx=%221725%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffffb9%22%2F%3E%3Ccircle cx=%221800%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff86%22%2F%3E%3Ccircle cx=%221875%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff90%22%2F%3E%3Ccircle cx=%221950%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff4c%22%2F%3E%3Ccircle cx=%222025%22 cy=%22787.5%22 r=%222.8%22 fill=%22%23ffffff28%22%2F%3E%3Ccircle cx=%2237.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff2e%22%2F%3E%3Ccircle cx=%22112.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff47%22%2F%3E%3Ccircle cx=%22187.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23fffffff1%22%2F%3E%3Ccircle cx=%22262.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff31%22%2F%3E%3Ccircle cx=%22337.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff94%22%2F%3E%3Ccircle cx=%22412.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff21%22%2F%3E%3Ccircle cx=%22487.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffb4%22%2F%3E%3Ccircle cx=%22562.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff14%22%2F%3E%3Ccircle cx=%22637.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff11%22%2F%3E%3Ccircle cx=%22712.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffbd%22%2F%3E%3Ccircle cx=%22787.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff68%22%2F%3E%3Ccircle cx=%22862.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffc2%22%2F%3E%3Ccircle cx=%22937.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff3a%22%2F%3E%3Ccircle cx=%221012.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff4a%22%2F%3E%3Ccircle cx=%221087.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff48%22%2F%3E%3Ccircle cx=%221162.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff9d%22%2F%3E%3Ccircle cx=%221237.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffab%22%2F%3E%3Ccircle cx=%221312.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffc6%22%2F%3E%3Ccircle cx=%221387.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff3c%22%2F%3E%3Ccircle cx=%221462.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff90%22%2F%3E%3Ccircle cx=%221537.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffae%22%2F%3E%3Ccircle cx=%221612.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff5e%22%2F%3E%3Ccircle cx=%221687.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff80%22%2F%3E%3Ccircle cx=%221762.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffc3%22%2F%3E%3Ccircle cx=%221837.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffbc%22%2F%3E%3Ccircle cx=%221912.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffffcd%22%2F%3E%3Ccircle cx=%221987.5%22 cy=%22862.5%22 r=%222.8%22 fill=%22%23ffffff04%22%2F%3E%3Ccircle cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff56%22%2F%3E%3Ccircle cx=%2275%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffb9%22%2F%3E%3Ccircle cx=%22150%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff99%22%2F%3E%3Ccircle cx=%22225%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff4e%22%2F%3E%3Ccircle cx=%22300%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffa4%22%2F%3E%3Ccircle cx=%22375%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffdf%22%2F%3E%3Ccircle cx=%22450%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff73%22%2F%3E%3Ccircle cx=%22525%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff07%22%2F%3E%3Ccircle cx=%22600%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff09%22%2F%3E%3Ccircle cx=%22675%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff6b%22%2F%3E%3Ccircle cx=%22750%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffb1%22%2F%3E%3Ccircle cx=%22825%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff25%22%2F%3E%3Ccircle cx=%22900%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffdb%22%2F%3E%3Ccircle cx=%22975%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffe2%22%2F%3E%3Ccircle cx=%221050%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff2f%22%2F%3E%3Ccircle cx=%221125%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffb5%22%2F%3E%3Ccircle cx=%221200%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff0b%22%2F%3E%3Ccircle cx=%221275%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff77%22%2F%3E%3Ccircle cx=%221350%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff67%22%2F%3E%3Ccircle cx=%221425%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23fffffff3%22%2F%3E%3Ccircle cx=%221500%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff29%22%2F%3E%3Ccircle cx=%221575%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff91%22%2F%3E%3Ccircle cx=%221650%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff2a%22%2F%3E%3Ccircle cx=%221725%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffa5%22%2F%3E%3Ccircle cx=%221800%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffffc4%22%2F%3E%3Ccircle cx=%221875%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff26%22%2F%3E%3Ccircle cx=%221950%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff72%22%2F%3E%3Ccircle cx=%222025%22 cy=%22937.5%22 r=%222.8%22 fill=%22%23ffffff8f%22%2F%3E%3Ccircle cx=%2237.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffaf%22%2F%3E%3Ccircle cx=%22112.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff11%22%2F%3E%3Ccircle cx=%22187.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffd0%22%2F%3E%3Ccircle cx=%22262.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff57%22%2F%3E%3Ccircle cx=%22337.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff67%22%2F%3E%3Ccircle cx=%22412.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffc0%22%2F%3E%3Ccircle cx=%22487.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffe4%22%2F%3E%3Ccircle cx=%22562.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffe1%22%2F%3E%3Ccircle cx=%22637.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffbc%22%2F%3E%3Ccircle cx=%22712.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff53%22%2F%3E%3Ccircle cx=%22787.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff36%22%2F%3E%3Ccircle cx=%22862.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffe9%22%2F%3E%3Ccircle cx=%22937.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffa3%22%2F%3E%3Ccircle cx=%221012.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff11%22%2F%3E%3Ccircle cx=%221087.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff20%22%2F%3E%3Ccircle cx=%221162.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffad%22%2F%3E%3Ccircle cx=%221237.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffc7%22%2F%3E%3Ccircle cx=%221312.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff05%22%2F%3E%3Ccircle cx=%221387.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffffa6%22%2F%3E%3Ccircle cx=%221462.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff77%22%2F%3E%3Ccircle cx=%221537.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff2e%22%2F%3E%3Ccircle cx=%221612.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff69%22%2F%3E%3Ccircle cx=%221687.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff45%22%2F%3E%3Ccircle cx=%221762.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff21%22%2F%3E%3Ccircle cx=%221837.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff8d%22%2F%3E%3Ccircle cx=%221912.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff01%22%2F%3E%3Ccircle cx=%221987.5%22 cy=%221012.5%22 r=%222.8%22 fill=%22%23ffffff2b%22%2F%3E%3Ccircle cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff2c%22%2F%3E%3Ccircle cx=%2275%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff1d%22%2F%3E%3Ccircle cx=%22150%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffd8%22%2F%3E%3Ccircle cx=%22225%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff0a%22%2F%3E%3Ccircle cx=%22300%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff72%22%2F%3E%3Ccircle cx=%22375%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23fffffffc%22%2F%3E%3Ccircle cx=%22450%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff5e%22%2F%3E%3Ccircle cx=%22525%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffdc%22%2F%3E%3Ccircle cx=%22600%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffc1%22%2F%3E%3Ccircle cx=%22675%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff32%22%2F%3E%3Ccircle cx=%22750%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffa8%22%2F%3E%3Ccircle cx=%22825%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff66%22%2F%3E%3Ccircle cx=%22900%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff11%22%2F%3E%3Ccircle cx=%22975%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffa1%22%2F%3E%3Ccircle cx=%221050%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff42%22%2F%3E%3Ccircle cx=%221125%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffbc%22%2F%3E%3Ccircle cx=%221200%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23fffffffe%22%2F%3E%3Ccircle cx=%221275%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff7f%22%2F%3E%3Ccircle cx=%221350%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffdd%22%2F%3E%3Ccircle cx=%221425%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff50%22%2F%3E%3Ccircle cx=%221500%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffd0%22%2F%3E%3Ccircle cx=%221575%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffffcb%22%2F%3E%3Ccircle cx=%221650%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff97%22%2F%3E%3Ccircle cx=%221725%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff9b%22%2F%3E%3Ccircle cx=%221800%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff95%22%2F%3E%3Ccircle cx=%221875%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff26%22%2F%3E%3Ccircle cx=%221950%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff62%22%2F%3E%3Ccircle cx=%222025%22 cy=%221087.5%22 r=%222.8%22 fill=%22%23ffffff4e%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3Cdefs%3E%3CradialGradient id=%22a%22%3E%3Cstop offset=%2256.8%25%22 stop-color=%22%23fff%22 stop-opacity=%220%22%2F%3E%3Cstop offset=%22100%25%22 stop-color=%22%23fff%22 stop-opacity=%22.432%22%2F%3E%3C%2FradialGradient%3E%3C%2Fdefs%3E%3C%2Fsvg%3E");
}

</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found! Please check your .env file")
    st.stop()
client = OpenAI(api_key=api_key)

def stream_response(messages):
    """Generator for streaming API responses"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True
        )

        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"An error occurred: {str(e)}"

def get_grammar_help(topic, question):
    """Get guided help without direct answers"""
    system_msg = """You are a Socratic grammar tutor. Help students think through problems by:
    - Asking 2-3 guiding questions
    - Providing hints and patterns instead of answers
    - Breaking problems into smaller steps
    - Providing partial examples to require completion
    - Encouraging self-discovery
    - Never providing complete solutions or direct answers"""
    
    user_prompt = f"""Student needs help with {topic}. Their question: {question}
    Guide them to find the answer themselves using these techniques:
    1. Ask questions about what they've tried
    2. Identify patterns in similar problems
    3. Provide incomplete examples to complete
    4. Suggest resources for self-checking
    5. Highlight key concepts to focus on
    Never give the direct answer or full solution!"""

    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ])

def analyze_grammar(text):
    """Analyze text for grammatical errors and provide guided correction help"""
    system_msg = """You are a meticulous grammar coach. Follow these steps:
    1. Identify 3-5 grammatical errors in the text
    2. Categorize each error (e.g., tense, punctuation, voice)
    3. Explain why it's incorrect using simple terms
    4. Ask a guiding question to help correct it
    5. Never show the corrected version
    6. Prioritize serious errors over minor ones
    7. Use examples where helpful"""
    
    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Analyze this text:\n{text}"}
    ])

def get_direct_answer_home(topic, question):
    """Get direct answer for home page questions"""
    system_msg = """You are a helpful grammar tutor that provides direct answers and clear explanations."""
    user_prompt = f"Provide a direct answer and detailed explanation for the student's question about {topic}: {question}"
    
    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ])

def get_direct_answer_analysis(text):
    """Get direct corrections for analysis page text"""
    system_msg = """You are a meticulous writing coach. Provide a corrected version of the user's text with detailed explanations of each change made. Format your response with the corrected text followed by bullet points explaining each correction."""
    user_prompt = f"Text to correct and explain:\n{text}"
    
    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ])

def generate_image(prompt):
    """Generate image using DALL·E"""
    try:
        response = client.images.generate(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="url"
        )
        return response.data[0].url
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Initialize session state for page navigation and answer tracking
if 'page' not in st.session_state:
    st.session_state.page = '📚 Grammar Concept Helper'
if 'home_initial' not in st.session_state:
    st.session_state.home_initial = False
if 'analysis_initial' not in st.session_state:
    st.session_state.analysis_initial = False

# Sidebar navigation
with st.sidebar:
    pages = ["📚 Grammar Concept Helper", "✍️ Analyze My Writing", "🎨 Generate Image", "🗣️ Socratic Tutor"]
    selected_index = sac.segmented(
        items=[
            sac.SegmentedItem(label='📚 Grammar Concept Helper'),
            sac.SegmentedItem(label='✍️ Analyze My Writing'),
            sac.SegmentedItem(label='🎨 Generate Image'),
            sac.SegmentedItem(label='🗣️ Socratic Tutor'),
        ], 
        label='',
        index=["📚 Grammar Concept Helper", "✍️ Analyze My Writing", "🎨 Generate Image", "🗣️ Socratic Tutor"].index(st.session_state.page),  
        align='center', 
        direction='vertical', 
        size='xl', 
        radius='xs', 
        color='rgb(20,80,90)', 
        divider=False,
        key='nav_segmented'
    )
    st.session_state.page = selected_index

# Home Page - Grammar Concept Helper
if st.session_state.page == "📚 Grammar Concept Helper":
    st.title("📚 Grammar Concept Helper")
    st.markdown("""
<div class="custom-markdown">
Welcome to your personal grammar tutor!
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    topic = st.selectbox(
        "Select Grammar Topic",
        options=["Story Writing", "Essay Writing", "Tenses", "Active/Passive Voice", "Other"]
    )
    user_question = st.text_area("Your Question/Prompt:", 
                           height=150, 
                           key="styledtextarea")

    if st.button("Get Help", key="pulse"):
        if user_question.strip() == "":
            st.warning("Please enter your question first!")
        else:
            st.subheader("Here's Your Guidance:")
            response = get_grammar_help(topic, user_question)
            st.write_stream(response)
            # Store session state for direct answer
            st.session_state.home_initial = True
            st.session_state.home_topic = topic
            st.session_state.home_question = user_question
            st.markdown("---")
            st.success("Remember: Great learning happens through exploration! Try applying these suggestions.")

    # Show direct answer button only after initial response
    if st.session_state.home_initial and st.session_state.page == '📚 Grammar Concept Helper':
        if st.button("Give Answer"):
            st.subheader("Direct Answer:")
            direct_response = get_direct_answer_home(
                st.session_state.home_topic, 
                st.session_state.home_question
            )
            st.write_stream(direct_response)

# Analysis Page
elif st.session_state.page == "✍️ Analyze My Writing":
    st.title("✍️ Analyze My Writing")
    st.markdown("""
<div class="custom-markdown">
Get personalized feedback on your writing: \n
1. Paste your text below
2. Get error analysis
3. Improve it yourself with guided questions
</div>
""", unsafe_allow_html=True)
    
    user_text = st.text_area("Your Text:", height=300, key="text_analysis")
    
    if st.button("Analyze My Writing", key="pulse"):
        if user_text.strip() == "":
            st.warning("Please enter some text to analyze!")
        else:
            st.subheader("Writing Feedback")
            st.markdown("**Key Areas to Improve** (work through these one at a time):")
            analysis = analyze_grammar(user_text)
            st.write_stream(analysis)
            # Store session state for direct answer
            st.session_state.analysis_initial = True
            st.session_state.analysis_text = user_text
            st.success("Try making corrections based on these insights, then analyze again!")

    # Show direct answer button only after initial response
    if st.session_state.analysis_initial and st.session_state.page == '✍️ Analyze My Writing':
        if st.button("Give Answer"):
            st.subheader("Direct Answer and Corrections:")
            direct_response = get_direct_answer_analysis(st.session_state.analysis_text)
            st.write_stream(direct_response)

# Image Generation Page
elif st.session_state.page == "🎨 Generate Image":
    st.title("🎨 Visual Story Helper")
    st.markdown("""
<div class="custom-markdown">
Turn your story ideas into images!  \n
    1. Describe a scene or character
    2. Get AI-generated artwork
    3. Use it for inspiration in your writing
</div>
""", unsafe_allow_html=True)

    image_prompt = st.text_area("Describe what you want to visualize:", 
                              height=150,
                              key="styledtextarea",
                              placeholder="Example: 'A brave knight fighting a dragon at sunset in a medieval castle courtyard'")
    
    if st.button("Generate Image", key="pulse"):
        if not image_prompt.strip():
            st.warning("Please enter a description first!")
        else:
            with st.spinner("Creating your artwork..."):
                image_url = generate_image(image_prompt)
                
                if image_url.startswith('http'):
                    response = requests.get(image_url)
                    image = Image.open(BytesIO(response.content))
                    st.image(image, caption="Your Generated Artwork")
                    st.success("Use this image to inspire your writing!")
                else:
                    st.error(image_url)

# Socratic Tutor Page
elif st.session_state.page == "🗣️ Socratic Tutor":
    st.title("Socratic Tutor 🤔")
    float_init()

    # Initialize session state
    if "socratic_messages" not in st.session_state:
        st.session_state.socratic_messages = [
            {"role": "system", "content": """You are a Socratic tutor. Never give direct answers. 
            Ask thought-provoking questions to guide users to discover answers independently."""},
            {"role": "assistant", "content": "What topic shall we explore today? I'll help you think through it with questions!"}
        ]

    # Footer container for microphone
    footer_container = st.container()
    with footer_container:
        audio_bytes = audio_recorder()

    # Display chat messages (skip system role)
    for message in st.session_state.socratic_messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Handle audio input
    if audio_bytes:
        with st.spinner("Transcribing..."):
            webm_file_path = "temp_audio.webm"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)
            
            try:
                transcript = speech_to_text(webm_file_path)
                if transcript:
                    st.session_state.socratic_messages.append({"role": "user", "content": transcript})
                    with st.chat_message("user"):
                        st.write(transcript)
                else:
                    st.error("Transcription failed. Please try again.")
            except ValueError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                if os.path.exists(webm_file_path):
                    os.remove(webm_file_path)

    # Generate response
    if st.session_state.socratic_messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking🤔..."):
                # Exclude system message from API call (already in context)
                final_response = get_answer([msg for msg in st.session_state.socratic_messages if msg["role"] != "system"])
            with st.spinner("Generating audio response..."):
                audio_file = text_to_speech(final_response)
                autoplay_audio(audio_file)
            st.write(final_response)
            st.session_state.socratic_messages.append({"role": "assistant", "content": final_response})
            if os.path.exists(audio_file):
                os.remove(audio_file)

    # Float footer
    footer_container.float("bottom: 0rem;")

# Footer
st.markdown("---")
st.caption("Powered by Brain | Made By Ayan Parmar")
