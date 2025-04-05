import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import yfinance as yf
import random
import json

# Configure page
st.set_page_config(
    page_title="AstroStocks AI Pro",
    page_icon="🌌📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BASE_URL = "https://www.astrostocks.com"
DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]
TIMEZONES = pytz.all_timezones

MARKET_SECTORS = {
    "Forex": {
        "tickers": ["EURUSD=X", "USDINR=X", "GBPUSD=X", "USDJPY=X"],
        "rulers": ["Mercury", "Venus"],
        "houses": ["2nd", "8th"]
    },
    "Indian Market": {
        "tickers": ["^NSEI", "^BSESN", "RELIANCE.NS", "TATASTEEL.NS"],
        "rulers": ["Moon", "Mars"],
        "houses": ["4th", "10th"]
    },
    "Crypto": {
        "tickers": ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD"],
        "rulers": ["Uranus", "Pluto"],
        "houses": ["11th", "8th"]
    },
    "Global Markets": {
        "tickers": ["^GSPC", "^DJI", "^IXIC", "^FTSE"],
        "rulers": ["Sun", "Jupiter", "Saturn"],
        "houses": ["10th", "9th", "12th"]
    }
}

# Initialize session state
if 'ai_history' not in st.session_state:
    st.session_state['ai_history'] = []

def get_random_useragent():
    return random.choice(USER_AGENTS)

@st.cache_data(ttl=300)
def get_market_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1d", progress=False)
            if not df.empty:
                data[ticker] = {
                    "price": round(df['Close'].iloc[-1], 2),
                    "change": round((df['Close'].iloc[-1]/df['Open'].iloc[-1]-1)*100, 2),
                    "volume": int(df['Volume'].iloc[-1])
                }
        except Exception as e:
            st.error(f"Error fetching {ticker}: {str(e)}")
    return data

def get_financial_transits():
    try:
        headers = {'User-Agent': get_random_useragent()}
        response = requests.get(f"{BASE_URL}/daily-transits", headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            transits = []
            
            # Example parsing - adjust based on actual website structure
            transit_items = soup.find_all('div', class_='transit-item')
            for item in transit_items[:5]:
                title = item.find('h3').text.strip()
                description = item.find('div', class_='description').text.strip()
                impact = item.find('span', class_='impact').text.strip()
                transits.append({
                    "title": title,
                    "description": description,
                    "impact": impact
                })
            return transits
        return []
    except Exception as e:
        st.error(f"Transit Error: {str(e)}")
        return []

def get_ai_insight(prompt, context=None):
    headers = {
        "Authorization": f"Bearer {st.secrets['DEEPSEEK_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    system_msg = """You are a financial astrologer AI. Provide insights combining:
    - Current market conditions
    - Planetary transits
    - Technical indicators
    - Sector-specific astrological influences
    Provide actionable advice with risk management tips."""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(DEEPSEEK_API, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

def main():
    st.title("🌌📈 AstroStocks AI Pro")
    st.markdown("### AI-Powered Financial Astrology Platform")
    
    # Sidebar - AI Chat
    with st.sidebar:
        st.header("AI Astro Advisor")
        user_input = st.text_input("Ask market prediction:")
        
        if user_input:
            with st.spinner("Analyzing celestial patterns..."):
                response = get_ai_insight(user_input)
                st.session_state.ai_history.append({
                    "user": user_input,
                    "ai": response
                })
        
        st.subheader("Chat History")
        for entry in reversed(st.session_state.ai_history[-3:]):
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
        st.header("Market Analysis")
        selected_sector = st.selectbox("Select Sector", list(MARKET_SECTORS.keys()))
        
        if st.button("Run Sector Analysis"):
            with st.spinner("Gathering cosmic insights..."):
                sector_data = MARKET_SECTORS[selected_sector]
                market_data = get_market_data(sector_data["tickers"])
                
                # Display prices
                st.subheader("Current Prices")
                cols = st.columns(len(market_data))
                for idx, (ticker, data) in enumerate(market_data.items()):
                    with cols[idx]:
                        st.metric(
                            label=ticker,
                            value=f"${data['price']}",
                            delta=f"{data['change']}%",
                            help=f"Volume: {data['volume']}"
                        )
                
                # AI Analysis
                st.subheader("AI Prediction")
                prompt = f"Analyze {selected_sector} sector with rulers {sector_data['rulers']} in houses {sector_data['houses']}"
                analysis = get_ai_insight(prompt)
                st.markdown(analysis)
                
                # Price Chart
                st.subheader("Price Movement")
                fig = go.Figure()
                for ticker in sector_data["tickers"]:
                    df = yf.download(ticker, period="5d", progress=False)
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['Close'],
                        name=ticker
                    ))
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
