import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import pytz
import json
from urllib.parse import urljoin
import random
import time
from fp.fp import FreeProxy

# Configure Streamlit
st.set_page_config(
    page_title="AstroScraper Pro",
    page_icon="🌠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
ASTROSEEK_BASE = "https://www.astro-seek.com"
ASTRO_DB = {
    "astro-seek": {
        "natal": {
            "url": "/birth-chart",
            "selectors": {
                "planets": ("table#tab_planety", {
                    "planet": "td:nth-of-type(1)",
                    "sign": "td:nth-of-type(2)",
                    "degree": "td:nth-of-type(3)",
                    "speed": "td:nth-of-type(4)",
                    "house": "td:nth-of-type(7)"
                }),
                "aspects": ("table#tab_aspekty", {
                    "planets": "td:nth-of-type(1)",
                    "type": "td:nth-of-type(2)",
                    "orb": "td:nth-of-type(3)",
                    "effect": "td:nth-of-type(4)"
                }),
                "houses": ("table#tab_houses", {
                    "house": "td:nth-of-type(1)",
                    "sign": "td:nth-of-type(2)",
                    "degree": "td:nth-of-type(3)"
                })
            }
        }
    }
}

class AdvancedAstroScraper:
    def __init__(self):
        self.session = requests.Session()
        self.proxy_pool = self._init_proxy_pool()
        self.user_agents = self._load_user_agents()
        
    def _init_proxy_pool(self):
        return FreeProxy(rand=True, anonym=True).get_proxy_list()
    
    def _load_user_agents(self):
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
            # ... (extensive list of 50+ user agents)
        ]
    
    def _rotate_proxy(self):
        proxy = random.choice(self.proxy_pool)
        self.session.proxies.update({"http": proxy, "https": proxy})
    
    def _get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": ASTROSEEK_BASE,
            "DNT": "1"
        }
    
    def scrape_natal_chart(self, birth_data, max_retries=5):
        """Advanced scraping with rotating proxies and headers"""
        form_data = self._prepare_form_data(birth_data)
        
        for attempt in range(max_retries):
            try:
                self._rotate_proxy()
                response = self.session.post(
                    urljoin(ASTROSEEK_BASE, ASTRO_DB["astro-seek"]["natal"]["url"]),
                    data=form_data,
                    headers=self._get_headers(),
                    timeout=15,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                return self._parse_response(response, birth_data)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    return {"error": f"Failed after {max_retries} attempts: {str(e)}"}
                time.sleep(2 ** attempt)
        
        return {"error": "Unknown scraping error"}

    def _prepare_form_data(self, birth_data):
        """Handle different date formats and localization"""
        return {
            'narozeni_den': birth_data['day'],
            'narozeni_mesic': birth_data['month'],
            'narozeni_rok': birth_data['year'],
            'narozeni_hodina': birth_data['hour'],
            'narozeni_minuta': birth_data['minute'],
            'narozeni_mesto': birth_data['city'],
            'narozeni_zeme': birth_data['country'],
            'submit': 'Calculate'
        }
    
    def _parse_response(self, response, birth_data):
        """Advanced parsing with fallback selectors"""
        soup = BeautifulSoup(response.text, 'html.parser')
        result = {"source": "astro-seek", "url": response.url}
        
        # Planetary positions
        planets = []
        planet_selector = ASTRO_DB["astro-seek"]["natal"]["selectors"]["planets"]
        table = soup.select_one(planet_selector[0])
        if table:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) >= 7:
                    planets.append({
                        "planet": self._clean_text(cols[0].text),
                        "sign": self._clean_text(cols[1].text),
                        "degree": self._clean_text(cols[2].text),
                        "speed": self._clean_text(cols[3].text),
                        "house": self._clean_text(cols[6].text),
                        "retrograde": "R" in cols[0].text
                    })
        result["planets"] = planets
        
        # Aspects parsing
        aspects = []
        aspect_selector = ASTRO_DB["astro-seek"]["natal"]["selectors"]["aspects"]
        table = soup.select_one(aspect_selector[0])
        if table:
            for row in table.find_all("tr")[1:6]:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    aspects.append({
                        "planets": self._clean_text(cols[0].text),
                        "type": self._clean_text(cols[1].text),
                        "orb": self._clean_text(cols[2].text),
                        "effect": self._clean_text(cols[3].text)
                    })
        result["aspects"] = aspects
        
        # House positions
        houses = []
        house_selector = ASTRO_DB["astro-seek"]["natal"]["selectors"]["houses"]
        table = soup.select_one(house_selector[0])
        if table:
            for row in table.find_all("tr")[1:13]:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    houses.append({
                        "house": self._clean_text(cols[0].text),
                        "sign": self._clean_text(cols[1].text),
                        "degree": self._clean_text(cols[2].text)
                    })
        result["houses"] = houses
        
        return result
    
    def _clean_text(self, text):
        """Advanced text normalization"""
        text = re.sub(r'\s+', ' ', text, flags=re.UNICODE).strip()
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        return text.encode('ascii', 'ignore').decode('ascii')

# Streamlit Interface
def main():
    st.title("🔮 AstroScraper Pro")
    st.markdown("### Advanced Astrological Chart Scraper")
    
    with st.sidebar:
        st.header("Birth Data Input")
        col1, col2 = st.columns(2)
        with col1:
            day = st.number_input("Day", 1, 31, 1)
            month = st.number_input("Month", 1, 12, 1)
            year = st.number_input("Year", 1900, 2100, 2000)
        with col2:
            hour = st.number_input("Hour", 0, 23, 12)
            minute = st.number_input("Minute", 0, 59, 0)
            tz = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index('UTC'))
        
        city = st.text_input("City", "London")
        country = st.text_input("Country", "United Kingdom")
        
        if st.button("Scrape Natal Chart"):
            birth_data = {
                "day": day, "month": month, "year": year,
                "hour": hour, "minute": minute,
                "city": city, "country": country
            }
            
            with st.spinner("Scraping with advanced techniques..."):
                scraper = AdvancedAstroScraper()
                result = scraper.scrape_natal_chart(birth_data)
                
                if "error" in result:
                    st.error(f"Scraping failed: {result['error']}")
                else:
                    st.session_state.chart_data = result
                    st.success("Successfully scraped chart data!")

    if "chart_data" in st.session_state:
        data = st.session_state.chart_data
        
        st.header("Astrological Analysis")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Planetary Positions")
            planets_df = pd.DataFrame(data["planets"])
            st.dataframe(planets_df.style.applymap(color_retrograde), height=500)
            
            st.subheader("Houses")
            houses_df = pd.DataFrame(data["houses"])
            st.dataframe(houses_df, height=300)
        
        with col2:
            st.subheader("Aspect Analysis")
            aspects_df = pd.DataFrame(data["aspects"])
            st.dataframe(aspects_df, height=400)
            
            st.subheader("Advanced Metrics")
            st.plotly_chart(create_astro_chart(data), use_container_width=True)
            
            with st.expander("Raw Data"):
                st.json(data, expanded=False)

def color_retrograde(val):
    color = '#ffcccc' if 'R' in str(val) else ''
    return f'background-color: {color}'

def create_astro_chart(data):
    signs = pd.Series([p['sign'] for p in data['planets']]).value_counts()
    fig = go.Figure(go.Bar(
        x=signs.index,
        y=signs.values,
        marker_color='skyblue'
    ))
    fig.update_layout(
        title="Planetary Sign Distribution",
        xaxis_title="Zodiac Signs",
        yaxis_title="Count",
        height=400
    )
    return fig

if __name__ == "__main__":
    main()
