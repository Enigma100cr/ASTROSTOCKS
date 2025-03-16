# Astro-Trading App

## Overview

The Astro-Trading App is a comprehensive tool designed to integrate astrological strategies with financial market analysis. It provides insights into Forex, Indian, and global markets by combining astrological data with market trends. The app includes visualizations of planetary positions, market data, and trading strategies extracted from PDF documents.

## Features

- **Astrological Data**: Scrapes and displays current planetary positions.
- **Market Data**: Fetches and visualizes market data for selected tickers.
- **Trading Strategies**: Extracts and displays trading strategies from PDF documents.
- **Visualizations**: Provides interactive charts and visualizations for both astrological and market data.
- **SEBI Disclaimer**: Includes a disclaimer to ensure users understand the educational nature of the app.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/astro-trading-app.git
   cd astro-trading-app
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv astro_trading_env
   source astro_trading_env/bin/activate  # On Windows use `astro_trading_env\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the App**:
   ```bash
   streamlit run app.py
   ```

2. **Navigate the App**:
   - **Sidebar**: Select the market type, enter the ticker symbol, and specify the date range.
   - **Main Page**: View astrological data, market data, visualizations, and trading strategies.

## File Structure

- `app.py`: Main Streamlit application script.
- `requirements.txt`: List of Python dependencies.
- `README.md`: This file, providing an overview and instructions for the app.
- `Comprehensive_Stock_Market_Astrology_Analysis (2).pdf`: Sample PDF containing trading strategies.

## Dependencies

- **Streamlit**: For building and running the web app.
- **Requests**: For making HTTP requests to scrape data.
- **BeautifulSoup**: For parsing HTML content.
- **Pandas**: For data manipulation and analysis.
- **NumPy**: For numerical computations.
- **Matplotlib**: For creating static visualizations.
- **Plotly**: For creating interactive visualizations.
- **yfinance**: For fetching market data.
- **pdfplumber**: For extracting text from PDF documents.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This app is for educational purposes only. Consult a financial advisor before making any investment decisions. The developers are not responsible for any financial losses incurred by using this app.

## Contact

For any questions or suggestions, please contact [Your Email Address].

---

This `README.md` provides a comprehensive guide to setting up, using, and contributing to the Astro-Trading App. It ensures that users have all the necessary information to get started and understand the purpose and functionality of the app.
