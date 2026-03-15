"""
Chatbot module for Conversational Investment Dashboard
Using Latest Gemini 2.0 Flash Experimental with Fallbacks
"""

import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from analytics import calculate_total_investment, calculate_growth, sector_summary

# Load environment
load_dotenv()

# Configure Gemini with Latest Models
def setup_gemini_advanced():
    """Setup Gemini with latest models and intelligent fallbacks"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No Google API key found in .env file")
            return None
            
        genai.configure(api_key=api_key)
        
        # 🚀 LATEST MODEL HIERARCHY (Nov 2024)
        model_hierarchy = [
            # Tier 1: Latest Experimental Models (Highest Capability)
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash-thinking-exp',
            
            # Tier 2: Stable Production Models
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest',
            
            # Tier 3: Legacy Models (High Reliability)
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            
            # Tier 4: Original Models
            'gemini-1.0-pro',
            'gemini-pro'
        ]
        
        print("🔍 Scanning for available Gemini models...")
        
        for model_name in model_hierarchy:
            try:
                print(f"🔄 Testing: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Minimal test to avoid quota consumption
                test_response = model.generate_content(
                    "Respond with just 'OK'", 
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=5,
                        temperature=0.1
                    )
                )
                
                if hasattr(test_response, 'text') and test_response.text.strip():
                    print(f"🎉 SUCCESS: Connected to {model_name}")
                    
                    # Model capabilities mapping
                    capabilities = {
                        'gemini-2.0-flash-exp': "🚀 Gemini 2.0 Flash Experimental (Latest)",
                        'gemini-2.0-flash-thinking-exp': "🧠 Gemini 2.0 Flash Thinking Exp",
                        'gemini-1.5-flash-latest': "⚡ Gemini 1.5 Flash Latest",
                        'gemini-1.5-pro-latest': "🎯 Gemini 1.5 Pro Latest",
                        'gemini-1.5-flash': "⚡ Gemini 1.5 Flash",
                        'gemini-1.5-pro': "🎯 Gemini 1.5 Pro",
                        'gemini-1.0-pro': "🔹 Gemini 1.0 Pro",
                        'gemini-pro': "🔸 Gemini Pro"
                    }
                    
                    model_display = capabilities.get(model_name, model_name)
                    print(f"✅ Using: {model_display}")
                    return model
                    
            except Exception as e:
                error_msg = str(e)
                
                # Intelligent error handling
                if "quota" in error_msg.lower() or "429" in error_msg:
                    print(f"⏳ Quota limited for {model_name}, waiting 10s...")
                    time.sleep(10)
                elif "404" in error_msg or "not found" in error_msg:
                    print(f"❌ Model not available: {model_name}")
                elif "503" in error_msg or "unavailable" in error_msg:
                    print(f"🔧 Service unavailable: {model_name}")
                elif "403" in error_msg or "permission" in error_msg:
                    print(f"🔐 Access denied: {model_name}")
                else:
                    print(f"⚠️ {model_name} failed: {error_msg[:80]}...")
                continue
        
        # If all models fail, provide detailed guidance
        print("\n💡 **Troubleshooting Guide:**")
        print("1. Check API key at: https://aistudio.google.com/")
        print("2. Verify API is enabled for Gemini API")
        print("3. Check quota usage: https://aistudio.google.com/usage")
        print("4. Free tier resets hourly, paid tier has higher limits")
        print("5. Try again in 5-10 minutes for quota reset")
        
        return None
        
    except Exception as e:
        print(f"💥 Critical setup failure: {e}")
        return None

# Initialize the model
model = setup_gemini_advanced()

def get_gemini_advanced_analysis(prompt, context="", max_tokens=500):
    """Advanced analysis with optimized token usage"""
    if not model:
        return "❌ Advanced AI unavailable. Using enhanced analytical mode."
    
    try:
        # Optimized prompt construction
        full_prompt = f"""
        CONTEXT: {context}
        
        QUERY: {prompt}
        
        As an advanced financial AI, provide:
        1. Data-driven insights
        2. Actionable recommendations  
        3. Risk considerations
        4. Clear, concise analysis
        
        Focus on accuracy and practical value.
        """ if context else prompt
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
                top_p=0.8
            )
        )
        
        return response.text if hasattr(response, 'text') else "🤖 Advanced analysis completed."
        
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return "⏳ **AI Quota Limit**: Advanced features temporarily limited. Using enhanced analytical mode."
        elif "503" in error_msg:
            return "🔧 **AI Service Busy**: Advanced analysis unavailable. Using enhanced mode."
        else:
            return f"⚠️ Advanced analysis issue. Using enhanced mode."

def process_query(query, df, mode="rule"):
    """Process user query with advanced AI capabilities"""
    if mode == "rule":
        return get_advanced_rule_response(query, df)
    
    elif mode == "gemini":
        if not model:
            status_msg = """
❌ **Gemini Advanced Unavailable**

**Possible Reasons:**
• API quota limits exceeded (resets hourly)
• Model temporarily unavailable  
• Regional restrictions
• Network connectivity issues

**🎯 Recommended Actions:**
1. Use **Enhanced Rule-based Mode** (comprehensive analysis)
2. Try again in 5-10 minutes for quota reset
3. Check API key at: https://aistudio.google.com/

**💡 Enhanced Rule-based mode provides:**
• Complete portfolio analytics
• Sector performance insights  
• Stock prediction capabilities
• Professional investment analysis
"""
            return status_msg
        
        try:
            # Advanced portfolio context
            portfolio_context = generate_advanced_portfolio_context(df)
            
            analysis_prompt = f"""
            You are Gemini 2.0 Flash Experimental, an advanced AI financial analyst.

            PORTFOLIO CONTEXT:
            {portfolio_context}

            USER REQUEST: {query}

            Provide advanced analysis covering:
            • Performance metrics and trends
            • Risk assessment and opportunities
            • Data-driven recommendations
            • Strategic insights

            Be insightful, professional, and actionable.
            """
            
            return get_gemini_advanced_analysis(analysis_prompt)
            
        except Exception as e:
            return f"⚠️ Advanced analysis error: {str(e)[:100]}... Using enhanced analytical mode."

def generate_advanced_portfolio_context(df):
    """Generate comprehensive portfolio context for advanced AI"""
    try:
        total_inv, total_cur = calculate_total_investment(df)
        df_growth, overall_growth = calculate_growth(df)
        sector_data = sector_summary(df_growth)
        
        # Advanced metrics
        total_profit = total_cur - total_inv
        profit_percentage = (total_profit / total_inv) * 100 if total_inv > 0 else 0
        annualized_return = (overall_growth / 100) * (365/len(df)) * 100  # Simplified
        
        # Sector deep analysis
        sector_analysis = []
        for _, row in sector_data.iterrows():
            sector_profit = row['Current Value'] - row['Investment']
            sector_weight = (row['Investment'] / total_inv) * 100
            performance = "🚀" if row['Growth %'] > overall_growth else "📊" if row['Growth %'] > 0 else "⚠️"
            
            sector_analysis.append(
                f"{performance} {row['Sector']}: {row['Growth %']:.2f}% growth, "
                f"₹{sector_profit:,.2f} profit, {sector_weight:.1f}% weight"
            )
        
        # Risk assessment
        volatility_indicators = []
        if not sector_data.empty:
            growth_std = sector_data['Growth %'].std()
            if growth_std > 15:
                volatility_indicators.append("High sector volatility")
            elif growth_std > 8:
                volatility_indicators.append("Moderate sector volatility")
            else:
                volatility_indicators.append("Low sector volatility")
        
        context = f"""
🎯 **PORTFOLIO INTELLIGENCE REPORT**

📊 **Core Metrics:**
• Total Investment: ₹{total_inv:,.2f}
• Current Value: ₹{total_cur:,.2f}
• Total Profit: ₹{total_profit:,.2f}
• Overall Growth: {overall_growth:.2f}%
• Profit Percentage: {profit_percentage:.2f}%
• Estimated Annual Return: {annualized_return:.1f}%

🏢 **Sector Intelligence:**
{chr(10).join(sector_analysis)}

📈 **Portfolio Composition:**
• Total Holdings: {len(df)} assets
• Sector Diversity: {len(sector_data)} sectors
• Key Sectors: {', '.join(df['Sector'].unique())}

⚖️ **Risk Profile:**
• {', '.join(volatility_indicators)}
• Diversification: {'Good' if len(sector_data) >= 3 else 'Moderate' if len(sector_data) >= 2 else 'Concentrated'}
"""
        
        return context
        
    except Exception as e:
        return f"Basic portfolio metrics available. Advanced analytics limited: {str(e)}"

def get_advanced_rule_response(query, df):
    """Advanced rule-based responses with AI-like intelligence"""
    q = query.lower()
    
    try:
        total_inv, total_cur = calculate_total_investment(df)
        df_growth, overall_growth = calculate_growth(df)
        sector_data = sector_summary(df_growth)
        total_profit = total_cur - total_inv
        roi_percentage = (total_profit / total_inv) * 100 if total_inv > 0 else 0
        
        # Advanced analytics
        if not sector_data.empty:
            best_sector = sector_data.loc[sector_data['Growth %'].idxmax()]
            worst_sector = sector_data.loc[sector_data['Growth %'].idxmin()]
            avg_sector_growth = sector_data['Growth %'].mean()
            growth_volatility = sector_data['Growth %'].std()
        else:
            best_sector = worst_sector = None
            avg_sector_growth = growth_volatility = 0

        # Intelligent response mapping
        if any(word in q for word in ['hello', 'hi', 'hey', 'greetings']):
            model_status = "🚀 Gemini 2.0 Flash Experimental" if model else "⚡ Enhanced Analytical Engine"
            return f"""👋 **Welcome to Advanced Investment Intelligence!**

**Powered by:** {model_status}

I provide deep portfolio analytics, AI-powered stock predictions, and strategic investment insights.

**💼 My Capabilities:**
• Advanced portfolio performance analysis
• Sector intelligence and risk assessment
• Live stock predictions with ML models
• Strategic investment recommendations

**🎯 Try:** "Analyze my portfolio performance" or "Stock AAPL prediction\""""

        elif any(word in q for word in ['total investment', 'invested', 'capital']):
            return f"""💰 **Capital Deployment Analysis**

**Total Investment:** ₹{total_inv:,.2f}
**Portfolio Value:** ₹{total_cur:,.2f}
**Net Gain/Loss:** ₹{total_profit:,.2f}

**📊 Performance Context:**
• This represents your initial capital across {len(df)} holdings
• Distributed across {len(sector_data)} sectors
• Current ROI: {roi_percentage:.2f}%"""

        elif any(word in q for word in ['current value', 'portfolio value', 'net worth']):
            return f"""📈 **Portfolio Valuation Report**

**Current Market Value:** ₹{total_cur:,.2f}
**Original Investment:** ₹{total_inv:,.2f}
**Total Profit:** ₹{total_profit:,.2f}

**🎯 Performance Metrics:**
• Overall Growth: {overall_growth:.2f}%
• Return on Investment: {roi_percentage:.2f}%
• Absolute Gain: ₹{total_profit:,.2f}

**💡 Insight:** Your portfolio has {'outperformed' if overall_growth > 0 else 'underperformed'} relative to your initial investment."""

        elif any(word in q for word in ['growth', 'performance', 'how is my portfolio']):
            performance_rating = "🚀 Excellent" if overall_growth > 20 else "📈 Good" if overall_growth > 10 else "📊 Moderate" if overall_growth > 0 else "⚠️ Needs Attention"
            
            response = f"""📊 **Portfolio Performance Intelligence**

**Overall Performance:** {performance_rating}
**Total Growth:** {overall_growth:.2f}%
**Absolute Profit:** ₹{total_profit:,.2f}
**ROI Percentage:** {roi_percentage:.2f}%

**🏆 Sector Leadership:**
"""
            if best_sector is not None:
                best_profit = best_sector['Current Value'] - best_sector['Investment']
                response += f"• **Top Performer:** {best_sector['Sector']} ({best_sector['Growth %']:.2f}%, ₹{best_profit:,.2f} profit)\n"
            
            if worst_sector is not None and worst_sector['Growth %'] < avg_sector_growth:
                response += f"• **Development Area:** {worst_sector['Sector']} ({worst_sector['Growth %']:.2f}%)\n"
            
            response += f"• **Sector Volatility:** {growth_volatility:.2f}% std dev"
            
            return response

        elif any(word in q for word in ['sector', 'sectors', 'sector performance']):
            if not sector_data.empty:
                sector_intel = []
                for _, row in sector_data.iterrows():
                    profit = row['Current Value'] - row['Investment']
                    weight = (row['Investment'] / total_inv) * 100
                    performance = "🟢" if row['Growth %'] > avg_sector_growth else "🟡" if row['Growth %'] > 0 else "🔴"
                    
                    sector_intel.append(f"{performance} **{row['Sector']}**\n   Growth: {row['Growth %']:.2f}% | Profit: ₹{profit:,.2f} | Weight: {weight:.1f}%")
                
                return f"""🏦 **Sector Intelligence Report**

**Sector Performance Analysis:**
{chr(10).join(sector_intel)}

**📈 Sector Metrics:**
• Average Sector Growth: {avg_sector_growth:.2f}%
• Performance Range: {sector_data['Growth %'].min():.2f}% to {sector_data['Growth %'].max():.2f}%
• Volatility: {growth_volatility:.2f}% standard deviation"""
            return "❌ No sector data available for analysis."

        elif any(word in q for word in ['help', 'what can you do', 'features']):
            return """🆘 **Advanced Investment Intelligence Platform**

**🚀 CORE CAPABILITIES:**

**📊 Portfolio Analytics Suite**
• Complete performance intelligence
• Sector-wise deep analytics
• Risk assessment & volatility metrics
• Profit/Loss optimization insights

**🔮 Stock Prediction Engine**
• Live price predictions (type 'Stock SYMBOL')
• Machine learning models
• Technical analysis & trend identification
• Global market coverage (US, India, UK, Canada)

**🧠 AI-Powered Insights** (When Available)
• Gemini 2.0 Flash Experimental analysis
• Strategic investment recommendations
• Market trend intelligence
• Risk-adjusted return optimization

**💼 Investment Intelligence**
• Portfolio composition analysis
• Sector allocation optimization
• Performance benchmarking
• Strategic rebalancing suggestions

**🎯 QUICK START EXAMPLES:**
• "Analyze my complete portfolio performance"
• "Stock AAPL prediction with analysis"
• "Sector performance deep dive"
• "Portfolio risk assessment"
• "Investment optimization suggestions\""""

        elif any(word in q for word in ['stock', 'predict', 'forecast', 'analyze stock']):
            # Extract stock symbol for direct analysis
            words = query.upper().split()
            for i, word in enumerate(words):
                if word == 'STOCK' and i + 1 < len(words):
                    ticker = words[i + 1]
                    return f"""🔮 **Stock Analysis Request: {ticker}**

**🎯 Recommended Approach:**
1. Use the **Stock Predictions** section above for:
   • Live price predictions with ML models
   • Interactive charts and technical indicators
   • Comprehensive risk analysis
   • Investment recommendations

2. Or type **'Stock {ticker}'** in chat for quick analysis

**🌍 Global Market Access:**
• US: AAPL, TSLA, GOOGL
• India: TCS.NS, INFY.NS, RELIANCE.NS
• UK: HSBA.L, BP.L
• Canada: RY.TO, TD.TO"""

            return """🔮 **Advanced Stock Prediction System**

**To access stock predictions:**

**📈 Stock Prediction Dashboard** (Recommended):
1. Navigate to **Stock Predictions** section above
2. Enter any global stock symbol
3. Click 'Get Prediction' for full analysis

**💬 Quick Analysis:**
Type: **'Stock SYMBOL'** (e.g., 'Stock AAPL', 'Stock TCS.NS')

**🎯 System Features:**
• Machine Learning price predictions
• Technical analysis with multiple indicators
• Risk assessment and trend identification
• Global market coverage (US, India, UK, Canada, Europe)

**💡 Example Symbols:**
• US: AAPL, TSLA, MSFT, AMZN
• India: TCS.NS, INFY.NS, RELIANCE.NS
• UK: HSBA.L, BP.L, VOD.L
• Canada: RY.TO, TD.TO, SHOP.TO"""

        elif any(word in q for word in ['thank', 'thanks']):
            return "🎉 You're welcome! I'm here to provide advanced investment intelligence and help you make data-driven decisions. Feel free to ask for portfolio analysis, stock predictions, or investment insights!"

        elif any(word in q for word in ['risk', 'volatility', 'safe']):
            risk_level = "High" if growth_volatility > 15 else "Medium" if growth_volatility > 8 else "Low"
            return f"""⚖️ **Portfolio Risk Assessment**

**Risk Level:** {risk_level}
**Volatility Metric:** {growth_volatility:.2f}% standard deviation
**Diversification:** {len(sector_data)} sectors

**📊 Risk Indicators:**
• Sector concentration: {'High' if len(sector_data) < 3 else 'Adequate'}
• Performance consistency: {'Volatile' if growth_volatility > 10 else 'Stable'}
• Growth sustainability: {'Strong' if overall_growth > 15 else 'Moderate'}

**💡 Recommendation:** {'Consider diversifying across more sectors' if len(sector_data) < 3 else 'Current diversification appears adequate'}"""

        else:
            return """🤔 **Advanced Investment Intelligence**

I can provide deep analytical insights into your investments. Try:

**📊 Portfolio Analytics:**
• "Complete portfolio performance analysis"
• "Sector performance deep dive"
• "Risk assessment and volatility metrics"
• "Investment return optimization"

**🔮 Stock Predictions:**
• "Stock AAPL prediction and analysis"
• "Technical analysis for TCS.NS"
• "Market trend identification"

**💼 Investment Intelligence:**
• "Portfolio composition breakdown"
• "Sector allocation optimization"
• "Performance benchmarking"

Or type **'help'** for full capabilities list."""
            
    except Exception as e:
        return f"❌ Analytical engine error: {str(e)}\n\nPlease try rephrasing your query or use simpler terms."

def get_ai_response(user_input):
    """Advanced AI response with optimized performance"""
    if not model:
        return "❌ Advanced AI currently unavailable. Using enhanced analytical engine for comprehensive investment insights."
    
    try:
        optimized_prompt = f"""
        As an advanced AI assistant, provide a helpful, insightful response to:

        USER: {user_input}

        Focus on being accurate, helpful, and providing practical value.
        Keep response concise and actionable.
        """
        
        return get_gemini_advanced_analysis(optimized_prompt, max_tokens=300)
    except Exception as e:
        return f"⚠️ Advanced AI response unavailable: {str(e)[:80]}... Using enhanced analytical mode."

def get_stock_analysis_gemini(ticker, prediction_result, recent_data):
    """Advanced stock analysis using latest AI capabilities"""
    if not model:
        # Fallback to enhanced analytical engine
        return get_enhanced_stock_analysis(ticker, prediction_result, recent_data)
    
    try:
        if isinstance(prediction_result, dict):
            # Advanced analysis context
            analysis_context = create_advanced_stock_context(ticker, prediction_result, recent_data)
            
            advanced_prompt = f"""
            Provide advanced stock analysis and investment intelligence:

            {analysis_context}

            Deliver professional analysis covering:
            1. Technical assessment and trend outlook
            2. Risk-reward evaluation
            3. Strategic investment recommendation
            4. Key monitoring indicators

            Be data-driven, professional, and actionable.
            """
            
            return get_gemini_advanced_analysis(advanced_prompt)
        else:
            diagnostic_prompt = f"""
            User requested analysis for {ticker} but encountered: {prediction_result}

            Provide helpful guidance and alternative approaches.
            """
            return get_gemini_advanced_analysis(diagnostic_prompt)
            
    except Exception as e:
        return get_enhanced_stock_analysis(ticker, prediction_result, recent_data)

def create_advanced_stock_context(ticker, prediction_result, recent_data):
    """Create advanced context for stock analysis"""
    if not isinstance(prediction_result, dict):
        return f"Analysis request for {ticker}. Issue: {prediction_result}"
    
    # Advanced context construction
    context = f"""
🎯 **STOCK ANALYSIS: {ticker}**

📊 **PREDICTION INTELLIGENCE:**
• Current Price: ${prediction_result['current_price']:,.2f}
• Predicted Price: ${prediction_result['predicted_price']:,.2f}
• Price Trend: {prediction_result['trend']}
• Expected Change: {prediction_result['change_percent']}%
• Price Difference: ${prediction_result.get('price_difference', 0):,.2f}
• Model Confidence: {prediction_result['model_accuracy']}%
• Volume Pattern: {prediction_result.get('volume_trend', 'Standard')}
• Company: {prediction_result.get('company_name', ticker)}
• Sector: {prediction_result.get('sector', 'Not specified')}
"""
    
    # Add technical context if available
    if not recent_data.empty and len(recent_data) > 5:
        recent_change = ((recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[-5]) / recent_data['Close'].iloc[-5]) * 100
        volatility = recent_data['Close'].pct_change().std() * 100
        
        context += f"""
📈 **TECHNICAL CONTEXT:**
• 5-Day Performance: {recent_change:.2f}%
• Price Volatility: {volatility:.2f}%
• Recent High: ${recent_data['High'].max():.2f}
• Recent Low: ${recent_data['Low'].min():.2f}
• Analysis Period: {len(recent_data)} trading days
"""
    
    return context

def get_enhanced_stock_analysis(ticker, prediction_result, recent_data):
    """Enhanced analytical engine for stock analysis"""
    if not isinstance(prediction_result, dict):
        return f"""🔍 **Analysis for {ticker}**

❌ **Prediction Unavailable:** {prediction_result}

**💡 Troubleshooting:**
• Verify stock symbol format (e.g., AAPL, TCS.NS, HSBA.L)
• Check internet connection
• Ensure symbol is traded on supported exchanges
• Try again in a few moments"""

    # Advanced analysis without AI
    trend_emoji = "📈" if "Bullish" in prediction_result['trend'] else "📉"
    action_verb = "consider accumulating" if "Bullish" in prediction_result['trend'] else "exercise caution with"
    confidence_level = "High" if prediction_result['model_accuracy'] > 85 else "Medium-High" if prediction_result['model_accuracy'] > 70 else "Medium" if prediction_result['model_accuracy'] > 60 else "Low"
    
    # Risk assessment
    risk_level = "Low" if abs(prediction_result['change_percent']) < 3 else "Medium" if abs(prediction_result['change_percent']) < 8 else "High"
    
    analysis = f"""
{trend_emoji} **ADVANCED STOCK ANALYSIS: {ticker}**

📊 **PREDICTION SUMMARY**
• **Trend Direction**: {prediction_result['trend']}
• **Expected Change**: {prediction_result['change_percent']}%
• **Current Price**: ${prediction_result['current_price']:,.2f}
• **Predicted Price**: ${prediction_result['predicted_price']:,.2f}
• **Price Movement**: ${prediction_result.get('price_difference', 0):,.2f}
• **Model Confidence**: {prediction_result['model_accuracy']}% ({confidence_level})
• **Risk Assessment**: {risk_level}

🎯 **INVESTMENT RECOMMENDATION**
Based on the {prediction_result['trend'].lower()} trend and {confidence_level.lower()} confidence, 
you may want to **{action_verb}** this stock.

🔍 **TECHNICAL INSIGHTS**
• Analysis based on {prediction_result['data_points']} trading sessions
• Volume pattern: {prediction_result.get('volume_trend', 'Normal')}
• Market sector: {prediction_result.get('sector', 'Not specified')}
• Company: {prediction_result.get('company_name', ticker)}

⚠️ **DISCLAIMER**
Predictions utilize machine learning models on historical data. 
Always conduct thorough research and consider professional advice before investing.
"""
    
    return analysis.strip()

def handle_stock_query(query, df):
    """Advanced stock query handling"""
    q = query.lower()
    
    if 'stock' in q or 'predict' in q or 'analyze' in q:
        # Extract ticker for direct analysis
        words = query.upper().split()
        for i, word in enumerate(words):
            if word == 'STOCK' and i + 1 < len(words):
                ticker = words[i + 1]
                return f"""🔮 **Stock Analysis: {ticker}**

**🎯 For Comprehensive Analysis:**
Use the **Stock Predictions** dashboard above for:
• Live ML-powered price predictions
• Interactive technical charts
• Advanced risk assessment
• Detailed investment recommendations

**💬 Quick Analysis:**
Type **'Stock {ticker}'** in chat

**🚀 System Features:**
• Advanced machine learning models
• Global market coverage
• Technical indicator analysis
• Professional investment insights"""

        return """🔮 **Advanced Stock Prediction System**

**ACCESS METHODS:**

**📈 Dashboard (Recommended):**
1. Navigate to **Stock Predictions** section
2. Enter any global stock symbol
3. Click 'Get Prediction' for full analysis

**💬 Quick Chat Analysis:**
Type: **'Stock SYMBOL'** (e.g., 'Stock AAPL')

**🌍 Global Market Coverage:**
• **US Markets**: AAPL, TSLA, GOOGL, MSFT, AMZN
• **Indian Markets**: TCS.NS, INFY.NS, RELIANCE.NS, HDFCBANK.NS
• **UK Markets**: HSBA.L, BP.L, VOD.L, GSK.L
• **Canadian Markets**: RY.TO, TD.TO, SHOP.TO
• **European Markets**: ASML.AS, SAP.DE

**🎯 Advanced Features:**
• Machine Learning price forecasting
• Technical analysis with multiple indicators
• Risk assessment and volatility metrics
• Professional investment recommendations"""
    
    return None