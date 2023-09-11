import json
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
import os

# use export command to generate
openai.api_key = os.environ["OPEN_API_KEY"]

# Function to get the latest stock price for a given ticker


def get_latest_stock_price(ticker):
    """
    Retrieves the latest stock price for a given ticker.

    Args:
    ticker (str): The stock ticker symbol.

    Returns:
    str: The latest stock price as a string.
    """
    return str(yf.Ticker(ticker).history(period="1y").iloc[-1].Close)


# Function to calculate the Simple Moving Average (SMA) for a given ticker and window size


def calculate_SMA(ticker, window):
    """
    Calculates the Simple Moving Average (SMA) for a given stock ticker and window size.

    Args:
    ticker (str): The stock ticker symbol.
    window (int): The window size for the SMA calculation.

    Returns:
    str: The calculated SMA as a string.
    """
    data = yf.Ticker(ticker).history(period="1y").Close
    return str(data.rolling(window=window).mean().iloc[-1])


# Function to calculate the Exponential Moving Average (EMA) for a given ticker and window size


def calculate_EMA(ticker, window):
    """
    Calculates the Exponential Moving Average (EMA) for a given stock ticker and window size.

    Args:
    ticker (str): The stock ticker symbol.
    window (int): The window size for the EMA calculation.

    Returns:
    str: The calculated EMA as a string.
    """
    data = yf.Ticker(ticker).history(period="1y").Close
    return str(data.ewm(span=window).mean().iloc[-1])


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


def plot_stock_price(ticker):
    # Retrieve historical stock data using the yfinance library
    data = yf.Ticker(ticker).history(period="1y")

    # Create a new figure with a specified size for the plot
    plt.figure(figsize=(10, 5))

    # Plot the stock's closing prices over time using the date as the x-axis and the Close column as the y-axis
    plt.plot(data.index, data.Close)  # *args:data.index is not a valid syntax

    # Set a title for the plot
    plt.title(f"{ticker} Stock Price over the Last Year")

    plt.xlabel("Date")

    plt.ylabel("Stock Price ($) ")

    plt.grid(True)

    plt.savefig("stock.png")

    plt.close()


functions = [
    {
        "name": "get_stock_price",
        "description": "get the latest stock price given the ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                    "description": "stock ticker symbol for a company (for example MSFT is microsoft)."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_SMA",
        "description": "calculate the simple moving average for a given stock ticker and window",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                    "description": "stock ticker symbol for a company (for example MSFT is microsoft)."
                },
                "window": {
                    "type": "interger"
                    "description": "the timeframe to consider when calculating the SMA"
                }
            },
            "required": ["ticker", "window"]
        },
    },
    {
        "name": "calculate_EMA",
        "description": "calculate the exponential moving average for a given stock ticker and window",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                    "description": "stock ticker symbol for a company (for example MSFT is microsoft)."
                },
                "window": {
                    "type": "interger"
                    "description": "the timeframe to consider when calculating the EMA"
                }
            },
            "required": ["ticker", "window"]
        },
    },
    {
        "name": "calculate_RSI",
        "description": "calculate the RSI for a given stock ticker and a window",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                    "description": "stock ticker symbol for a company (for example MSFT is microsoft)."
                },
                "window": {
                    "type": "interger"
                    "description": "the timeframe to consider when calculating the EMA"
                }
            },
            "required": ["ticker"]
        },
    },
    {
        "name": "plot_stock_price",
        "description": "Plot the stock price for last year give the sticker of the company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                    "description": "stock ticker symbol for a company (for example MSFT is microsoft)."
                },
            },
            "required": ["ticker"]
        },
    },
]

available_funcs = {
    "get_stock_latest_price": get_latest_stock_price,
    "calculate_SMA": calculate_SMA,
    "calculate_EMA": calculate_EMA,
    "calculate_RSI": calculate_RSI,
    "calculate_MACD": calculate_MACD
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
            model="gpt-3.5=turbo-0613",
            messages=st.session_state["messages"],
            functions=functions,
            function_call="auto"
        )
        response_message = response["choices"][0]["message"]

        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(
                response_message["function_call"]["arguements"])
            if function_name in ["get_stock_price", "calculate_RSI", "calculate_MACD", "plot_stock_price"]:
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
                st.session_state["messages"].append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response
                    }
                )
    except:
        pass
