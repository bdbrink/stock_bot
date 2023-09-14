import json
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
import os

# Use export command to generate
openai.api_key = os.environ["OPEN_API_KEY"]

# Function to get the latest stock price for a given ticker


def get_latest_stock_price(ticker):
    return str(yf.Ticker(ticker).history(period="1y").iloc[-1].Close)

# Function to calculate the Simple Moving Average (SMA) for a given ticker and window size


def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y").Close
    return str(data.rolling(window=window).mean().iloc[-1])

# Function to calculate the Exponential Moving Average (EMA) for a given ticker and window size


def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y").Close
    return str(data.ewm(span=window).mean().iloc[-1])


def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period="1y").Close
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=14 - 1, adjust=False).mean()
    ema_down = down.ewm(com=14 - 1, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    return str(rsi)


def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period="1y").Close
    short_EMA = data.ewm(span=12, adjust=False).mean()
    long_EMA = data.ewm(span=26, adjust=False).mean()
    MACD = short_EMA - long_EMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    MACD_histogram = MACD - signal
    return f"MACD: {MACD[-1]}, Signal Line: {signal[-1]}, MACD Histogram: {MACD_histogram[-1]}"


def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period="1y")
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.Close)
    plt.title(f"{ticker} Stock Price over the Last Year")
    plt.xlabel("Date")
    plt.ylabel("Stock Price ($)")
    plt.grid(True)
    plt.savefig("stock.png")
    plt.close()


# Define function descriptions and parameters for OpenAI chatbot
functions = [
    {
        "name": "get_latest_stock_price",
        "description": "Get the latest stock price given the ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol for a company (e.g., MSFT for Microsoft)."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_SMA",
        "description": "Calculate the Simple Moving Average (SMA) for a given stock ticker and window.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol for a company (e.g., MSFT for Microsoft)."
                },
                "window": {
                    "type": "integer",
                    "description": "The timeframe to consider when calculating the SMA."
                }
            },
            "required": ["ticker", "window"]
        }
    },
    {
        "name": "calculate_EMA",
        "description": "Calculate the Exponential Moving Average (EMA) for a given stock ticker and window.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol for a company (e.g., MSFT for Microsoft)."
                },
                "window": {
                    "type": "integer",
                    "description": "The timeframe to consider when calculating the EMA."
                }
            },
            "required": ["ticker", "window"]
        }
    },
    {
        "name": "calculate_RSI",
        "description": "Calculate the Relative Strength Index (RSI) for a given stock ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol for a company (e.g., MSFT for Microsoft)."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_MACD",
        "description": "Calculate the Moving Average Convergence Divergence (MACD) for a given stock ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol for a company (e.g., MSFT for Microsoft)."
                }
            },
            "required": ["ticker"]
        }
    },
]

# Create a dictionary to map function names to their corresponding functions
available_funcs = {
    "get_latest_stock_price": get_latest_stock_price,
    "calculate_SMA": calculate_SMA,
    "calculate_EMA": calculate_EMA,
    "calculate_RSI": calculate_RSI,
    "calculate_MACD": calculate_MACD,
}

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("Stock Analysis Chatbot")
user_input = st.text_input("Your Input:")

if user_input:
    try:
        st.session_state["messages"].append(
            {"role": "user", "content": f"{user_input}"})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=st.session_state["messages"],
            functions=functions,
            function_call="auto"
        )
        response_message = response["choices"][0]["message"]
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(
                response_message["function_call"]["arguments"])
            if function_name in ["get_latest_stock_price", "calculate_RSI", "calculate_MACD", "plot_stock_price"]:
                args_dict = {"ticker": function_args.get("ticker")}
            elif function_name in ["calculate_SMA", "calculate_EMA"]:
                args_dict = {"ticker": function_args.get(
                    "ticker"), "window": function_args.get("window")}
            function_to_call = available_funcs[function_name]
            function_response = function_to_call(**args_dict)
            if function_name == "plot_stock_price":
                st.image("stock.png")
            else:
                st.session_state["messages"].append(response_message)
                st.session_state["messages"].append({
                    "role": "function",
                    "name": function_name,
                    "content": function_response
                })
                second_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0613",
                    messages=st.session_state["messages"]
                )
        else:
            st.text(response_message["content"])
            st.session_state["messages"].append(
                {"role": "assistant", "content": response_message["content"]})
    except:
        st.text("Try again")
