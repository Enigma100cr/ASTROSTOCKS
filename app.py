import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import time

# Set page configuration
st.set_page_config(
    page_title="Real-Time Financial Astrology",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
REFRESH_INTERVAL = 300  # 5 minutes in seconds
ASTROSEEK_URL = "https://www.astro-seek.com/current-planets-astrology-transits"
MARKETWATCH_URL = "https://www.marketwatch.com/investing"

# Cache real-time data with expiration
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_realtime_data():
    return {
        "market_data": get_market_data(),
        "astrology_data": get_astrology_data()
    }

# Get real-time market data
def get_market_data():
    tickers = {
        "S&P 500": "^GSPC",
        "Gold": "GC=F",
        "Crude Oil": "CL=F",
        "Bitcoin": "BTC-USD",
        "USD/INR": "INR=X"
    }
    
    market_data = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for name, ticker in tickers.items():
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not data.empty:
                data = data.reset_index()
                market_data[name] = {
                    "current": round(data['Close'].iloc[-1], 2),
                    "change": round((data['Close'].iloc[-1]/data['Close'].iloc[-2]-1)*100, 2),
                    "chart_data": data[['Date', 'Close']]
                }
        except Exception as e:
            st.error(f"Error fetching {name} data: {e}")
    
    return market_data

# Get real-time astrology data from AstroSeek
def get_astrology_data():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(ASTROSEEK_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract current planetary positions
        planets = []
        planets_table = soup.find('table', {'class': 'table_planets'})
        if planets_table:
            for row in planets_table.find_all('tr')[1:11]:  # First 10 planets
                cols = row.find_all('td')
                if len(cols) >= 4:
                    planets.append({
                        "Planet": cols[0].text.strip(),
                        "Sign": cols[1].text.strip(),
                        "Degree": cols[2].text.strip(),
                        "Speed": cols[3].text.strip()
                    })
        
        # Extract current aspects
        aspects = []
        aspects_table = soup.find('table', {'class': 'table_aspects'})
        if aspects_table:
            for row in aspects_table.find_all('tr')[1:6]:  # First 5 aspects
                cols = row.find_all('td')
                if len(cols) >= 4:
                    aspects.append({
                        "Planets": cols[0].text.strip(),
                        "Aspect": cols[1].text.strip(),
                        "Orb": cols[2].text.strip(),
                        "Effect": cols[3].text.strip()[:50] + "..."  # Truncate long text
                    })
        
        return {
            "planets": planets,
            "aspects": aspects,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        st.error(f"Error fetching astrology data: {e}")
        return None

# Display market charts
def show_market_charts(market_data):
    st.subheader("Real-Time Market Performance")
    cols = st.columns(len(market_data))
    
    for idx, (name, data) in enumerate(market_data.items()):
        with cols[idx]:
            st.metric(
                label=name,
                value=f"${data['current']:,}",
                delta=f"{data['change']:.2f}%"
            )
    
    selected_market = st.selectbox("Select market to view chart:", list(market_data.keys()))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=market_data[selected_market]["chart_data"]['Date'],
        y=market_data[selected_market]["chart_data"]['Close'],
        mode='lines',
        name=selected_market
    ))
    fig.update_layout(
        title=f"{selected_market} 30-Day Performance",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# Display astrology data
def show_astrology_data(astrology_data):
    st.subheader("Current Planetary Positions")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(f"{ASTROSEEK_URL}-chart.gif?t={int(time.time())}",
               caption="Live Planetary Positions", use_column_width=True)
    
    with col2:
        st.dataframe(pd.DataFrame(astrology_data["planets"]), hide_index=True)
        
        st.markdown("""
        **Interpretation Guide:**
        - **Fast-moving planets** (Moon, Mercury, Venus, Mars): Short-term trends (hours/days)
        - **Slow-moving planets** (Jupiter, Saturn, Uranus, Neptune, Pluto): Long-term trends (weeks/months)
        - **Retrograde motion**: Reversal or review of market trends
        """)
    
    st.subheader("Active Planetary Aspects")
    st.dataframe(pd.DataFrame(astrology_data["aspects"]), hide_index=True)
    
    st.image(f"{ASTROSEEK_URL}-aspects.gif?t={int(time.time())}",
           caption="Current Planetary Aspects", use_column_width=True)

# Market-Astrology correlations
def show_correlations():
    st.subheader("Real-Time Market-Astrology Correlations")
    
    correlations = {
        "Market": ["S&P 500", "Gold", "Oil", "Bitcoin", "Currencies"],
        "Key Planet": ["Sun/Jupiter", "Moon/Venus", "Mars/Pluto", "Uranus", "Mercury"],
        "Current Influence": ["Expansion", "Stability", "Volatility", "Innovation", "Communication"],
        "Trading Strategy": ["Buy growth stocks", "Hold safe assets", "Trade carefully", "Speculate wisely", "Watch news"]
    }
    
    st.dataframe(pd.DataFrame(correlations), hide_index=True)
    
    st.markdown("""
    **How to Use This Data:**
    1. Check which planets are strong in current astrology
    2. See which markets they correlate with
    3. Combine with technical analysis for trading decisions
    4. Monitor aspect expiration dates for trend changes
    """)

# Main app
def main():
    st.title("📡 Real-Time Financial Astrology Dashboard")
    st.markdown("""
    Combining live market data with current astrological positions for financial timing.
    Data updates every 5 minutes.
    """)
    
    # Get all data
    data = get_realtime_data()
    market_data = data["market_data"]
    astrology_data = data["astrology_data"]
    
    if not market_data or not astrology_data:
        st.error("Failed to load real-time data. Please try again later.")
        return
    
    # Display last update time
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"Last updated: {last_update} (Refreshes every 5 minutes)")
    
    # Show main content
    show_market_charts(market_data)
    show_astrology_data(astrology_data)
    show_correlations()
    
    # Sidebar
    st.sidebar.title("Navigation")
    st.sidebar.markdown("""
    - [Market Data](#real-time-market-performance)
    - [Astrology Data](#current-planetary-positions)
    - [Correlations](#real-time-market-astrology-correlations)
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Highlights")
    
    # Find strongest aspect
    strongest_aspect = max(astrology_data["aspects"], key=lambda x: float(x["Orb"].split('°')[0]))
    st.sidebar.markdown(f"""
    **Strongest Aspect Today:**  
    {strongest_aspect["Planets"]} ({strongest_aspect["Aspect"]})  
    *{strongest_aspect["Effect"]}*
    """)
    
    # Find top gaining market
    top_market = max(market_data.items(), key=lambda x: x[1]["change"])
    st.sidebar.markdown(f"""
    **Top Performing Market:**  
    {top_market[0]}: {top_market[1]["change"]:.2f}%
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.warning("""
    **Educational Purpose Only**  
    Not financial advice. Astrological correlations are experimental.  
    Always conduct your own research.
    """)

if __name__ == "__main__":
    main()
