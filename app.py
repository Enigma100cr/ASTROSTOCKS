import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import yfinance as yf
import time
from fake_useragent import UserAgent

# Configure page
st.set_page_config(
    page_title="Cosmic Market Analyst",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BASE_URL = "https://www.astro-seek.com"
USER_AGENT = UserAgent().chrome
HEADERS = {'User-Agent': USER_AGENT}
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

# Cache market data
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

# Scrape natal chart from AstroSeek
def get_natal_chart(birth_datetime, city, country):
    try:
        # Convert to AstroSeek format
        params = {
            'narozeni_den': birth_datetime.day,
            'narozeni_mesic': birth_datetime.month,
            'narozeni_rok': birth_datetime.year,
            'narozeni_hodina': birth_datetime.hour,
            'narozeni_minuta': birth_datetime.minute,
            'narozeni_mesto': city,
            'narozeni_zeme': country,
            'submit': 'Calculate'
        }
        
        with requests.Session() as session:
            # Get initial cookies
            session.get(f"{BASE_URL}/birth-chart", headers=HEADERS)
            
            # Submit form
            response = session.post(
                f"{BASE_URL}/birth-chart",
                data=params,
                headers=HEADERS
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract planetary positions
                planets = []
                planet_table = soup.find('table', {'id': 'tab_planety'})
                if planet_table:
                    for row in planet_table.find_all('tr')[1:12]:  # Skip header and include up to Pluto
                        cols = row.find_all('td')
                        if len(cols) >= 7:
                            planets.append({
                                "Planet": cols[0].text.strip(),
                                "Sign": cols[1].text.strip(),
                                "Degree": cols[2].text.strip(),
                                "House": cols[6].text.strip(),
                                "Speed": cols[3].text.strip()
                            })
                
                # Extract aspects
                aspects = []
                aspect_table = soup.find('table', {'id': 'tab_aspekty'})
                if aspect_table:
                    for row in aspect_table.find_all('tr')[1:6]:  # Top 5 aspects
                        cols = row.find_all('td')
                        if len(cols) >= 4:
                            aspects.append({
                                "Planets": cols[0].text.strip(),
                                "Aspect": cols[1].text.strip(),
                                "Orb": cols[2].text.strip(),
                                "Effect": cols[3].text.strip()[:100] + "..."
                            })
                
                return {
                    "planets": planets,
                    "aspects": aspects,
                    "valid": True,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "chart_url": response.url
                }
            else:
                return {"valid": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# Calculate planetary strengths
def calculate_planetary_strengths(planets):
    strengths = {}
    for planet in planets:
        name = planet["Planet"]
        strength = 1
        
        # House weighting
        if planet["House"] in ["1st", "4th", "7th", "10th"]:  # Angular
            strength *= 2
        elif planet["House"] in ["2nd", "5th", "8th", "11th"]:  # Succedent
            strength *= 1.5
        
        # Sign dignity
        if name == "Sun" and planet["Sign"] == "Leo":
            strength *= 2
        elif name == "Moon" and planet["Sign"] == "Cancer":
            strength *= 2
        # Add other essential dignities...
        
        strengths[name] = round(strength, 2)
    
    return strengths

# Analyze favorable sectors
def analyze_sectors(planets, aspects):
    sector_scores = {sector: 0 for sector in MARKET_SECTORS}
    
    # Calculate based on planetary rulers
    planetary_strengths = calculate_planetary_strengths(planets)
    
    for sector, data in MARKET_SECTORS.items():
        for ruler in data["rulers"]:
            if ruler in planetary_strengths:
                sector_scores[sector] += planetary_strengths[ruler]
        
        # Check if any planets are in relevant houses
        for planet in planets:
            if planet["House"] in data["houses"]:
                sector_scores[sector] += planetary_strengths.get(planet["Planet"], 1)
    
    # Normalize scores
    max_score = max(sector_scores.values()) if any(sector_scores.values()) else 1
    return {k: round(v/max_score, 2) for k, v in sector_scores.items()}

# Find favorable times
def find_favorable_times(aspects):
    favorable_periods = []
    
    # Major aspects
    for aspect in aspects:
        planets = aspect["Planets"]
        orb = float(aspect["Orb"].replace("°", ""))
        
        if orb < 3:  # Tight orb
            period = {
                "Aspect": f"{planets} {aspect['Aspect']}",
                "Orb": aspect["Orb"],
                "Effect": aspect["Effect"],
                "Duration": "1-3 days",
                "Priority": "High" if "Sun" in planets or "Moon" in planets else "Medium"
            }
            favorable_periods.append(period)
    
    return favorable_periods

# Visualization
def create_sector_radar(sector_scores):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(sector_scores.values()),
        theta=list(sector_scores.keys()),
        fill='toself',
        name='Sector Strength'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Market Sector Strength Analysis",
        height=500
    )
    return fig

# Main app
def main():
    st.title("🌌 Cosmic Market Analyst")
    st.markdown("### Financial Astrology for Strategic Trading")
    
    # Sidebar inputs
    with st.sidebar:
        st.header("Natal Chart Data")
        
        col1, col2 = st.columns(2)
        with col1:
            birth_date = st.date_input("Birth Date", value=datetime(2000, 1, 1))
        with col2:
            birth_time = st.time_input("Birth Time", value=datetime(2000, 1, 1, 12, 0))
        
        birth_datetime = datetime.combine(birth_date, birth_time)
        
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City", "Mumbai")
        with col2:
            country = st.text_input("Country", "India")
        
        timezone = st.selectbox("Timezone", TIMEZONES, index=TIMEZONES.index("Asia/Kolkata"))
        
        if st.button("Analyze Natal Chart"):
            with st.spinner("Calculating planetary positions..."):
                result = get_natal_chart(birth_datetime, city, country)
                if result["valid"]:
                    st.session_state["chart_data"] = result
                    st.success("Chart calculated successfully!")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    # Main display
    if "chart_data" in st.session_state:
        chart_data = st.session_state["chart_data"]
        
        # Display chart info
        st.header("Natal Chart Analysis")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Planetary Positions")
            st.dataframe(
                pd.DataFrame(chart_data["planets"]),
                hide_index=True,
                use_container_width=True
            )
        
        with col2:
            st.subheader("Major Aspects")
            st.dataframe(
                pd.DataFrame(chart_data["aspects"]),
                hide_index=True,
                use_container_width=True
            )
        
        # Market Analysis
        st.header("Market Sector Analysis")
        sector_scores = analyze_sectors(chart_data["planets"], chart_data["aspects"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                create_sector_radar(sector_scores),
                use_container_width=True
            )
        with col2:
            st.subheader("Sector Recommendations")
            for sector, score in sorted(sector_scores.items(), key=lambda x: x[1], reverse=True):
                st.progress(score, text=f"{sector}: {score:.0%} favorable")
        
        # Favorable Times
        st.header("Favorable Trading Times")
        favorable_times = find_favorable_times(chart_data["aspects"])
        
        if favorable_times:
            st.dataframe(
                pd.DataFrame(favorable_times),
                hide_index=True,
                use_container_width=True
            )
            
            # Current transits
            st.subheader("Current Planetary Hours")
            current_hour = (datetime.now().hour + 1) % 24
            planetary_hours = [
                ("Sun", "Leadership assets"),
                ("Moon", "Emotional markets"),
                ("Mars", "Energy/defense"),
                ("Mercury", "Tech/communication"),
                ("Jupiter", "Banking/expansion"),
                ("Venus", "Luxury/relationships"),
                ("Saturn", "Structure/mining")
            ]
            current_planet, current_sector = planetary_hours[current_hour // 3.43]  # Approximate
            
            st.markdown(f"""
            **Current Hour Ruler:** {current_planet}  
            **Focus Sectors:** {current_sector}  
            **Next Change:** In {(3.43 - (current_hour % 3.43)):.1f} hours
            """)
        else:
            st.warning("No strong favorable periods detected")
        
        # Market Data
        st.header("Current Market Conditions")
        for sector, data in MARKET_SECTORS.items():
            with st.expander(f"{sector} Market"):
                market_data = get_market_data(data["tickers"])
                cols = st.columns(len(market_data))
                for idx, (ticker, values) in enumerate(market_data.items()):
                    with cols[idx]:
                        st.metric(
                            label=ticker,
                            value=f"${values['price']:,}",
                            delta=f"{values['change']:.2f}%",
                            help=f"Volume: {values['volume']:,}"
                        )
        
        # Advanced Techniques
        st.header("Advanced Techniques")
        
        with st.expander("Planetary Transits"):
            st.markdown("""
            **Current Transits:**
            - Jupiter in Taurus: Favorable for commodities
            - Saturn in Pisces: Caution in liquid assets
            - Pluto in Aquarius: Tech transformations
            """)
        
        with st.expander("Lunar Phases"):
            st.markdown("""
            **Current Moon Phase:** Waxing Crescent (Building momentum)  
            **Next Full Moon:** 2023-09-29 (Emotional peak)  
            **Trading Strategy:** Accumulate during waxing, distribute during waning
            """)
        
        with st.expander("Fixed Stars"):
            st.markdown("""
            **Regulus (29° Leo):** Success with risk of downfall  
            **Aldebaran (10° Gemini):** Financial partnerships  
            **Antares (10° Sagittarius):** Volatile opportunities
            """)
    
    else:
        st.warning("Please generate a natal chart using the sidebar inputs")
        st.image("https://www.astro-seek.com/birth-chart/horoscope-wheel.gif", width=500)

if __name__ == "__main__":
    main()
