# stock_data.py
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

# Global stock exchange mappings
STOCK_EXCHANGES = {
    # US Stocks (no suffix needed)
    'AAPL': '', 'TSLA': '', 'GOOGL': '', 'MSFT': '', 'AMZN': '', 
    'META': '', 'NFLX': '', 'NVDA': '', 'AMD': '', 'INTC': '',
    'IBM': '', 'ORCL': '', 'CSCO': '', 'ADBE': '', 'CRM': '',
    'SPY': '', 'QQQ': '', 'VOO': '', 'IVV': '', 'GLD': '',
    
    # Indian Stocks (.NS for NSE)
    'TCS': '.NS', 'INFY': '.NS', 'RELIANCE': '.NS', 'HDFCBANK': '.NS',
    'ICICIBANK': '.NS', 'ITC': '.NS', 'HUL': '.NS', 'ONGC': '.NS',
    'TITAN': '.NS', 'DMART': '.NS', 'BAJFINANCE': '.NS', 'BHARTIARTL': '.NS',
    'KOTAKBANK': '.NS', 'SBIN': '.NS', 'AXISBANK': '.NS', 'MARUTI': '.NS',
    'SUNPHARMA': '.NS', 'TATAMOTORS': '.NS', 'WIPRO': '.NS', 'LT': '.NS',
    
    # UK Stocks (.L for London)
    'HSBA': '.L', 'BP': '.L', 'VOD': '.L', 'GSK': '.L', 'AZN': '.L',
    'BARC': '.L', 'LLOY': '.L', 'TSCO': '.L', 'RIO': '.L', 'NG': '.L',
    
    # Canadian Stocks (.TO for Toronto)
    'RY': '.TO', 'TD': '.TO', 'BNS': '.TO', 'BMO': '.TO', 'ENB': '.TO',
    'TRP': '.TO', 'CNR': '.TO', 'CP': '.TO', 'SHOP': '.TO', 'SU': '.TO',
    
    # European Stocks
    'ASML': '.AS',  # Netherlands
    'SAP': '.DE',   # Germany
    'ALV': '.DE',   # Germany
    'SIEGY': '',    # Siemens
    'NVO': '',      # Denmark
    
    # Asian Stocks
    'BABA': '',     # Alibaba
    'JD': '',       # JD.com
    'PDD': '',      # Pinduoduo
    'TSM': '',      # Taiwan Semiconductor
    'SONY': '',     # Sony
}

def get_complete_ticker(ticker):
    """Add exchange suffix to ticker if needed"""
    ticker_upper = ticker.upper()
    
    # If ticker already has a dot, return as is
    if '.' in ticker_upper:
        return ticker_upper
    
    # Check if we have exchange mapping
    if ticker_upper in STOCK_EXCHANGES:
        return ticker_upper + STOCK_EXCHANGES[ticker_upper]
    
    # For unknown stocks, try common exchanges
    common_exchanges = ['.NS', '.BO', '.L', '.TO', '.DE', '.AS', '.PA', '.SW']
    
    for exchange in common_exchanges:
        try:
            test_ticker = ticker_upper + exchange
            stock = yf.Ticker(test_ticker)
            info = stock.info
            if info and 'regularMarketPrice' in info:
                print(f"✅ Found {ticker} as {test_ticker}")
                return test_ticker
        except:
            continue
    
    # If no exchange found, try without suffix (might be US stock)
    return ticker_upper

def get_stock_prediction(ticker="AAPL"):
    """Get stock prediction with global stock support"""
    try:
        # Get complete ticker with exchange
        complete_ticker = get_complete_ticker(ticker)
        print(f"🔍 Analyzing: {complete_ticker}")
        
        # Get stock data
        stock = yf.Ticker(complete_ticker)
        data = stock.history(period="3mo", interval="1d")
        
        # Check if data is empty
        if data.empty:
            return f"❌ No data found for {ticker}. Try: {get_stock_suggestions(ticker)}", pd.DataFrame()
        
        if len(data) < 10:
            return f"❌ Not enough historical data for {ticker}. Only {len(data)} days available.", pd.DataFrame()
        
        # Clean data
        data_clean = data.dropna()
        
        if len(data_clean) < 5:
            return f"❌ Not enough clean data for {ticker} after processing.", pd.DataFrame()
        
        # Enhanced feature engineering
        data_clean = data_clean.copy()
        data_clean['Price_Range'] = data_clean['High'] - data_clean['Low']
        data_clean['Price_Change'] = data_clean['Close'] - data_clean['Open']
        data_clean['MA_5'] = data_clean['Close'].rolling(window=5).mean()
        data_clean['MA_10'] = data_clean['Close'].rolling(window=10).mean()
        data_clean['Volume_MA'] = data_clean['Volume'].rolling(window=5).mean()
        
        # Calculate RSI
        data_clean['RSI'] = calculate_rsi(data_clean['Close'])
        data_clean['Momentum'] = data_clean['Close'] - data_clean['Close'].shift(4)
        
        data_clean = data_clean.dropna()
        
        if len(data_clean) < 10:
            return f"❌ Insufficient data after feature engineering for {ticker}.", pd.DataFrame()
        
        # Prepare features
        feature_columns = ['Open', 'High', 'Low', 'Volume', 'Price_Range', 
                          'Price_Change', 'MA_5', 'MA_10', 'Volume_MA', 'RSI', 'Momentum']
        
        available_features = [col for col in feature_columns if col in data_clean.columns]
        X = data_clean[available_features]
        y = data_clean['Close']
        
        # Time-based split
        split_index = int(len(X) * 0.8)
        if split_index == 0:
            return f"❌ Not enough data for training {ticker}.", pd.DataFrame()
            
        X_train = X.iloc[:split_index]
        X_test = X.iloc[split_index:]
        y_train = y.iloc[:split_index]
        y_test = y.iloc[split_index:]
        
        if len(X_train) == 0:
            return f"❌ No training data available for {ticker}.", pd.DataFrame()
        
        # Train enhanced model
        model = RandomForestRegressor(
            n_estimators=100, 
            random_state=42,
            max_depth=15,
            min_samples_split=3,
            min_samples_leaf=2
        )
        model.fit(X_train, y_train)
        
        # Predict next price
        if len(X_test) > 0:
            latest_features = X_test.iloc[[-1]]
        else:
            latest_features = X_train.iloc[[-1]]
            
        predicted_price = model.predict(latest_features)[0]
        current_price = data_clean['Close'].iloc[-1]
        
        # Calculate metrics
        change_percent = ((predicted_price - current_price) / current_price) * 100
        
        # Calculate accuracy
        if len(X_test) > 0:
            y_pred_test = model.predict(X_test)
            accuracy = max(0, min(100, (1 - np.mean(np.abs((y_pred_test - y_test) / y_test))) * 100))
        else:
            accuracy = 85.0
        
        # Get company info
        try:
            info = stock.info
            company_name = info.get('longName', ticker)
            sector = info.get('sector', 'N/A')
            market_cap = info.get('marketCap', 'N/A')
            currency = info.get('currency', 'USD')
        except:
            company_name = ticker
            sector = 'N/A'
            market_cap = 'N/A'
            currency = 'USD'
        
        # Format currency symbol
        currency_symbol = get_currency_symbol(currency)
        
        result = {
            'ticker': ticker,
            'complete_ticker': complete_ticker,
            'company_name': company_name,
            'sector': sector,
            'market_cap': market_cap,
            'currency': currency,
            'currency_symbol': currency_symbol,
            'current_price': round(current_price, 2),
            'predicted_price': round(predicted_price, 2),
            'trend': 'Bullish 📈' if predicted_price > current_price else 'Bearish 📉',
            'change_percent': round(change_percent, 2),
            'price_difference': round(predicted_price - current_price, 2),
            'model_accuracy': round(accuracy, 2),
            'data_points': len(data_clean),
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'volume_trend': 'High' if data_clean['Volume'].mean() > data_clean['Volume'].median() else 'Normal'
        }
        
        return result, data_clean
        
    except Exception as e:
        error_msg = f"❌ Error analyzing {ticker}: {str(e)}"
        print(f"Detailed error: {error_msg}")
        return error_msg, pd.DataFrame()

def get_multiple_stock_predictions(tickers):
    """Get predictions for multiple stocks at once"""
    results = {}
    for ticker in tickers:
        try:
            prediction_result, data = get_stock_prediction(ticker)
            results[ticker] = {
                'prediction': prediction_result,
                'data': data
            }
            print(f"✅ Completed prediction for {ticker}")
        except Exception as e:
            results[ticker] = {
                'prediction': f"Error: {str(e)}",
                'data': pd.DataFrame()
            }
            print(f"❌ Failed prediction for {ticker}: {e}")
    
    return results

def get_currency_symbol(currency):
    """Get currency symbol"""
    symbols = {
        'USD': '$',
        'INR': '₹',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'C$',
        'AUD': 'A$',
        'JPY': '¥',
        'CNY': '¥'
    }
    return symbols.get(currency, '$')

def calculate_rsi(prices, window=14):
    """Calculate Relative Strength Index"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except:
        return pd.Series([np.nan] * len(prices), index=prices.index)

def get_stock_suggestions(ticker):
    """Provide helpful suggestions for stock symbols"""
    ticker_upper = ticker.upper()
    
    suggestions = {
        'TCS': 'Try TCS.NS for Tata Consultancy Services (India)',
        'INFY': 'Try INFY.NS for Infosys (India)',
        'RELIANCE': 'Try RELIANCE.NS for Reliance Industries (India)',
        'HDFC': 'Try HDFCBANK.NS for HDFC Bank (India)',
        'ICICI': 'Try ICICIBANK.NS for ICICI Bank (India)',
    }
    
    if ticker_upper in suggestions:
        return suggestions[ticker_upper]
    
    # General suggestions based on common errors
    common_suggestions = [
        "For Indian stocks, add .NS suffix (e.g., TCS.NS, INFY.NS)",
        "For UK stocks, add .L suffix (e.g., HSBA.L)",
        "For Canadian stocks, add .TO suffix (e.g., RY.TO)",
        "US stocks usually don't need suffix (e.g., AAPL, TSLA)"
    ]
    
    return " | ".join(common_suggestions)

def search_stock(query):
    """Search for stocks by company name"""
    try:
        # This is a simplified search - in production, you'd use a proper stock search API
        search_terms = {
            'tata consultancy': 'TCS.NS',
            'infosys': 'INFY.NS',
            'reliance': 'RELIANCE.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'icici bank': 'ICICIBANK.NS',
            'apple': 'AAPL',
            'tesla': 'TSLA',
            'google': 'GOOGL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
        }
        
        query_lower = query.lower()
        for term, symbol in search_terms.items():
            if term in query_lower:
                return symbol
        
        return None
    except:
        return None

def get_popular_stocks():
    """Get list of popular stocks by region"""
    return {
        'US Stocks': ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NFLX', 'NVDA'],
        'Indian Stocks': ['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'ICICIBANK.NS'],
        'UK Stocks': ['HSBA.L', 'BP.L', 'VOD.L', 'GSK.L'],
        'Canadian Stocks': ['RY.TO', 'TD.TO', 'SHOP.TO']
    }

def get_stock_info(ticker):
    """Get basic stock information"""
    try:
        complete_ticker = get_complete_ticker(ticker)
        stock = yf.Ticker(complete_ticker)
        info = stock.info
        
        return {
            'symbol': complete_ticker,
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'currency': info.get('currency', 'USD'),
            'exchange': info.get('exchange', 'N/A'),
            'country': info.get('country', 'N/A')
        }
    except Exception as e:
        return {
            'symbol': ticker,
            'name': ticker,
            'sector': 'N/A',
            'industry': 'N/A',
            'error': str(e)
        }