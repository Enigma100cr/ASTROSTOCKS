import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import yfinance as yf
import pdfplumber

# Function to scrape astrological data
def scrape_astrological_data():
    url = "https://www.astro-seek.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Example: Extract planetary positions
    planets = soup.find_all('div', class_='planet')
    data = []
    for planet in planets:
        name = planet.find('span', class_='planet-name').text
        position = planet.find('span', class_='planet-position').text
        data.append({'Planet': name, 'Position': position})
    return pd.DataFrame(data)

# Function to get market data
def get_market_data(ticker, start_date, end_date):
    market_data = yf.download(ticker, start=start_date, end=end_date)
    return market_data

# Function to extract strategies from PDF
def extract_strategies_from_pdf(pdf_path):
    strategies = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                strategies.append(text)
    return strategies

# Streamlit app
def main():
    st.title("Astro-Trading App for Forex, Indian, and Global Markets")
    
    # SEBI Disclaimer
    st.sidebar.header("SEBI Disclaimer")
    st.sidebar.write("This app is for educational purposes only. Consult a financial advisor before making any investment decisions.")
    
    # Sidebar for user inputs
    st.sidebar.header("User Input")
    market_type = st.sidebar.selectbox("Select Market", ["Forex", "Indian", "Global"])
    ticker = st.sidebar.text_input("Enter Ticker Symbol", "AAPL")
    start_date = st.sidebar.text_input("Start Date", "2023-01-01")
    end_date = st.sidebar.text_input("End Date", "2023-12-31")
    
    # Scrape astrological data
    st.header("Astrological Data")
    astro_data = scrape_astrological_data()
    st.write(astro_data)
    
    # Get market data
    st.header("Market Data")
    market_data = get_market_data(ticker, start_date, end_date)
    st.write(market_data)
    
    # Plot market data
    st.header("Market Price Chart")
    fig = px.line(market_data, x=market_data.index, y='Close', title=f'{ticker} Closing Prices')
    st.plotly_chart(fig)
    
    # Astrological Visualization
    st.header("Astrological Visualization")
    fig, ax = plt.subplots()
    ax.bar(astro_data['Planet'], astro_data['Position'].str.extract('(\d+)')[0].astype(int))
    ax.set_xlabel('Planet')
    ax.set_ylabel('Position')
    ax.set_title('Planetary Positions')
    st.pyplot(fig)
    
    # Extract and display strategies from PDF
    st.header("Trading Strategies from PDF")
    pdf_path = "Comprehensive_Stock_Market_Astrology_Analysis (2).pdf"
    strategies = extract_strategies_from_pdf(pdf_path)
    for strategy in strategies:
        st.write(strategy)

if __name__ == "__main__":
    main()
