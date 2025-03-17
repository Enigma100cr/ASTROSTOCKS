import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import yfinance as yf

# Function to display educational content
def display_educational_content():
    st.title("Comprehensive Stock Market Astrology & Trading Strategies")
    
    # Astrology & Business Cycles
    st.header("Astrology & Business Cycles")
    st.write("""
    Astrology can provide insights into market cycles based on planetary movements. Here are some key cycles:
    """)
    cycles_data = {
        "Cycle": ["Jupiter-Saturn Conjunction", "Rahu-Ketu Transit", "Sunspot Cycles"],
        "Ruling Planets": ["Jupiter, Saturn", "Rahu, Ketu", "Sun"],
        "Impact on Market": [
            "Major economic shifts",
            "Market volatility",
            "Economic fluctuations"
        ],
        "Bullish Phase": ["Expansion phase", "Speculative boom", "High solar activity boosts economy"],
        "Bearish Phase": ["Recession", "Market correction", "Low activity slows economy"]
    }
    st.table(pd.DataFrame(cycles_data))

    # Sector-Wise Astrological Analysis
    st.header("Sector-Wise Astrological Analysis")
    st.write("""
    Different sectors are influenced by different planets. Here's a breakdown:
    """)
    sectors_data = {
        "Sector": ["Banking & Finance", "Pharmaceuticals", "IT & Technology", "Oil & Gas", "Gold & Metals", "Real Estate"],
        "Ruling Planets": ["Jupiter, Mercury", "Mars, Ketu", "Mercury, Uranus", "Saturn, Moon", "Jupiter, Rahu", "Saturn, Moon"],
        "Bullish Periods": [
            "Jupiter Direct, Guru Hora",
            "Mars in Aries, Ketu in Scorpio",
            "Mercury Direct, Uranus in Aquarius",
            "Saturn in Capricorn, Full Moon",
            "Jupiter in Pisces, Rahu in Taurus",
            "Saturn in Aquarius, Full Moon"
        ],
        "Bearish Periods": [
            "Rahu Aspect, Mercury Retrograde",
            "Mars-Ketu Conjunction",
            "Mercury Retrograde",
            "Saturn Retrograde, Rahu in Pisces",
            "Saturn-Rahu Aspect",
            "Moon in Scorpio, Saturn Retrograde"
        ]
    }
    st.table(pd.DataFrame(sectors_data))

    # Gold Market Analysis
    st.header("Gold Market Analysis")
    st.write("""
    Gold prices are influenced by astrological factors. Here's how:
    """)
    gold_data = {
        "Astrological Factors": ["Jupiter Strength", "Rahu Influence", "Saturn Aspect"],
        "Market Impact": ["Gold Prices Rise", "Speculative gold surge", "Long-term strength"],
        "Bullish Triggers": ["Jupiter in Pisces, Sagittarius", "Rahu in Taurus", "Saturn in Aquarius"],
        "Bearish Triggers": ["Jupiter Combustion", "Rahu in Scorpio", "Saturn Retrograde"]
    }
    st.table(pd.DataFrame(gold_data))

    # Crude Oil Market Analysis
    st.header("Crude Oil Market Analysis")
    st.write("""
    Crude oil prices are influenced by planetary transits. Here's how:
    """)
    oil_data = {
        "Astrological Factors": ["Saturn Influence", "Moon Transits", "Ketu Aspect"],
        "Market Impact": ["Price Stability", "Short-term fluctuations", "Volatility"],
        "Bullish Triggers": ["Saturn in Capricorn", "Moon in Pisces", "Ketu in Sagittarius"],
        "Bearish Triggers": ["Saturn in Aries", "Moon in Gemini", "Ketu in Gemini"]
    }
    st.table(pd.DataFrame(oil_data))

    # Trading Strategies
    st.header("Trading Strategies")
    st.write("""
    Here are some advanced trading strategies based on astrology:
    """)
    strategies_data = {
        "Strategy": [
            "Intraday Scalping", "Swing Trading", "Breakout Trading", "Trend Following",
            "Reversal Trading", "Seasonal Trading", "Gann Astrology Cycles", "Fibonacci & Astrology"
        ],
        "Astrological Timing": [
            "Moon in strong Nakahara + Mercury Hora",
            "Jupiter in direct motion + Venus favorable",
            "Mars in strong sign + Rahu impact",
            "Saturn moving direct + bullish planetary cycle",
            "Sun combusting major planet",
            "Solar Eclipses & Lunar Phases",
            "Jupiter-Saturn aspecting 9th house",
            "Venus & Mercury transits"
        ],
        "Trading Insights": [
            "Best for short-term gains",
            "Profitable for mid-term holding",
            "High volatility trading strategy",
            "Follow long-term upward trends",
            "Identify reversal before major moves",
            "Market reacts strongly around eclipses",
            "Used for long-term stock analysis",
            "Align technical retracements with astrology"
        ]
    }
    st.table(pd.DataFrame(strategies_data))

    # Astrological Events
    st.header("Astrological Events Affecting Stock Markets")
    st.write("""
    Certain astrological events can significantly impact the stock market. Here's how:
    """)
    events_data = {
        "Astrological Event": [
            "Lunar Eclipse", "Solar Eclipse", "Mercury Retrograde", "Jupiter Combustion",
            "Saturn Return", "Mars-Ketu Conjunction"
        ],
        "Market Impact": [
            "Short-term volatility", "Market Uncertainty", "High volatility & confusion",
            "Weakens financial sector", "Long-term market changes", "Panic Selling"
        ],
        "Bullish Stocks": [
            "Gold, Silver, Commodities", "Energy, Oil, PSU Stocks", "FMCG, Commodities",
            "Energy, Pharma", "Infrastructure, Real Estate", "Defense, Metals"
        ],
        "Bearish Stocks": [
            "IT, FMCG", "Banking, Pharma", "Tech, Banking", "Banking, Finance",
            "High-risk stocks", "Banking, Real Estate"
        ]
    }
    st.table(pd.DataFrame(events_data))

    # Sector-Wise Investment Timings
    st.header("Sector-Wise Investment Timings")
    st.write("""
    Here are the best and worst times to invest in different sectors based on astrology:
    """)
    investment_data = {
        "Sector": [
            "Banking & Finance", "Pharmaceuticals", "Technology", "Real Estate",
            "Gold & Metals", "Oil & Gas", "FMCG"
        ],
        "Best Investment Period": [
            "Jupiter Direct in Pisces, Sagittarius",
            "Mars in Aries, Jupiter in Cancer",
            "Mercury in Gemini, Aquarius",
            "Saturn in Capricorn, Aquarius",
            "Jupiter in Taurus, Pisces",
            "Saturn in Capricorn, Full Moon",
            "Venus in Taurus, Libra"
        ],
        "Avoid During": [
            "Mercury Retrograde",
            "Mars-Ketu Conjunction",
            "Mercury Retrograde",
            "Saturn Retrograde",
            "Saturn-Rahu Aspect",
            "Saturn in Aries",
            "Venus Retrograde"
        ]
    }
    st.table(pd.DataFrame(investment_data))

# Function to get market data
def get_market_data(ticker, start_date, end_date):
    """
    Fetch market data using yfinance.
    """
    try:
        market_data = yf.download(ticker, start=start_date, end=end_date)
        return market_data
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return pd.DataFrame()

# Streamlit app
def main():
    st.sidebar.header("SEBI Disclaimer")
    st.sidebar.write("This app is for educational purposes only. Consult a financial advisor before making any investment decisions.")
    
    # Sidebar for user inputs
    st.sidebar.header("User Input")
    market_type = st.sidebar.selectbox("Select Market", ["Forex", "Indian", "Global"])
    ticker = st.sidebar.text_input("Enter Ticker Symbol", "AAPL")
    start_date = st.sidebar.text_input("Start Date", "2023-01-01")
    end_date = st.sidebar.text_input("End Date", "2023-12-31")
    
    # Display educational content
    display_educational_content()
    
    # Get market data
    st.header("Market Data")
    market_data = get_market_data(ticker, start_date, end_date)
    if not market_data.empty:
        st.write(market_data)
        
        # Plot market data
        st.header("Market Price Chart")
        fig = px.line(market_data, x=market_data.index, y='Close', title=f'{ticker} Closing Prices')
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
