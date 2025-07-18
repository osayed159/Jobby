import sys
import os
import json

from agent.agent import Agent
from backend.cv_assistant import CVAssistant
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from agent.agent import Agent

st.set_page_config(page_title="Jobby - AI Job Hunting Assistant", page_icon="\U0001F4BC", layout="centered")

st.title("Jobby")
st.markdown("""
Welcome to **Jobby**! \U0001F680

Your AI-powered assistant for job hunting, CV creation, and motivational letters.

---
""")
            



