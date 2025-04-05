import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import pytz
from bs4 import Comment
import time
from urllib.parse import urljoin
import random

# Configure Streamlit
st.set_page_config(
    page_title="Advanced Astrology Scraper",
    page_icon="♋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
ASTROSEEK_URL = "https://www.astro-seek.com"
ASTRO_URLS = {
    "astro-seek": {
        "base": "https://www.astro-seek.com",
        "natal": "/birth-chart",
        "transit": "/current-planets-astrology-transits"
    },
    "astro.com": {
        "base": "https://www.astro.com",
        "natal": "/cgi/chart.cgi"
    },
    "cafeastrology": {
        "base": "https://www.cafeastrology.com",
        "natal": "/natalastrology.html"
    }
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Helper functions
def get_random_header():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def safe_request(url, max_retries=3, timeout=10):
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=get_random_header(),
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def clean_text(text):
    """Clean and normalize text from HTML"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    return text

# AstroSeek Scraper
class AstroSeekScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(get_random_header())
        self.base_url = ASTROSEEK_URL

    def get_natal_chart(self, birth_data):
        """Get natal chart data from AstroSeek"""
        try:
            # Step 1: Load the initial form
            form_url = urljoin(self.base_url, "/birth-chart")
            response = self.session.get(form_url, timeout=10)
            response.raise_for_status()
            
            # Step 2: Submit the form
            post_url = urljoin(self.base_url, "/birth-chart")
            form_data = {
                'narozeni_den': birth_data['day'],
                'narozeni_mesic': birth_data['month'],
                'narozeni_rok': birth_data['year'],
                'narozeni_hodina': birth_data['hour'],
                'narozeni_minuta': birth_data['minute'],
                'narozeni_mesto': birth_data['city'],
                'narozeni_zeme': birth_data['country'],
                'submit': 'Calculate'
            }
            
            response = self.session.post(post_url, data=form_data, timeout=15)
            response.raise_for_status()
            
            # Step 3: Parse the results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            chart_info = {
                'url': response.url,
                'timestamp': datetime.now().isoformat(),
                'source': 'astro-seek'
            }
            
            # Extract planetary positions
            planets = self._extract_planets(soup)
            
            # Extract aspects
            aspects = self._extract_aspects(soup)
            
            # Extract houses
            houses = self._extract_houses(soup)
            
            return {
                'success': True,
                'chart_info': chart_info,
                'planets': planets,
                'aspects': aspects,
                'houses': houses
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _extract_planets(self, soup):
        """Extract planetary positions from the chart"""
        planets = []
        table = soup.find('table', {'id': 'tab_planety'})
        
        if table:
            for row in table.find_all('tr')[1:12]:  # Skip header and include up to Pluto
                cols = row.find_all('td')
                if len(cols) >= 7:
                    planet_data = {
                        'planet': clean_text(cols[0].text),
                        'sign': clean_text(cols[1].text),
                        'degree': clean_text(cols[2].text),
                        'speed': clean_text(cols[3].text),
                        'house': clean_text(cols[6].text),
                        'retrograde': 'R' in cols[0].text
                    }
                    planets.append(planet_data)
        
        return planets

    def _extract_aspects(self, soup):
        """Extract aspects between planets"""
        aspects = []
        table = soup.find('table', {'id': 'tab_aspekty'})
        
        if table:
            for row in table.find_all('tr')[1:6]:  # Top 5 major aspects
                cols = row.find_all('td')
                if len(cols) >= 4:
                    aspect_data = {
                        'planets': clean_text(cols[0].text),
                        'aspect': clean_text(cols[1].text),
                        'orb': clean_text(cols[2].text),
                        'effect': clean_text(cols[3].text)
                    }
                    aspects.append(aspect_data)
        
        return aspects

    def _extract_houses(self, soup):
        """Extract house cusps"""
        houses = []
        table = soup.find('table', {'id': 'tab_houses'})
        
        if table:
            for row in table.find_all('tr')[1:13]:  # 12 houses
                cols = row.find_all('td')
                if len(cols) >= 3:
                    house_data = {
                        'house': clean_text(cols[0].text),
                        'sign': clean_text(cols[1].text),
                        'degree': clean_text(cols[2].text)
                    }
                    houses.append(house_data)
        
        return houses

# Streamlit UI
def main():
    st.title("Advanced Astrological Chart Scraper")
    st.markdown("### Extract natal charts from astrology websites")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Chart Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            day = st.number_input("Day", min_value=1, max_value=31, value=1)
            month = st.number_input("Month", min_value=1, max_value=12, value=1)
            year = st.number_input("Year", min_value=1900, max_value=2050, value=2000)
        with col2:
            hour = st.number_input("Hour", min_value=0, max_value=23, value=12)
            minute = st.number_input("Minute", min_value=0, max_value=59, value=0)
        
        city = st.text_input("City", "New York")
        country = st.text_input("Country", "USA")
        
        website = st.selectbox(
            "Select Astrology Website",
            list(ASTRO_URLS.keys()),
            index=0
        )
        
        if st.button("Get Natal Chart"):
            birth_data = {
                'day': day,
                'month': month,
                'year': year,
                'hour': hour,
                'minute': minute,
                'city': city,
                'country': country
            }
            
            with st.spinner(f"Fetching data from {website}..."):
                if website == "astro-seek":
                    scraper = AstroSeekScraper()
                    result = scraper.get_natal_chart(birth_data)
                    
                    if result['success']:
                        st.session_state['chart_data'] = result
                        st.success("Successfully retrieved chart data!")
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
                else:
                    st.warning(f"Scraper for {website} coming soon!")

    # Display results
    if 'chart_data' in st.session_state:
        data = st.session_state['chart_data']
        
        st.header("Natal Chart Analysis")
        st.markdown(f"**Source:** {data['chart_info']['source']} | **URL:** {data['chart_info']['url']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Planetary Positions")
            if data['planets']:
                planets_df = pd.DataFrame(data['planets'])
                st.dataframe(planets_df, hide_index=True)
            else:
                st.warning("No planetary data found")
            
            st.subheader("Houses")
            if data['houses']:
                houses_df = pd.DataFrame(data['houses'])
                st.dataframe(houses_df, hide_index=True)
            else:
                st.warning("No house data found")
        
        with col2:
            st.subheader("Major Aspects")
            if data['aspects']:
                aspects_df = pd.DataFrame(data['aspects'])
                st.dataframe(aspects_df, hide_index=True)
            else:
                st.warning("No aspect data found")
            
            st.subheader("Chart Summary")
            if data['planets']:
                sun_sign = next((p['sign'] for p in data['planets'] if p['planet'] == 'Sun'), 'Unknown')
                moon_sign = next((p['sign'] for p in data['planets'] if p['planet'] == 'Moon'), 'Unknown')
                rising_sign = next((p['sign'] for p in data['houses'] if p['house'] == '1st House'), 'Unknown')
                
                st.markdown(f"""
                - **Sun Sign:** {sun_sign}
                - **Moon Sign:** {moon_sign}
                - **Rising Sign:** {rising_sign}
                - **Planets in Angular Houses:** {
                    sum(1 for p in data['planets'] 
                    if p['house'] in ['1st House', '4th House', '7th House', '10th House'])
                }
                - **Retrograde Planets:** {
                    sum(1 for p in data['planets'] if p.get('retrograde', False))
                }
                """)
        
        # Advanced Analysis
        st.header("Advanced Analysis")
        
        with st.expander("Planetary Dominance"):
            if data['planets']:
                signs = [p['sign'] for p in data['planets']]
                sign_counts = pd.Series(signs).value_counts()
                st.bar_chart(sign_counts)
        
        with st.expander("Aspect Patterns"):
            if data['aspects']:
                aspects = [a['aspect'] for a in data['aspects']]
                aspect_counts = pd.Series(aspects).value_counts()
                st.bar_chart(aspect_counts)
        
        with st.expander("Raw HTML"):
            if st.button("Show Raw Response (for debugging)"):
                response = safe_request(data['chart_info']['url'])
                if response:
                    st.code(response.text[:5000] + "...", language='html')

if __name__ == "__main__":
    main()
