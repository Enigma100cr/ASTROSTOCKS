import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import yfinance as yf
from transformers import pipeline

# Set page configuration
st.set_page_config(
    page_title="Financial Astrology Pro",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load free LLM model
@st.cache_resource
def load_astrology_llm():
    try:
        return pipeline('text-generation', model='gpt2')
    except Exception as e:
        st.error(f"Could not load AI model: {e}")
        return None

llm = load_astrology_llm()

# Your provided financial astrology data
ASTROLOGY_DATA = {
    "planetary_positions": [
        {"Planet": "Sun", "Sign": "Leo", "Degree": "15°", "Effect": "Bullish energy in markets"},
        {"Planet": "Moon", "Sign": "Cancer", "Degree": "23°", "Effect": "Emotional trading"},
        {"Planet": "Mercury", "Sign": "Virgo", "Degree": "5°", "Effect": "Analytical market moves"},
        {"Planet": "Venus", "Sign": "Leo", "Degree": "19°", "Effect": "Luxury sector favored"},
        {"Planet": "Mars", "Sign": "Virgo", "Degree": "12°", "Effect": "Precision trading"},
        {"Planet": "Jupiter", "Sign": "Taurus", "Degree": "14°", "Effect": "Financial expansion"},
        {"Planet": "Saturn", "Sign": "Pisces", "Degree": "28°", "Effect": "Structural pressure"}
    ],
    "aspects": [
        {"Aspect": "Sun trine Jupiter", "Effect": "Bullish for growth stocks", "Duration": "Aug 20-30"},
        {"Aspect": "Mars square Moon", "Effect": "Increased volatility", "Duration": "Aug 22-24"},
        {"Aspect": "Mercury opposite Neptune", "Effect": "Confusing signals", "Duration": "Aug 25-27"}
    ],
    "market_correlations": [
        {"Sector": "Technology", "Planet": "Mercury/Uranus", "Bullish": "Mercury direct in Gemini", "Bearish": "Mercury retrograde"},
        {"Sector": "Finance", "Planet": "Jupiter", "Bullish": "Jupiter in Sagittarius", "Bearish": "Jupiter square Saturn"},
        {"Sector": "Energy", "Planet": "Mars/Pluto", "Bullish": "Mars in Scorpio", "Bearish": "Mars square Saturn"},
        {"Sector": "Healthcare", "Planet": "Neptune/Chiron", "Bullish": "Neptune in Pisces", "Bearish": "Neptune retrograde"},
        {"Sector": "Real Estate", "Planet": "Saturn", "Bullish": "Saturn in Capricorn", "Bearish": "Saturn retrograde"}
    ],
    "upcoming_events": [
        {"Date": "2023-08-27", "Event": "Mercury enters Libra", "Impact": "Communication sectors active"},
        {"Date": "2023-09-02", "Event": "Venus square Pluto", "Impact": "Relationship markets stressed"},
        {"Date": "2023-09-10", "Event": "Full Moon in Pisces", "Impact": "Emotional trading peaks"},
        {"Date": "2023-09-25", "Event": "Saturn goes direct", "Impact": "Structural market shifts"},
        {"Date": "2023-10-08", "Event": "Solar Eclipse", "Impact": "Major market turning point"}
    ]
}

# Get recent market data with error handling
def get_recent_market_data(tickers=["^GSPC", "GC=F", "CL=F", "BTC-USD"]):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    market_data = {}
    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            if not data.empty and len(data) > 1:
                # Ensure we have datetime index
                data = data.reset_index()
                if 'Date' not in data.columns:
                    data['Date'] = data.index
                
                market_data[ticker] = {
                    "current_price": round(data['Close'].iloc[-1], 2),
                    "change_pct": round((data['Close'].iloc[-1]/data['Close'].iloc[-2]-1)*100, 2),
                    "chart_data": data[['Date', 'Close']].copy()
                }
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
    
    return market_data

# Generate AI response with improved error handling
def ask_astrology_ai(question, context=""):
    if not llm:
        return "AI service is currently unavailable."
    
    prompt = f"""You are a financial astrologer with 20 years experience. 
    Combine astrological insights with technical market analysis to answer questions.
    Current astrological context: {context}
    
    Question: {question}
    
    Detailed Answer:"""
    
    try:
        response = llm(
            prompt,
            max_length=400,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True
        )
        generated_text = response[0]['generated_text']
        return generated_text.split("Detailed Answer:")[-1].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Main educational content with improved error handling
def show_educational_content():
    st.title("📚 Financial Astrology Masterclass")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Current Planetary Alignments")
        st.dataframe(pd.DataFrame(ASTROLOGY_DATA["planetary_positions"]), hide_index=True)
        
        st.subheader("Active Astrological Aspects")
        st.dataframe(pd.DataFrame(ASTROLOGY_DATA["aspects"]), hide_index=True)
        
        st.subheader("Market Performance Under Current Aspects")
        market_data = get_recent_market_data()
        
        if market_data:
            for ticker, data in market_data.items():
                st.metric(
                    label=ticker,
                    value=f"${data['current_price']}",
                    delta=f"{data['change_pct']}%"
                )
                
                try:
                    # Ensure we have valid data for plotting
                    if not data['chart_data'].empty and 'Date' in data['chart_data'].columns and 'Close' in data['chart_data'].columns:
                        fig = px.line(
                            data['chart_data'], 
                            x="Date", 
                            y="Close", 
                            title=f"{ticker} Price",
                            labels={'Close': 'Price ($)'}
                        )
                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Price",
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Incomplete data for {ticker} chart")
                except Exception as e:
                    st.error(f"Error creating chart for {ticker}: {str(e)}")
    
    with col2:
        st.subheader("Sector-Planet Correlations")
        st.dataframe(pd.DataFrame(ASTROLOGY_DATA["market_correlations"]), hide_index=True)
        
        st.subheader("Upcoming Astrological Events")
        events_df = pd.DataFrame(ASTROLOGY_DATA["upcoming_events"])
        events_df["Days Until"] = (pd.to_datetime(events_df["Date"]) - datetime.now()).dt.days
        st.dataframe(events_df, hide_index=True)
        
        st.subheader("Trading Strategies by Moon Phase")
        moon_phases = {
            "Phase": ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", 
                     "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"],
            "Strategy": ["Initiate new positions", "Add to winners", "Take partial profits", 
                        "Prepare to exit", "Take profits", "Reduce exposure", "Short selling", 
                        "Market analysis"],
            "Best Sectors": ["Growth stocks", "Technology", "Energy", "Healthcare", 
                           "Commodities", "Defensive", "Short ETFs", "Research"]
        }
        st.dataframe(pd.DataFrame(moon_phases), hide_index=True)

# AI Chat interface with improved error handling
def show_ai_chat():
    st.title("🔮 Financial Astrology Advisor")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input
    if prompt := st.chat_input("Ask about astrology and markets..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate context from current astrological data
        current_context = {
            "planetary_positions": ASTROLOGY_DATA["planetary_positions"],
            "active_aspects": ASTROLOGY_DATA["aspects"],
            "upcoming_events": ASTROLOGY_DATA["upcoming_events"]
        }
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Consulting the stars..."):
                try:
                    response = ask_astrology_ai(prompt, str(current_context))
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Main app with improved error handling
def main():
    st.sidebar.image("https://via.placeholder.com/200x50?text=AstroTrader+Pro", width=200)
    st.sidebar.title("Navigation")
    
    app_mode = st.sidebar.radio("Select Mode", [
        "📊 Learn Financial Astrology", 
        "💬 Consult Astro Advisor",
        "📆 Astrological Calendar"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Astrological Highlights")
    
    today = datetime.now().strftime("%Y-%m-%d")
    st.sidebar.write(f"Date: {today}")
    st.sidebar.write("Sun in Leo (Leadership energy)")
    st.sidebar.write("Mercury in Virgo (Analytical focus)")
    st.sidebar.write("Venus in Leo (Luxury favored)")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Trading Tips Today")
    st.sidebar.markdown("""
    - Good day for tech stocks (Mercury strong)
    - Avoid overtrading (Mars square Moon)
    - Focus on quality stocks (Virgo influence)
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.warning("""
    **Educational Purpose Only**
    Not financial advice. Astrological market analysis is experimental.
    """)
    
    try:
        if app_mode == "📊 Learn Financial Astrology":
            show_educational_content()
        elif app_mode == "💬 Consult Astro Advisor":
            show_ai_chat()
        else:
            st.title("📆 Astrological Trading Calendar")
            
            # Create calendar view with error handling
            try:
                calendar_data = []
                start_date = datetime.now()
                for i in range(30):  # Next 30 days
                    date = start_date + timedelta(days=i)
                    date_str = date.strftime("%Y-%m-%d")
                    
                    events = [e for e in ASTROLOGY_DATA["upcoming_events"] if e["Date"] == date_str]
                    
                    # Get aspects for this date
                    aspects_today = []
                    for aspect in ASTROLOGY_DATA["aspects"]:
                        if "-" in aspect.get("Duration", ""):
                            start, end = aspect["Duration"].split("-")
                            try:
                                start_date_aspect = datetime.strptime(f"{start} 2023", "%b %d %Y")
                                end_date_aspect = datetime.strptime(f"{end} 2023", "%b %d %Y")
                                if start_date_aspect <= date <= end_date_aspect:
                                    aspects_today.append(aspect["Aspect"])
                            except:
                                continue
                    
                    calendar_data.append({
                        "Date": date_str,
                        "Day": date.strftime("%A"),
                        "Moon Phase": "🌑" if i%7 == 0 else "🌓" if i%7 == 2 else "🌕" if i%7 == 4 else "🌗",
                        "Major Aspects": "\n".join(aspects_today),
                        "Events": "\n".join([e["Event"] for e in events]),
                        "Trading Outlook": "Bullish" if any("trine" in a.lower() for a in aspects_today) else "Neutral"
                    })
                
                st.dataframe(pd.DataFrame(calendar_data), hide_index=True, height=800)
            except Exception as e:
                st.error(f"Error generating calendar: {str(e)}")
    except Exception as e:
        st.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
