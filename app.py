import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pytz
from astropy.coordinates import solar_system_ephemeris, get_body
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz
import yfinance as yf
import swisseph as swe

# Function to calculate planetary positions for a natal chart
def calculate_natal_chart(birth_date, birth_time, birth_place):
    """
    Calculate the positions of planets for a natal chart.
    """
    # Convert birth date and time to astropy.Time object
    birth_time_utc = Time(f"{birth_date} {birth_time}", format='iso', scale='utc')
    
    # Define Earth location (latitude, longitude, elevation)
    location = EarthLocation.from_geodetic(lon=birth_place['longitude'], lat=birth_place['latitude'])
    
    # Get planetary positions
    planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    planet_positions = {}
    
    for planet in planets:
        planet_pos = get_body(planet, birth_time_utc, location)
        planet_positions[planet.capitalize()] = {
            'RA': planet_pos.ra.deg,  # Right Ascension
            'Dec': planet_pos.dec.deg,  # Declination
            'Distance': planet_pos.distance.au  # Distance from Earth in AU
        }
    
    return planet_positions

# Function to calculate aspects between planets
def calculate_aspects(planet_positions, aspect_orb=5):
    """
    Calculate aspects (conjunction, square, trine, etc.) between planets.
    """
    aspects = []
    planets = list(planet_positions.keys())
    
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            planet1 = planets[i]
            planet2 = planets[j]
            angle = abs(planet_positions[planet1]['RA'] - planet_positions[planet2]['RA'])
            angle = angle % 360  # Normalize to 0-360 degrees
            
            if angle < aspect_orb:
                aspects.append(f"{planet1} - {planet2}: Conjunction ({angle:.2f}°)")
            elif abs(angle - 90) < aspect_orb:
                aspects.append(f"{planet1} - {planet2}: Square ({angle:.2f}°)")
            elif abs(angle - 120) < aspect_orb:
                aspects.append(f"{planet1} - {planet2}: Trine ({angle:.2f}°)")
            elif abs(angle - 180) < aspect_orb:
                aspects.append(f"{planet1} - {planet2}: Opposition ({angle:.2f}°)")
    
    return aspects

# Function to calculate house divisions
def calculate_houses(birth_date, birth_time, birth_place, house_system='P'):
    """
    Calculate house divisions using the specified house system.
    """
    swe.set_ephe_path('/path/to/ephemeris')  # Set path to ephemeris files
    julian_day = swe.julday(birth_date.year, birth_date.month, birth_date.day, birth_time.hour + birth_time.minute / 60)
    houses = swe.houses(julian_day, birth_place['latitude'], birth_place['longitude'], house_system.encode())
    return houses

# Function to visualize natal chart
def visualize_natal_chart(planet_positions):
    """
    Create an interactive 3D visualization of the natal chart.
    """
    # Prepare data for visualization
    planets = list(planet_positions.keys())
    ra = [planet_positions[planet]['RA'] for planet in planets]
    dec = [planet_positions[planet]['Dec'] for planet in planets]
    distance = [planet_positions[planet]['Distance'] for planet in planets]
    
    # Create a 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=ra,
        y=dec,
        z=distance,
        mode='markers+text',
        text=planets,
        marker=dict(
            size=10,
            color=distance,
            colorscale='Viridis',
            opacity=0.8
        )
    )])
    
    # Update layout
    fig.update_layout(
        title="Natal Chart Visualization",
        scene=dict(
            xaxis_title='Right Ascension (RA)',
            yaxis_title='Declination (Dec)',
            zaxis_title='Distance from Earth (AU)'
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    
    return fig

# Function to get market data
def get_market_data(ticker, start_date, end_date):
    """
    Fetch market data using yfinance.
    """
    market_data = yf.download(ticker, start=start_date, end=end_date)
    return market_data

# Streamlit app
def main():
    st.title("Advanced Astro-Trading App with Natal Chart Analysis")
    
    # SEBI Disclaimer
    st.sidebar.header("SEBI Disclaimer")
    st.sidebar.write("This app is for educational purposes only. Consult a financial advisor before making any investment decisions.")
    
    # Sidebar for user inputs
    st.sidebar.header("User Input")
    market_type = st.sidebar.selectbox("Select Market", ["Forex", "Indian", "Global"])
    ticker = st.sidebar.text_input("Enter Ticker Symbol", "AAPL")
    start_date = st.sidebar.text_input("Start Date", "2023-01-01")
    end_date = st.sidebar.text_input("End Date", "2023-12-31")
    
    # Natal Chart Inputs
    st.sidebar.header("Natal Chart Analysis")
    birth_date = st.sidebar.date_input("Enter Birth Date", datetime.now())
    birth_time = st.sidebar.time_input("Enter Birth Time", datetime.now().time())
    birth_place = {
        'latitude': st.sidebar.number_input("Enter Latitude", value=28.6139),
        'longitude': st.sidebar.number_input("Enter Longitude", value=77.2090)
    }
    aspect_orb = st.sidebar.slider("Aspect Orb (degrees)", 1, 10, 5)
    house_system = st.sidebar.selectbox("House System", ["Placidus", "Koch", "Equal"])
    
    # Calculate Natal Chart
    if st.sidebar.button("Generate Natal Chart"):
        planet_positions = calculate_natal_chart(birth_date, birth_time, birth_place)
        st.header("Natal Chart Planetary Positions")
        st.write(pd.DataFrame(planet_positions).T)
        
        # Calculate Aspects
        st.header("Planetary Aspects")
        aspects = calculate_aspects(planet_positions, aspect_orb)
        for aspect in aspects:
            st.write(aspect)
        
        # Calculate House Divisions
        st.header("House Divisions")
        houses = calculate_houses(birth_date, birth_time, birth_place, house_system[0])
        st.write(pd.DataFrame(houses, columns=["House", "Degree"]))
        
        # Visualize Natal Chart
        st.header("Natal Chart Visualization")
        natal_chart_fig = visualize_natal_chart(planet_positions)
        st.plotly_chart(natal_chart_fig)
    
    # Get market data
    st.header("Market Data")
    market_data = get_market_data(ticker, start_date, end_date)
    st.write(market_data)
    
    # Plot market data
    st.header("Market Price Chart")
    fig = px.line(market_data, x=market_data.index, y='Close', title=f'{ticker} Closing Prices')
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
