# app.py
"""
Conversational Investment Dashboard
Powered by Gemini 2.5 Flash
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import (
    load_portfolio,
    calculate_total_investment,
    calculate_growth,
    sector_summary,
    get_portfolio_insights_gemini
)
from chatbot import process_query, get_ai_response, get_stock_analysis_gemini
from stock_data import get_stock_prediction, get_multiple_stock_predictions, search_stock, get_popular_stocks

# Streamlit page setup
st.set_page_config(
    page_title="Gemini 2.5 Flash Investment Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Gemini theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4285f4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #4285f4, #34a853, #fbbc05, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .gemini-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4285f4;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4285f4;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .chat-user {
        background-color: #e3f2fd;
        padding: 12px;
        border-radius: 12px;
        margin: 8px 0;
        border: 1px solid #bbdefb;
    }
    .chat-bot {
        background-color: #f3e5f5;
        padding: 12px;
        border-radius: 12px;
        margin: 8px 0;
        border: 1px solid #e1bee7;
    }
    .prediction-positive {
        background-color: #e8f5e8;
        border-left: 4px solid #34a853;
    }
    .prediction-negative {
        background-color: #ffeaea;
        border-left: 4px solid #ea4335;
    }
</style>
""", unsafe_allow_html=True)

# Title with Gemini branding
st.markdown('<h1 class="main-header">🚀 Gemini 2.5 Flash Investment Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="gemini-card">
    <h3>🎯 Powered by Google's Gemini 2.5 Flash</h3>
    <p>Experience advanced AI-powered portfolio analysis and stock predictions with cutting-edge technology.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
### 🎯 What You Can Do:
- 📊 **Upload & Analyze** your portfolio CSV
- 🏦 **Sector-wise** analytics with deep insights  
- 💬 **Chat** with Gemini 2.5 Flash AI assistant
- 🔮 **Live stock predictions** with ML + AI analysis
- 📈 **Advanced analytics** with risk assessment
""")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "portfolio_data" not in st.session_state:
    st.session_state.portfolio_data = None
if "gemini_status" not in st.session_state:
    from chatbot import model
    st.session_state.gemini_status = "✅ Connected" if model else "❌ Disconnected"

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    # Gemini Status
    st.markdown(f"**Gemini 2.5 Flash Status:** {st.session_state.gemini_status}")
    
    # File upload
    uploaded_file = st.file_uploader("📁 Upload Portfolio CSV", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.portfolio_data = df
            st.success("✅ Portfolio uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Error reading CSV: {e}")
    else:
        # Sample data
        try:
            sample_data = {
                'Date': ['2024-01-10', '2024-02-12', '2024-03-15', '2024-04-01', '2024-04-20', 
                        '2024-05-10', '2024-06-05', '2024-07-01', '2024-07-25', '2024-08-15'],
                'Stock': ['INFY', 'TCS', 'HDFCBANK', 'ICICIBANK', 'ITC', 
                         'HUL', 'RELIANCE', 'ONGC', 'TITAN', 'DMART'],
                'Sector': ['Tech', 'Tech', 'Finance', 'Finance', 'FMCG', 
                          'FMCG', 'Energy', 'Energy', 'Consumer', 'Retail'],
                'Investment': [10000, 8000, 12000, 9000, 7000, 8000, 11000, 6000, 9000, 10000],
                'Current Value': [12500, 9400, 13500, 9800, 7600, 8500, 12300, 6700, 9900, 11500]
            }
            df = pd.DataFrame(sample_data)
            st.session_state.portfolio_data = df
            st.info("ℹ️ Using sample portfolio. Upload your CSV for personal analysis.")
        except Exception as e:
            st.error(f"❌ Error loading sample: {e}")

    # Quick Actions
    st.header("🚀 Quick Actions")
    
    if st.button("📈 Portfolio Summary", use_container_width=True):
        if st.session_state.portfolio_data is not None:
            st.session_state.chat_history.append(("🧑 You", "Show portfolio summary"))
            total_inv, total_cur = calculate_total_investment(st.session_state.portfolio_data)
            df_growth, avg_growth = calculate_growth(st.session_state.portfolio_data)
            response = f"**Portfolio Summary:**\n- Total Investment: ₹{total_inv:,.2f}\n- Current Value: ₹{total_cur:,.2f}\n- Average Growth: {avg_growth:.2f}%"
            st.session_state.chat_history.append(("🤖 Assistant", response))
    
    if st.button("🏦 Sector Performance", use_container_width=True):
        if st.session_state.portfolio_data is not None:
            st.session_state.chat_history.append(("🧑 You", "Show sector performance"))
            sector_data = sector_summary(st.session_state.portfolio_data)
            if not sector_data.empty:
                sector_info = "\n".join([f"- {row['Sector']}: {row['Growth %']:.2f}%" for _, row in sector_data.iterrows()])
                response = f"**Sector Performance:**\n{sector_info}"
                st.session_state.chat_history.append(("🤖 Assistant", response))
    
    if st.button("🔮 Stock Insights", use_container_width=True):
        if st.session_state.portfolio_data is not None:
            st.session_state.chat_history.append(("🧑 You", "Give me stock insights"))
            response = "💡 For stock predictions, type 'Stock TICKER' (e.g., 'Stock AAPL', 'Stock TSLA')"
            st.session_state.chat_history.append(("🤖 Assistant", response))

# --- MAIN DASHBOARD ---
df = st.session_state.portfolio_data

if df is not None:
    # Portfolio Data
    st.subheader("📊 Portfolio Data")
    st.dataframe(df, use_container_width=True)
    
    # Analytics
    try:
        total_inv, total_cur = calculate_total_investment(df)
        df_growth, avg_growth = calculate_growth(df)
        sector_data = sector_summary(df_growth)
        total_profit = total_cur - total_inv
        
        # KPI Metrics
        st.subheader("📈 Portfolio Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Investment</h3>
                <h2>₹{total_inv:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Current Value</h3>
                <h2>₹{total_cur:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Profit</h3>
                <h2>₹{total_profit:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Avg Growth %</h3>
                <h2>{avg_growth:.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏦 Sector-wise Growth")
            if not sector_data.empty:
                fig = px.bar(
                    sector_data,
                    x="Sector",
                    y="Growth %",
                    color="Growth %",
                    text="Growth %",
                    title="Sector Growth Overview",
                    color_continuous_scale="Viridis"
                )
                fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig.update_layout(showlegend=False, yaxis_title="Growth %")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💰 Investment Distribution")
            if not sector_data.empty:
                fig = px.pie(
                    sector_data,
                    values="Investment",
                    names="Sector",
                    title="Investment by Sector",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Analytics error: {e}")

# --- STOCK PREDICTION SECTION ---
st.markdown("---")
st.subheader("🔮 Global Stock Predictions with Gemini 2.5 Flash")

pred_col1, pred_col2 = st.columns([1, 3])

# Initialize variables
recent_data = pd.DataFrame()
prediction_result = None

with pred_col1:
    st.markdown("### 📊 Stock Analysis")
    
    # Stock search with suggestions
    stock_ticker = st.text_input("Enter Stock Ticker or Company Name", "AAPL", key="stock_ticker").upper()
    
    # Show popular stocks
    st.markdown("**💡 Popular Stocks:**")
    popular_col1, popular_col2 = st.columns(2)
    
    with popular_col1:
        if st.button("US Stocks", use_container_width=True):
            st.session_state.chat_history.append(("🧑 You", "Show US stocks"))
            response = "**US Stocks**: AAPL, TSLA, GOOGL, MSFT, AMZN, META, NFLX, NVDA"
            st.session_state.chat_history.append(("🤖 Assistant", response))
    
    with popular_col2:
        if st.button("Indian Stocks", use_container_width=True):
            st.session_state.chat_history.append(("🧑 You", "Show Indian stocks"))
            response = "**Indian Stocks**: TCS.NS, INFY.NS, RELIANCE.NS, HDFCBANK.NS, ICICIBANK.NS"
            st.session_state.chat_history.append(("🤖 Assistant", response))
    
    # Prediction button
    col1, col2 = st.columns(2)
    with col1:
        predict_button = st.button("🚀 Get Prediction", use_container_width=True)
    with col2:
        if st.button("🔍 Search Help", use_container_width=True):
            st.session_state.chat_history.append(("🧑 You", "Stock search help"))
            response = """**Stock Symbol Guide**:
- **US Stocks**: AAPL, TSLA, GOOGL (no suffix needed)
- **Indian Stocks**: TCS.NS, INFY.NS (.NS suffix)
- **UK Stocks**: HSBA.L, BP.L (.L suffix)  
- **Canadian Stocks**: RY.TO, TD.TO (.TO suffix)"""
            st.session_state.chat_history.append(("🤖 Assistant", response))
    
    if predict_button:
        with st.spinner(f"🔮 Gemini 2.5 Flash analyzing {stock_ticker}..."):
            try:
                # First try to search if it's a company name
                from stock_data import search_stock
                actual_symbol = search_stock(stock_ticker)
                if actual_symbol and actual_symbol != stock_ticker:
                    st.info(f"🔍 Found: {stock_ticker} → {actual_symbol}")
                    stock_ticker = actual_symbol
                
                prediction_result, recent_data = get_stock_prediction(stock_ticker)
                
                if isinstance(prediction_result, dict):
                    st.success("🎯 Advanced Prediction Completed!")
                    
                    # Get currency symbol
                    currency_symbol = prediction_result.get('currency_symbol', '$')
                    
                    # Display main metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    prediction_class = "prediction-positive" if prediction_result['change_percent'] > 0 else "prediction-negative"
                    
                    with col1:
                        st.metric("Current Price", f"{currency_symbol}{prediction_result['current_price']:,.2f}")
                    with col2:
                        st.metric("Predicted Price", f"{currency_symbol}{prediction_result['predicted_price']:,.2f}")
                    with col3:
                        st.metric("Trend", prediction_result['trend'])
                    with col4:
                        st.metric("Change %", f"{prediction_result['change_percent']}%")
                    
                    # Additional info
                    st.markdown(f"""
                    <div class="{prediction_class}">
                        <h4>📋 Prediction Details</h4>
                        <p><strong>Company:</strong> {prediction_result.get('company_name', stock_ticker)}</p>
                        <p><strong>Sector:</strong> {prediction_result.get('sector', 'N/A')}</p>
                        <p><strong>Currency:</strong> {prediction_result.get('currency', 'USD')}</p>
                        <p><strong>Model Confidence:</strong> {prediction_result['model_accuracy']}%</p>
                        <p><strong>Data Points:</strong> {prediction_result['data_points']} days</p>
                        <p><strong>Symbol Used:</strong> {prediction_result.get('complete_ticker', stock_ticker)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get Gemini 2.5 Flash analysis
                    analysis = get_stock_analysis_gemini(stock_ticker, prediction_result, recent_data)
                    st.markdown("### 🧠 Gemini 2.5 Flash Analysis")
                    st.info(analysis)
                    
                else:
                    st.error(f"❌ {prediction_result}")
                    
                    # Show suggestions
                    from stock_data import get_stock_suggestions
                    suggestions = get_stock_suggestions(stock_ticker)
                    st.warning(f"💡 **Suggestions**: {suggestions}")
                    
            except Exception as e:
                st.error(f"❌ Prediction error: {str(e)}")

with pred_col2:
    # Show charts and data
    if predict_button and not recent_data.empty and isinstance(prediction_result, dict):
        st.subheader(f"📈 {stock_ticker} Advanced Analysis")
        
        # Get currency symbol for chart
        currency_symbol = prediction_result.get('currency_symbol', '$')
        
        # Price trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recent_data.index, 
            y=recent_data['Close'], 
            mode='lines', 
            name='Close Price', 
            line=dict(color='#4285f4', width=3)
        ))
        
        # Add predicted price
        last_date = recent_data.index[-1]
        next_date = last_date + pd.Timedelta(days=1)
        fig.add_trace(go.Scatter(
            x=[next_date], 
            y=[prediction_result['predicted_price']],
            mode='markers+text',
            name='Predicted Price',
            marker=dict(color='#ea4335', size=15, symbol='star'),
            text=[f"Predicted: {currency_symbol}{prediction_result['predicted_price']}"],
            textposition="top center"
        ))
        
        fig.update_layout(
            title=f"{stock_ticker} Price Trend & Prediction",
            xaxis_title="Date",
            yaxis_title=f"Price ({currency_symbol})",
            showlegend=True,
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical indicators
        if len(recent_data) > 10:
            st.subheader("📊 Technical Indicators")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                price_change = ((recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[-5]) / recent_data['Close'].iloc[-5]) * 100
                st.metric("5-Day Change", f"{price_change:.2f}%")
            
            with col2:
                volatility = recent_data['Close'].pct_change().std() * 100
                st.metric("Volatility", f"{volatility:.2f}%")
            
            with col3:
                avg_volume = recent_data['Volume'].mean()
                st.metric("Avg Volume", f"{avg_volume:,.0f}")
                
            with col4:
                rsi = recent_data['RSI'].iloc[-1] if 'RSI' in recent_data.columns else 50
                st.metric("RSI", f"{rsi:.1f}")

        # Recent data table
        st.subheader("📋 Recent Price Data")
        display_data = recent_data.tail()[['Open', 'High', 'Low', 'Close', 'Volume']].round(2)
        st.dataframe(display_data.style.format({
            'Open': f'{currency_symbol}{{:.2f}}',
            'High': f'{currency_symbol}{{:.2f}}',
            'Low': f'{currency_symbol}{{:.2f}}',
            'Close': f'{currency_symbol}{{:.2f}}',
            'Volume': '{:,.0f}'
        }))
# --- CHATBOT SECTION ---
st.markdown("---")
st.subheader("💬 Chat with Gemini 2.5 Flash")

# Model status
if st.session_state.gemini_status == "✅ Connected":
    st.success("🚀 Gemini 2.5 Flash is ready for advanced analysis!")
else:
    st.warning("⚠️ Using enhanced rule-based mode. Check API configuration for Gemini 2.5 Flash.")

mode = st.radio(
    "Choose Assistant Mode:",
    ["Rule-based", "Gemini 2.5 Flash"],
    horizontal=True,
    key="chat_mode"
)

chat_mode = "rule" if mode == "Rule-based" else "gemini"

# Chat interface
user_input = st.text_input("💭 Ask Gemini 2.5 Flash anything about investments...", key="user_input")

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    ask_button = st.button("🚀 Ask", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

# Process buttons
if clear_button:
    st.session_state.chat_history = []
    st.rerun()

if ask_button:
    if not user_input.strip():
        st.warning("Please enter a question for Gemini 2.5 Flash.")
    else:
        # Process the query
        if user_input.lower().startswith("stock "):
            ticker = user_input.split()[1].upper() if len(user_input.split()) > 1 else "AAPL"
            st.session_state.chat_history.append(("🧑 You", user_input))
            
            with st.spinner(f"🔮 Gemini 2.5 Flash analyzing {ticker}..."):
                try:
                    prediction_result, recent_data = get_stock_prediction(ticker)
                    reply = get_stock_analysis_gemini(ticker, prediction_result, recent_data)
                except Exception as e:
                    reply = f"❌ Error analyzing {ticker}: {str(e)}"
            
            st.session_state.chat_history.append(("🤖 Assistant", reply))
        else:
            st.session_state.chat_history.append(("🧑 You", user_input))
            try:
                if st.session_state.portfolio_data is not None:
                    reply = process_query(user_input, st.session_state.portfolio_data, mode=chat_mode)
                else:
                    reply = "📊 Please upload a portfolio CSV first for personalized analysis."
            except Exception as e:
                reply = f"❌ Processing error: {str(e)}"
            st.session_state.chat_history.append(("🤖 Assistant", reply))

# Display chat history
if st.session_state.chat_history:
    st.subheader("💭 Conversation History")
    for speaker, msg in st.session_state.chat_history:
        if speaker == "🧑 You":
            st.markdown(f'<div class="chat-user"><b>{speaker}:</b> {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot"><b>{speaker}:</b> {msg}</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div class="gemini-card">
    <h3>🚀 Powered by Gemini 2.5 Flash</h3>
    <p>This dashboard uses Google's most advanced AI model for investment analysis and predictions.</p>
    
    <h4>💡 Try These Advanced Queries:</h4>
    <ul>
    <li>"Analyze my portfolio performance and suggest optimizations"</li>
    <li>"Stock AAPL - give me detailed technical analysis"</li>
    <li>"Which sectors in my portfolio are underperforming?"</li>
    <li>"Predict market trends for the next quarter"</li>
    <li>"Risk assessment of my current investments"</li>
    </ul>
    
    <p><strong>Stock Examples:</strong> AAPL, TSLA, GOOGL, MSFT, AMZN, NFLX, NVDA, META</p>
</div>
""", unsafe_allow_html=True)