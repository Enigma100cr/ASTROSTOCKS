import streamlit as st
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Advanced Financial Astrology Analyzer",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Financial Astrology Principles (Your Specifications)
PRINCIPLES = {
    "planetary_rulers": {
        "Sun": {"Sectors": ["Government", "Gold"], "Effects": ["Confidence", "Leadership"]},
        "Moon": {"Sectors": ["Real Estate", "Agriculture"], "Effects": ["Emotions", "Liquidity"]},
        "Mercury": {"Sectors": ["Technology", "Communication"], "Effects": ["Information", "Volatility"]},
        "Venus": {"Sectors": ["Luxury", "Arts"], "Effects": ["Value", "Harmony"]},
        "Mars": {"Sectors": ["Energy", "Defense"], "Effects": ["Aggression", "Risk"]},
        "Jupiter": {"Sectors": ["Banking", "Expansion"], "Effects": ["Growth", "Optimism"]},
        "Saturn": {"Sectors": ["Mining", "Construction"], "Effects": ["Restriction", "Structure"]},
        "Uranus": {"Sectors": ["Innovation", "Cryptocurrency"], "Effects": ["Disruption", "Sudden Changes"]},
        "Neptune": {"Sectors": ["Pharma", "Spirituality"], "Effects": ["Illusion", "Speculation"]},
        "Pluto": {"Sectors": ["Power", "Transformation"], "Effects": ["Control", "Rebirth"]}
    },
    "aspect_interpretations": {
        "Conjunction": "Intensified focus in the combined areas",
        "Sextile": "Opportunities through the connected sectors",
        "Square": "Challenges requiring resolution between areas",
        "Trine": "Natural flow and harmony between sectors",
        "Opposition": "Polarization needing balance between forces"
    },
    "house_meanings": {
        "2nd": "Personal finances, currencies, values",
        "5th": "Speculation, entertainment, creativity",
        "8th": "Joint finances, crises, transformation",
        "10th": "Government, corporations, public image",
        "11th": "Technology, social networks, future trends"
    }
}

# Advanced Analysis Functions
def analyze_angular_houses(chart_data):
    """Analyze planets in angular houses (1st, 4th, 7th, 10th)"""
    angular_planets = []
    for planet in chart_data["planets"]:
        if planet["house"] in ["1st", "4th", "7th", "10th"]:
            angular_planets.append({
                "Planet": planet["name"],
                "House": planet["house"],
                "Influence": "Strong immediate impact on corresponding sectors",
                "Duration": "Short-term (days/weeks)"
            })
    return pd.DataFrame(angular_planets)

def analyze_aspect_patterns(aspects):
    """Identify significant aspect patterns"""
    patterns = []
    for aspect in aspects:
        if float(aspect["orb"].replace("°", "")) < 3:  # Tight orb
            patterns.append({
                "Planets": aspect["planets"],
                "Aspect": aspect["type"],
                "Orb": aspect["orb"],
                "Financial Meaning": PRINCIPLES["aspect_interpretations"][aspect["type"]],
                "Impact Duration": "Weeks" if "Sun" in aspect["planets"] or "Moon" in aspect["planets"] else "Months"
            })
    return pd.DataFrame(patterns)

def calculate_sector_strengths(chart_data):
    """Calculate sector strengths based on planetary positions"""
    sectors = {}
    for planet in chart_data["planets"]:
        for sector in PRINCIPLES["planetary_rulers"][planet["name"]]["Sectors"]:
            if sector not in sectors:
                sectors[sector] = 0
            # Add strength based on house position and dignity
            strength = 1
            if planet["house"] in ["1st", "10th"]:
                strength *= 2
            if planet["sign"] in ["Taurus", "Leo", "Scorpio", "Aquarius"]:  # Fixed signs = stability
                strength *= 1.5
            sectors[sector] += strength
    
    # Normalize and sort
    max_strength = max(sectors.values()) if sectors else 1
    return sorted(
        [{"Sector": k, "Strength": f"{v/max_strength:.0%}"} 
         for k, v in sectors.items()],
        key=lambda x: x["Strength"],
        reverse=True
    )

# Mock Chart Data Generator (Replace with real chart data)
def generate_sample_chart():
    """Generate a sample natal chart for demonstration"""
    planets = [
        {"name": "Sun", "sign": "Leo", "house": "10th", "dignity": "Domicile"},
        {"name": "Moon", "sign": "Cancer", "house": "4th", "dignity": "Domicile"},
        {"name": "Mercury", "sign": "Virgo", "house": "11th", "dignity": "Domicile"},
        {"name": "Venus", "sign": "Libra", "house": "12th", "dignity": "Domicile"},
        {"name": "Mars", "sign": "Scorpio", "house": "2nd", "dignity": "Domicile"},
        {"name": "Jupiter", "sign": "Pisces", "house": "5th", "dignity": "Domicile"},
        {"name": "Saturn", "sign": "Aquarius", "house": "5th", "dignity": "Domicile"},
        {"name": "Uranus", "sign": "Taurus", "house": "8th", "dignity": "Detriment"},
        {"name": "Neptune", "sign": "Pisces", "house": "6th", "dignity": "Domicile"},
        {"name": "Pluto", "sign": "Capricorn", "house": "4th", "dignity": "Exalted"}
    ]
    
    aspects = [
        {"planets": "Sun conjunct Jupiter", "type": "Conjunction", "orb": "0°32'"},
        {"planets": "Moon square Pluto", "type": "Square", "orb": "2°15'"},
        {"planets": "Mercury trine Uranus", "type": "Trine", "orb": "1°47'"},
        {"planets": "Venus sextile Mars", "type": "Sextile", "orb": "3°01'"},
        {"planets": "Saturn opposite Uranus", "type": "Opposition", "orb": "5°22'"}
    ]
    
    return {"planets": planets, "aspects": aspects}

# Visualization Functions
def create_radar_chart(sector_strengths):
    """Create radar chart of sector strengths"""
    categories = [s["Sector"] for s in sector_strengths]
    values = [float(s["Strength"].strip("%")) for s in sector_strengths]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Sector Strength'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Financial Sector Strengths"
    )
    return fig

# Main Application
def main():
    st.title("Advanced Financial Natal Chart Analysis")
    st.markdown("""
    ### Applying Classical Financial Astrology Principles
    """)
    
    # Generate or load natal chart data
    chart_data = generate_sample_chart()
    
    # Analysis Section
    st.header("Core Chart Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Angular Planets Analysis")
        angular_df = analyze_angular_houses(chart_data)
        if not angular_df.empty:
            st.dataframe(angular_df, hide_index=True)
        else:
            st.warning("No significant angular planets found")
        
        st.subheader("Sector Strengths")
        sector_strengths = calculate_sector_strengths(chart_data)
        if sector_strengths:
            st.plotly_chart(create_radar_chart(sector_strengths), use_container_width=True)
        else:
            st.warning("No sector strengths calculated")
    
    with col2:
        st.subheader("Aspect Pattern Analysis")
        aspect_df = analyze_aspect_patterns(chart_data["aspects"])
        if not aspect_df.empty:
            st.dataframe(aspect_df, hide_index=True)
        else:
            st.warning("No significant aspect patterns found")
        
        st.subheader("Planetary Dignities")
        dignities = pd.DataFrame([
            {
                "Planet": p["name"],
                "Sign": p["sign"],
                "House": p["house"],
                "Dignity": p["dignity"],
                "Effect": PRINCIPLES["planetary_rulers"][p["name"]]["Effects"][0]
            } for p in chart_data["planets"]
        ])
        st.dataframe(dignities, hide_index=True)
    
    # Advanced Techniques Section
    st.header("Advanced Techniques")
    
    with st.expander("Planetary Periods (Dasha Analysis)"):
        st.markdown("""
        **Current Major Period:** Jupiter-Mercury (Growth through communication sectors)
        
        **Sub-Period Focus:** 
        - Technology (Mercury-ruled)
        - Banking (Jupiter-ruled)
        - Expect increased volatility in these sectors
        """)
    
    with st.expander("Fixed Star Influences"):
        st.markdown("""
        **Regulus at 0° Virgo (10th House):** 
        - Success followed by dramatic reversal in corporate leadership
        
        **Aldebaran at 10° Gemini (7th House):** 
        - Important partnerships in tech sector
        """)
    
    with st.expander("Lunar Nodes Analysis"):
        st.markdown("""
        **North Node in Taurus (8th House):** 
        - Karmic direction toward value investing and joint finances
        
        **South Node in Scorpio (2nd House):** 
        - Release of old patterns in personal asset management
        """)
    
    # Sidebar
    st.sidebar.title("Analysis Parameters")
    analysis_date = st.sidebar.date_input("Select Analysis Date", datetime.now())
    house_system = st.sidebar.selectbox("House System", ["Placidus", "Koch", "Whole Sign"])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Financial Astrology Principles")
    principle = st.sidebar.selectbox("View Principle", list(PRINCIPLES.keys()))
    st.sidebar.json(PRINCIPLES[principle])
    
    st.sidebar.markdown("---")
    st.sidebar.warning("""
    **Advanced Interpretation Only**  
    For educational purposes.  
    Not financial advice.
    """)

if __name__ == "__main__":
    main()
