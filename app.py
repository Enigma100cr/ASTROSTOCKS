import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import random

# Configure page
st.set_page_config(
    page_title="Natal Chart Generator",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
ASTROSEEK_URL = "https://www.astro-seek.com/birth-chart"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

def get_random_useragent():
    return random.choice(USER_AGENTS)

def get_natal_chart(birth_datetime, city, country):
    """Retrieve natal chart data from AstroSeek"""
    try:
        headers = {'User-Agent': get_random_useragent()}
        
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
            session.get(ASTROSEEK_URL, headers=headers)
            response = session.post(ASTROSEEK_URL, data=params, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return parse_chart_data(soup)
            return None
            
    except Exception as e:
        st.error(f"Error retrieving chart: {str(e)}")
        return None

def parse_chart_data(soup):
    """Parse HTML response into structured data"""
    chart = {'planets': [], 'aspects': [], 'houses': []}
    
    # Parse planetary positions
    planet_table = soup.find('table', {'id': 'tab_planety'})
    if planet_table:
        for row in planet_table.find_all('tr')[1:12]:
            cols = row.find_all('td')
            chart['planets'].append({
                "Planet": cols[0].text.strip(),
                "Sign": cols[1].text.strip(),
                "Degree": cols[2].text.strip(),
                "House": cols[6].text.strip()
            })
    
    # Parse house cusps
    house_table = soup.find('table', {'id': 'tab_domy'})
    if house_table:
        for row in house_table.find_all('tr')[1:13]:
            cols = row.find_all('td')
            chart['houses'].append({
                "House": cols[0].text.strip(),
                "Sign": cols[1].text.strip(),
                "Degree": cols[2].text.strip()
            })
    
    # Parse aspects
    aspect_table = soup.find('table', {'id': 'tab_aspekty'})
    if aspect_table:
        for row in aspect_table.find_all('tr')[1:6]:
            cols = row.find_all('td')
            chart['aspects'].append({
                "Planets": cols[0].text.strip(),
                "Aspect": cols[1].text.strip(),
                "Orb": cols[2].text.strip()
            })
    
    return chart

def create_zodiac_chart(planets):
    """Create interactive zodiac visualization"""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    data = []
    for planet in planets:
        sign_idx = signs.index(planet['Sign'].split()[0])
        degree = float(planet['Degree'].split('°')[0])
        position = sign_idx * 30 + degree
        
        data.append({
            "Planet": planet['Planet'],
            "Sign": planet['Sign'],
            "Position": position,
            "Degree": degree
        })
    
    fig = px.line_polar(
        data, r=[30]*12, theta=[i*30 for i in range(12)],
        line_close=True, 
        direction='clockwise',
        start_angle=90
    )
    
    fig.update_traces(
        line_color='lightgray',
        line_width=1,
        showlegend=False
    )
    
    for point in data:
        fig.add_trace(px.scatter_polar(
            pd.DataFrame([point]),
            r=[30], theta=["Position"],
            text="Planet",
            hover_data=["Sign", "Degree"]
        ).data[0])
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickvals=[i*30 for i in range(12)],
                ticktext=signs
            )
        ),
        height=600
    )
    return fig

# Main app
def main():
    st.title("🌌 Natal Chart Generator")
    
    # Sidebar inputs
    with st.sidebar:
        st.header("Birth Information")
        birth_date = st.date_input("Date of Birth", value=datetime(2000, 1, 1))
        birth_time = st.time_input("Time of Birth", value=datetime(2000, 1, 1, 12, 0))
        birth_tz = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index('Asia/Kolkata'))
        city = st.text_input("City", "Mumbai")
        country = st.text_input("Country", "India")
        
        if st.button("Generate Natal Chart"):
            with st.spinner("Calculating planetary positions..."):
                tz = pytz.timezone(birth_tz)
                birth_datetime = tz.localize(datetime.combine(birth_date, birth_time))
                chart_data = get_natal_chart(birth_datetime, city, country)
                
                if chart_data:
                    st.session_state.chart_data = chart_data
                    st.success("Chart generated successfully!")
                else:
                    st.error("Failed to generate chart")

    # Main display
    if "chart_data" in st.session_state:
        chart = st.session_state.chart_data
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Planetary Positions")
            st.dataframe(
                pd.DataFrame(chart['planets']),
                use_container_width=True,
                hide_index=True
            )
            
            st.subheader("House Cusps")
            st.dataframe(
                pd.DataFrame(chart['houses']),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.subheader("Zodiac Chart")
            st.plotly_chart(create_zodiac_chart(chart['planets']), use_container_width=True)
            
            st.subheader("Major Aspects")
            st.dataframe(
                pd.DataFrame(chart['aspects']),
                use_container_width=True,
                hide_index=True
            )

if __name__ == "__main__":
    main()
