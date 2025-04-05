import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import yfinance as yf
import time
import random
import json

# Configure page
st.set_page_config(
    page_title="Cosmic Market Analyst Pro",
    page_icon="🌌🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BASE_URL = "https://www.astrostocks.com"  # Updated URL
DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]
TIMEZONES = pytz.all_timezones

# Initialize session state
if "ai_history" not in st.session_state:
    st.session_state.ai_history = []

def get_random_useragent():
    return random.choice(USER_AGENTS)

# DeepSeek AI Integration
def get_ai_insight(prompt, chart_data=None, market_data=None):
    headers = {
        "Authorization": f"Bearer {st.secrets['DEEPSEEK_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    system_msg = """You are a financial astrologer AI assistant. Analyze the given astrological chart data 
    and market conditions to provide strategic trading insights. Combine planetary positions, aspects, 
    and current market data to make predictions. Be specific about sectors, timing, and risk management."""
    
    user_content = f"User Query: {prompt}\n\nChart Data: {json.dumps(chart_data)}\nMarket Data: {market_data}"
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(DEEPSEEK_API, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return "Error: Failed to get AI response"
    except Exception as e:
        return f"API Error: {str(e)}"

# Enhanced AstroStocks Scraper
def get_financial_transits():
    try:
        headers = {'User-Agent': get_random_useragent()}
        response = requests.get(f"{BASE_URL}/daily-transits", headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            transits = []
            
            # Extract transit information
            transit_cards = soup.find_all('div', class_='transit-card')
            for card in transit_cards[:5]:  # Get top 5 transits
                title = card.find('h3').text.strip()
                description = card.find('div', class_='description').text.strip()
                impact = card.find('span', class_='impact').text.strip()
                
                transits.append({
                    "title": title,
                    "description": description,
                    "impact": impact
                })
            
            return transits
        return []
    except Exception as e:
        st.error(f"Transit Scraping Error: {str(e)}")
        return []

# Real-time Market Data with AI Analysis
@st.cache_data(ttl=60)
def get_ai_enhanced_market_data(sector):
    tickers = MARKET_SECTORS[sector]["tickers"]
    data = yf.download(tickers, period="1d", group_by='ticker')
    
    analysis = get_ai_insight(
        f"Analyze current {sector} market conditions and predict next 24 hours trends",
        market_data=data.to_dict()
    )
    
    return {
        "prices": data[-1:].to_dict(),
        "analysis": analysis
    }

# Modified Main App Structure
def main():
    st.title("🚀 AI Cosmic Market Analyst Pro")
    st.markdown("### AI-Powered Financial Astrology Platform")
    
    # Sidebar - AI Chat Interface
    with st.sidebar:
        st.header("AI Astro Advisor")
        
        user_input = st.text_input("Ask market prediction:", key="ai_input")
        if user_input:
            with st.spinner("Consulting the stars..."):
                chart_data = st.session_state.get("chart_data")
                market_data = get_market_data()
                response = get_ai_insight(user_input, chart_data, market_data)
                st.session_state.ai_history.append(
                    {"user": user_input, "ai": response}
                )
        
        for entry in reversed(st.session_state.ai_history[-5:]):
            st.markdown(f"**You**: {entry['user']}")
            st.markdown(f"**AI**: {entry['ai']}")
            st.divider()
    
    # Main Interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Planetary Transits")
        transits = get_financial_transits()
        if transits:
            for transit in transits:
                with st.expander(transit["title"]):
                    st.markdown(f"""
                    **Impact**: {transit["impact"]}  
                    **Description**: {transit["description"]}
                    """)
        else:
            st.warning("Could not retrieve transit data")
    
    with col2:
        st.header("AI Market Analysis")
        selected_sector = st.selectbox("Select Sector", list(MARKET_SECTORS.keys()))
        
        if st.button("Run Deep Analysis"):
            with st.spinner("Analyzing cosmic patterns..."):
                sector_data = get_ai_enhanced_market_data(selected_sector)
                
                st.subheader("Price Data")
                st.dataframe(pd.DataFrame(sector_data["prices"]))
                
                st.subheader("AI Prediction")
                st.markdown(sector_data["analysis"])
                
                # Generate visual
                fig = go.Figure()
                for ticker in MARKET_SECTORS[selected_sector]["tickers"]:
                    fig.add_trace(go.Scatter(
                        x=sector_data["prices"].index,
                        y=sector_data["prices"][ticker]["Close"],
                        name=ticker
                    ))
                st.plotly_chart(fig)

# Run the app
if __name__ == "__main__":
    main()
