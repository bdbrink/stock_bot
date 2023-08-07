import json
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
import os

# use export command to generate
openai.api_key = os.environ['OPEN_API_KEY']
