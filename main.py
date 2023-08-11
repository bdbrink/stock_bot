import json
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
import os

# use export command to generate
openai.api_key = os.environ['OPEN_API_KEY']

def stock_price_price(ticker):
    return str(yf.Ticker(ticker).history(period="1y").iloc[-1].Close)

# simple moving average
def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y").Close
    return str(data.rolling(window=window).mean().iloc[-1])

# exponential moving average
def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y").Close
    return str(data.ewm(span=window).mean().iloc[-1])

import yfinance as yf

def calculate_RSI(ticker):
    # Fetch historical closing prices for the given ticker over the last 1 year
    data = yf.Ticker(ticker).history(period="1y").Close
    
    # Calculate the price change (delta) between consecutive days
    delta = data.diff()
    
    # Separate positive price changes (gains) and negative price changes (losses)
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    # Calculate the 14-day Exponential Moving Average (EMA) of gains and losses
    ema_up = up.ewm(com=14 - 1, adjust=False).mean()
    ema_down = down.ewm(com=14 - 1, adjust=False).mean()
    
    # Calculate the Relative Strength (RS) by dividing EMA of gains by EMA of losses
    rs = ema_up / ema_down
    
    # Calculate the RSI using the formula: 100 - (100 / (1 + RS))
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    # Convert the RSI value to a string and return
    return str(rsi)

def calculate_MACD(ticker):
    # Fetch historical stock price data for the given ticker over the last year
    data = yf.Ticker(ticker).history(period="1y").Close
    
    # Calculate the 12-day Exponential Moving Average (EMA) of closing prices (short-term EMA)
    short_EMA = data.ewm(span=12, adjust=False).mean()
    
    # Calculate the 26-day Exponential Moving Average of closing prices (long-term EMA)
    long_EMA = data.ewm(span=26, adjust=False).mean()

    # Calculate the MACD line by subtracting the long-term EMA from the short-term EMA
    MACD = short_EMA - long_EMA
    
    # Calculate the signal line (9-day EMA of the MACD line)
    signal = MACD.ewm(span=9, adjust=False).mean()
    
    # Calculate the MACD histogram by subtracting the signal line from the MACD line
    MACD_histogram = MACD - signal
    
    # Return a formatted string containing the last values of MACD line, signal line, and MACD histogram
    return f"MACD: {MACD[-1]}, Signal Line: {signal[-1]}, MACD Histogram: {MACD_histogram[-1]}"