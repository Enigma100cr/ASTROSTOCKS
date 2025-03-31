import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Set page config
st.set_page_config(
    page_title="Financial Astrology Advisor",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load free LLM model (using HuggingFace pipeline)
@st.cache_resource
def load_llm():
    try:
        # Using a smaller free model that can run locally
        return pipeline('text-generation', model='gpt2')
    except Exception as e:
        st.error(f"Could not load LLM: {e}")
        return None

# Initialize LLM
llm = load_llm()

# Function to generate AI response using free model
def ask_ai(question):
    if not llm:
        return "AI service is currently unavailable. Please try again later."
    
    prompt = f"""
    You are a financial astrologer expert. Provide detailed explanations combining astrology and market analysis.
    Answer the following question with practical trading insights:
    
    Question: {question}
    
    Answer: According to financial astrology principles,"""
    
    try:
        response = llm(
            prompt,
            max_length=300,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True
        )
        return response[0]['generated_text'].split("Answer: ")[-1]
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Enhanced web scraping functions
def scrape_astrological_events():
    """Scrape planetary positions and aspects"""
    try:
        url = "https://www.lunarplanner.com/planets/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = []
        planets_table = soup.find('table', {'class': 'planet-positions'})
        if planets_table:
            rows = planets_table.find_all('tr')[1:8]  # Get main planets
            for row in rows:
                cols = row.find_all('td')
                events.append({
                    "Planet": cols[0].text.strip(),
                    "Sign": cols[1].text.strip(),
                    "Degree": cols[2].text.strip(),
                    "Aspects": cols[3].text.strip() if len(cols) > 3 else ""
                })
        return pd.DataFrame(events)
    except Exception as e:
        st.error(f"Scraping error: {e}")
        return pd.DataFrame({
            "Planet": ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"],
            "Sign": ["Leo", "Cancer", "Virgo", "Leo", "Virgo", "Taurus", "Pisces"],
            "Degree": ["15°", "23°", "5°", "19°", "12°", "14°", "28°"],
            "Aspects": ["Trine Jupiter", "Square Mars", "Opposite Neptune", "Conjunct Sun", "Trine Pluto", "Square Saturn", "Sextile Uranus"]
        })

def scrape_market_sentiment():
    """Scrape market sentiment data"""
    try:
        url = "https://www.marketwatch.com/investing"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        markets = []
        for item in soup.select('.market__item')[:5]:
            markets.append({
                "Market": item.select_one('.market__label').text.strip(),
                "Price": item.select_one('.market__price').text.strip(),
                "Change": item.select_one('.market__change').text.strip()
            })
        return pd.DataFrame(markets)
    except Exception as e:
        st.error(f"Scraping error: {e}")
        return pd.DataFrame({
            "Market": ["S&P 500", "Gold", "Crude Oil", "Bitcoin", "USD/INR"],
            "Price": ["4,450", "$1,950", "$81.50", "$29,380", "82.45"],
            "Change": ["+0.5%", "-0.2%", "+1.8%", "+3.2%", "-0.4%"]
        })

# Educational Content
def display_educational_content():
    st.title("🔮 Financial Astrology Masterclass")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        with st.expander("🌌 Current Planetary Alignments", expanded=True):
            st.write("**Planetary Positions Today**")
            planets_df = scrape_astrological_events()
            st.dataframe(planets_df, hide_index=True)
            
            st.markdown("""
            **Key Aspects Today:**
            - Sun trine Jupiter: Bullish energy for growth stocks
            - Mars square Moon: Increased market volatility
            - Mercury opposite Neptune: Confusing market signals
            """)
        
        with st.expander("📈 Market Correlations"):
            st.markdown("""
            | Planet       | Market Sector          | Bullish Signs               | Bearish Signs               |
            |--------------|------------------------|-----------------------------|-----------------------------|
            | **Jupiter**  | Banking, Finance       | In Sagittarius/Pisces       | In retrograde               |
            | **Saturn**   | Real Estate, Mining    | In Capricorn/Aquarius       | Square Uranus               |
            | **Mercury**  | Tech, Communications   | Direct motion in Gemini      | Retrograde periods          |
            | **Venus**    | Luxury, Relationships  | In Taurus/Libra             | Combust or retrograde       |
            | **Mars**     | Energy, Defense        | In Aries/Scorpio            | Square Saturn               |
            """)
            
            st.write("**Current Market Sentiment**")
            market_df = scrape_market_sentiment()
            st.dataframe(market_df, hide_index=True)
    
    with col2:
        with st.expander("✨ Upcoming Astrological Events"):
            events = {
                "Date": ["2023-08-27", "2023-09-02", "2023-09-10", "2023-09-25", "2023-10-08"],
                "Event": ["Mercury enters Libra", "Venus square Pluto", "Full Moon in Pisces", "Saturn goes direct", "Solar Eclipse"],
                "Impact": ["Communication sectors volatile", "Relationship markets stressed", "Emotional trading peaks", "Structural market shifts", "Major market turning point"]
            }
            st.table(events)
            
            st.markdown("""
            **Trading Strategy:**
            - 3 days before/after major aspects: Reduce position sizes
            - During Mercury retrograde: Avoid new tech IPOs
            - Venus in Taurus: Good for luxury sector investments
            """)
        
        with st.expander("🧠 Advanced Techniques"):
            st.markdown("""
            **Gann Astro-Cycles:**
            1. Identify planetary cycles matching asset patterns
            2. Combine with Fibonacci retracements
            3. Trade when both align
            
            **Lunar Phases Trading:**
            - New Moon: Start new positions
            - Full Moon: Take profits
            - Waning Moon: Short selling favored
            
            **Planetary Hours Trading:**
            - Trade sectors during their planetary hours
            - Example: Tech during Mercury hour
            """)

# Chat Interface
def chat_interface():
    st.header("💬 Consult the Financial Astrologer")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "I'm your Financial Astrology advisor. Ask me about planetary impacts on markets, sector timing, or trading strategies."}
        ]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    if prompt := st.chat_input("Ask about astrology and trading..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Consulting the stars..."):
                response = ask_ai(prompt)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# Main App
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=AstroTrader", width=150)
        st.title("Navigation")
        app_mode = st.radio("Choose Mode", ["📚 Learn Financial Astrology", "🔮 AI Astrologer Chat"])
        
        st.markdown("---")
        st.header("Planetary Trading Guide")
        st.markdown("""
        - 🌞 Sun: General market direction
        - 🌙 Moon: Short-term sentiment
        - ☿ Mercury: Trading volume/communication
        - ♀ Venus: Luxury/relationship sectors
        - ♂ Mars: Energy/volatility
        - ♃ Jupiter: Expansion/growth
        - ♄ Saturn: Contraction/structure
        """)
        
        st.markdown("---")
        st.warning("""
        **Disclaimer:**  
        This is for educational purposes only.  
        Astrological market analysis is experimental.  
        Past performance doesn't guarantee future results.
        """)
    
    # Main content
    if app_mode == "📚 Learn Financial Astrology":
        display_educational_content()
    else:
        chat_interface()

if __name__ == "__main__":
    main()
