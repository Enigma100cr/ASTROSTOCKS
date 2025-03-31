import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai

# Configure OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to scrape astrological data from AstroSeek
def scrape_astroseek():
    try:
        url = "https://www.astro-seek.com/astrological-events-calendar"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract relevant data (adjust selectors based on actual page structure)
        events = []
        event_elements = soup.select('.event-item')[:10]  # Example selector
        for event in event_elements:
            date = event.select_one('.event-date').text.strip()
            description = event.select_one('.event-desc').text.strip()
            impact = event.select_one('.event-impact').text.strip()
            events.append({
                "Date": date,
                "Event": description,
                "Market Impact": impact
            })
        
        return pd.DataFrame(events)
    
    except Exception as e:
        st.error(f"Error scraping AstroSeek: {e}")
        return pd.DataFrame()

# Function to scrape market data from TradingView
def scrape_tradingview():
    try:
        url = "https://www.tradingview.com/markets/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract relevant market data (adjust selectors)
        markets = []
        market_elements = soup.select('.market-card')[:5]  # Example selector
        for market in market_elements:
            name = market.select_one('.market-name').text.strip()
            price = market.select_one('.market-price').text.strip()
            change = market.select_one('.market-change').text.strip()
            markets.append({
                "Market": name,
                "Price": price,
                "Change": change
            })
        
        return pd.DataFrame(markets)
    
    except Exception as e:
        st.error(f"Error scraping TradingView: {e}")
        return pd.DataFrame()

# Function to generate AI response
def ask_ai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial astrologer expert. Provide detailed explanations combining astrology and market analysis."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Main educational content
def display_educational_content():
    st.title("🧙‍♂️ Financial Astrology & Market Insights")
    
    with st.expander("📚 Astrological Market Cycles", expanded=True):
        st.write("""
        Planetary movements create measurable cycles in financial markets. Here are the key astrological cycles:
        """)
        cycles_data = {
            "Cycle": ["Jupiter-Saturn Conjunction (20 yrs)", "Saturn-Pluto Cycle (33-38 yrs)", 
                     "Jupiter-Uranus Cycle (14 yrs)", "Venus Retrograde (18 months)", 
                     "Mars Retrograde (26 months)", "Mercury Retrograde (3-4x/year)"],
            "Current Phase": ["Expansion (2020-2040)", "Transformation (2020-2053)", 
                             "Innovation (2024-2038)", "Re-evaluation (Oct 2023-Mar 2024)", 
                             "Correction (Dec 2022-Feb 2023)", "Communication (Next: Aug 2024)"],
            "Market Impact": ["Major economic paradigm shifts", "Structural reforms & crises", 
                            "Technological breakthroughs", "Currency & relationship markets", 
                            "Energy & conflict sectors", "Communication & transport sectors"]
        }
        st.table(pd.DataFrame(cycles_data))
        
        st.write("""
        **Key Insights:**
        - Jupiter-Saturn conjunctions mark shifts between tangible (Earth signs) and intangible (Air signs) assets
        - Saturn-Pluto cycles correlate with major financial crises (2008, 1987, 1929)
        - Mercury retrogrades increase market volatility and trading errors
        """)
    
    with st.expander("🪐 Current Planetary Alignments"):
        st.write("**Today's Planetary Positions:**")
        today = datetime.now().strftime("%Y-%m-%d")
        planets = {
            "Planet": ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"],
            "Sign": ["Leo", "Cancer", "Virgo", "Leo", "Virgo", "Taurus", "Pisces", "Taurus", "Pisces", "Aquarius"],
            "Aspect": ["Trine Jupiter", "Square Mars", "Opposite Neptune", "Conjunct Sun", "Trine Pluto", "Square Saturn", "Sextile Uranus", "Trine Mercury", "Square Moon", "Conjunct Venus"],
            "Market Effect": ["Bullish energy", "Emotional trading", "Communication issues", "Relationship markets up", "Energy volatility", "Financial expansion", "Structural pressure", "Tech innovation", "Illiquid assets", "Transformation"]
        }
        st.table(pd.DataFrame(planets))
        
        st.write(f"**Upcoming Astrological Events (Next 30 Days) - Scraped from AstroSeek**")
        astro_events = scrape_astroseek()
        if not astro_events.empty:
            st.table(astro_events)
        else:
            st.warning("Couldn't fetch live astrological events. Showing sample data.")
            sample_events = {
                "Date": ["2023-08-27", "2023-09-02", "2023-09-10"],
                "Event": ["Mercury enters Libra", "Venus square Pluto", "Full Moon in Pisces"],
                "Market Impact": ["Communication sectors volatile", "Relationship markets stressed", "Emotional trading peaks"]
            }
            st.table(pd.DataFrame(sample_events))
    
    with st.expander("💎 Sector Analysis by Planetary Rulership"):
        sectors = {
            "Sector": ["Technology", "Finance", "Energy", "Healthcare", "Real Estate", "Consumer", "Materials", "Utilities"],
            "Ruling Planet": ["Uranus/Mercury", "Jupiter/Venus", "Mars/Pluto", "Chiron/Neptune", "Saturn", "Venus", "Saturn/Pluto", "Neptune"],
            "Current Transit": ["Uranus in Taurus", "Jupiter in Taurus", "Mars in Virgo", "Neptune retrograde", "Saturn in Pisces", "Venus in Leo", "Pluto in Aquarius", "Neptune in Pisces"],
            "Outlook": ["Strong (5G/AI boom)", "Cautious (rate hikes)", "Volatile (geopolitics)", "Mixed (biotech strong)", "Weak (high rates)", "Stable (luxury up)", "Bearish (commodities down)", "Neutral"]
        }
        st.table(pd.DataFrame(sectors))
        
        st.write("""
        **Trading Strategies by Sector:**
        1. **Tech (Uranus):** Buy on Mercury direct days, sell during retrogrades
        2. **Finance (Jupiter):** Trade options during Jupiter aspects (trines/sextiles)
        3. **Energy (Mars):** Swing trade during Mars sign changes
        4. **Healthcare (Neptune):** Position trade around major aspects
        """)
    
    with st.expander("📈 Live Market Data from TradingView"):
        st.write("**Current Market Overview**")
        market_data = scrape_tradingview()
        if not market_data.empty:
            st.table(market_data)
        else:
            st.warning("Couldn't fetch live market data. Showing sample data.")
            sample_markets = {
                "Market": ["S&P 500", "Gold", "Crude Oil", "Bitcoin", "USD/INR"],
                "Price": ["4,450", "$1,950", "$81.50", "$29,380", "82.45"],
                "Change": ["+0.5%", "-0.2%", "+1.8%", "+3.2%", "-0.4%"]
            }
            st.table(pd.DataFrame(sample_markets))
        
        st.write("""
        **Astrological Correlations:**
        - Gold prices strongest when Moon is in Taurus
        - Oil prices volatile during Mars-Uranus aspects
        - Bitcoin follows Uranus cycles (tech planet)
        - Currencies affected by Venus transits
        """)

# AI Chat Functionality
def chat_interface():
    st.header("🔮 Ask the Financial Astrologer AI")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about astrology and market trends..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = ask_ai(prompt)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# Main app
def main():
    st.sidebar.image("https://via.placeholder.com/150x50?text=Financial+Astrology", width=150)
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Educational Content", "AI Astrologer"])
    
    st.sidebar.markdown("---")
    st.sidebar.header("Disclaimer")
    st.sidebar.warning("""
    This is for educational purposes only. Not financial advice. 
    Astrological market analysis is experimental. Always do your own research.
    """)
    
    if page == "Educational Content":
        display_educational_content()
    else:
        chat_interface()

if __name__ == "__main__":
    main()
