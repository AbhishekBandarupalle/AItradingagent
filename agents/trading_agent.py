# Standard library imports
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

# Third-party imports
import matplotlib.pyplot as plt
import requests
import yfinance as yf

# Local imports
# Add project root to Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import MCPClient, clean_llm_json, FinBertSentiment

# Configure logging: log to both console and file, rotate daily, keep 7 days
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

import os
log_dir = 'logging'
os.makedirs(log_dir, exist_ok=True)
file_handler = TimedRotatingFileHandler(os.path.join(log_dir, 'trading_agent.log'), when='midnight', backupCount=7, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class SmartM1TradingAgent:
    def __init__(self, api_key=None, max_investment=10000, llm_url="http://localhost:11534", newsapi_key=None):
        self.api_key = api_key  # Not used in simulation mode
        self.max_investment = max_investment
        self.portfolio = {}
        self.last_rebalance = datetime.min
        self.trade_log = []
        self.mcp = MCPClient(llm_url)
        self.newsapi_key = newsapi_key
        self.finbert = FinBertSentiment()
        
        # Get current transaction ID first (needed for auto-initialization)
        self.transaction_id = self._get_last_transaction_id()
        
        # Auto-initialize if needed
        self._auto_initialize_if_needed()
        
        # Get current state after potential initialization
        self.holdings = self._get_last_holdings()
        self.cash = self._get_last_cash()

    def _get_last_transaction_id(self):
        # Get the last transaction ID from the database via MCP
        result = self.mcp.get_last_transaction_id()
        if result['success']:
            return result['transaction_id']
        else:
            logging.error(f"Error getting last transaction ID: {result['error']}")
            return 0

    def _get_next_transaction_id(self):
        self.transaction_id += 1
        return f"{self.transaction_id:05d}"

    def query_llm(self, prompt):
        return self.mcp.send(prompt)

    def fetch_news_sentiment(self, symbol):
        if not self.newsapi_key:
            return "No API key", 1.0
        url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&language=en&apiKey={self.newsapi_key}"
        try:
            response = requests.get(url)
            articles = response.json().get("articles", [])
            headlines = [a["title"] for a in articles[:5]]
            if not headlines:
                return ["No headlines"], 1.0
            avg_scores = self.finbert.aggregate_score(headlines)
            # Use positive - negative as a custom sentiment score (range -1 to 1)
            sentiment_score = avg_scores['positive'] - avg_scores['negative']
            # Optionally scale/normalize to 0.5-1.5 for compatibility
            scaled_score = 1.0 + sentiment_score  # Range: 0.0 to 2.0
            scaled_score = max(0.5, min(scaled_score, 1.5))
            return headlines, scaled_score
        except Exception as e:
            logging.warning(f"Failed to fetch news for {symbol}: {e}")
            return ["Error fetching news"], 1.0

    def fetch_news_sentiment_batch(self, symbols):
        """Fetch news and sentiment for a list of symbols using a single NewsAPI request."""
        results = {}
        if not self.newsapi_key:
            return {s: (["No API key"], 1.0) for s in symbols}

        query = " OR ".join(symbols)
        url = (
            f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={self.newsapi_key}"
        )
        try:
            response = requests.get(url)
            articles = response.json().get("articles", [])
            symbol_map = {s: [] for s in symbols}
            for a in articles:
                title = a.get("title", "")
                for s in symbols:
                    if s.lower() in title.lower():
                        symbol_map[s].append(title)

            for s in symbols:
                headlines = symbol_map[s][:5]
                if headlines:
                    avg = self.finbert.aggregate_score(headlines)
                    score = avg["positive"] - avg["negative"]
                    scaled = max(0.5, min(1.0 + score, 1.5))
                    results[s] = (headlines, scaled)
                else:
                    results[s] = (["No headlines"], 1.0)
        except Exception as e:
            logging.warning(f"Failed batch news fetch: {e}")
            results = {s: (["Error fetching news"], 1.0) for s in symbols}
        return results

    def get_fund_holdings(self, fund):
        """Return a list of stock tickers held by the given fund."""
        try:
            ticker = yf.Ticker(fund)
            if hasattr(ticker, "fund_holdings"):
                df = ticker.fund_holdings
                if hasattr(df, "symbol"):
                    return list(df["symbol"])
                return list(df.index)
            info = getattr(ticker, "info", {})
            return [h.get("symbol") for h in info.get("holdings", []) if h.get("symbol")]
        except Exception as e:
            logging.warning(f"Failed to get holdings for {fund}: {e}")
            return []

    def get_top_movers(self, funds):
        """Return top 10 positive and top 10 negative movers from the given funds."""
        all_stocks = set()
        for f in funds:
            all_stocks.update(self.get_fund_holdings(f))

        movers = []
        for s in all_stocks:
            try:
                hist = yf.Ticker(s).history(period="11d")
                closes = hist["Close"]
                if len(closes) < 2:
                    continue
                pct = (closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]
                movers.append((s, pct))
            except Exception as e:
                logging.warning(f"Failed to fetch history for {s}: {e}")

        movers.sort(key=lambda x: x[1], reverse=True)
        top_positive = [s for s, _ in movers[:10]]
        top_negative = [s for s, _ in sorted(movers, key=lambda x: x[1])[:10]]
        return top_positive, top_negative

    def generate_portfolio_with_llm(self):
        """Generate a portfolio using LLM guidance combined with market data."""
        # Step 1: Ask the LLM for index funds to analyze
        prompt = (
            "List major index funds or ETFs to analyze. "
            "Respond ONLY with JSON like {\"funds\": [\"SPY\", \"QQQ\"]}."
        )
        symbol_response = self.query_llm(prompt)
        logging.info(f"LLM fund response: {symbol_response}")
        try:
            cleaned = clean_llm_json(symbol_response)
            fund_obj = json.loads(cleaned) if cleaned else json.loads(self.try_fix_llm_response(symbol_response))
            fund_list = fund_obj.get("funds", [])
        except Exception as e:
            logging.error(f"Failed to parse fund list: {e}")
            self.portfolio = {}
            return

        # Step 2: Determine top movers from these index funds
        pos, neg = self.get_top_movers(fund_list)
        stock_list = pos + neg

        # Step 3: Fetch news and sentiment in a single batch
        news_data = self.fetch_news_sentiment_batch(stock_list)
        news_digest = ""
        sentiment_map = {}
        for sym in stock_list:
            headlines, score = news_data.get(sym, (["No headlines"], 1.0))
            sentiment_map[sym] = score
            news_digest += f"\n[{sym}] Sentiment Score: {score:.2f}\n" + "\n".join(f"- {h}" for h in headlines) + "\n"

        logging.info(f"News Digest for LLM allocation:\n{news_digest}")

        # Step 4: Ask the LLM for allocation
        allocation_prompt = (
            "You are an expert portfolio manager. "
            "Based on the following news sentiment and recent movers, provide allocation weights. "
            "Respond ONLY with a JSON object where keys are tickers and values are decimals summing to 1.\n\n"
            f"{news_digest}"
        )
        result = self.query_llm(allocation_prompt)
        logging.info(f"Raw LLM allocation result: {result}")
        try:
            cleaned = clean_llm_json(result)
            portfolio = json.loads(cleaned)
            if isinstance(portfolio, dict):
                self.portfolio = {s: portfolio.get(s, 0) for s in stock_list if s in portfolio}
                self.current_sentiment = {s: sentiment_map[s] for s in self.portfolio}
                logging.info(f"LLM generated portfolio: {self.portfolio}")
            else:
                logging.warning("Invalid format returned from LLM.")
                self.portfolio = {}
        except Exception as e:
            logging.error(f"Error parsing LLM output: {e}")
            self.portfolio = {}

    @staticmethod
    def try_fix_llm_response(raw):
        import re
        s = raw.strip()
        # Try to convert ["DOGE-USD": 0.4, ...] to {"DOGE-USD": 0.4, ...}
        if s.startswith('[') and ':' in s:
            fixed = '{' + s[1:-1] + '}'
            fixed = re.sub(r'([a-zA-Z0-9_-]+):', r'"\1":', fixed)  # Add quotes to keys
            fixed = fixed.replace("'", '"')  # Replace single quotes with double quotes
            return fixed
        # Try to convert Python dict style to JSON
        if s.startswith('{') and ':' in s:
            fixed = re.sub(r'([a-zA-Z0-9_-]+):', r'"\1":', s)
            fixed = fixed.replace("'", '"')
            return fixed
        return s

    def _get_last_holdings(self):
        # Get last holdings from the database via MCP
        result = self.mcp.get_current_holdings()
        if result['success']:
            holdings = {}
            for symbol, data in result['holdings'].items():
                holdings[symbol] = data['shares']
            return holdings
        else:
            logging.error(f"Error getting holdings: {result['error']}")
            return {}

    def _get_last_cash(self):
        # Get last cash from the database via MCP
        result = self.mcp.get_current_holdings()
        if result['success']:
            cash = result['cash']
            return cash
        else:
            logging.error(f"Error getting cash: {result['error']}")
            return 0

    def _auto_initialize_if_needed(self):
        """Automatically initialize the trading system if it hasn't been initialized yet."""
        try:
            # Check if system is already initialized
            result = self.mcp.get_current_holdings()
            if result['success']:
                cash = result.get('cash', 0)
                holdings = result.get('holdings', {})
                
                # System is initialized if cash > 0 or there are holdings
                if cash > 0 or len(holdings) > 0:
                    logging.info("Trading system already initialized")
                    return
                else:
                    # System needs initialization
                    logging.info(f"First-time run detected! Initializing trading system with ${self.max_investment} starting cash")
                    self.initialize_trading_system()
            else:
                logging.warning(f"Could not check initialization status: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logging.warning(f"Could not check initialization status: {e}")
            # Don't fail the agent startup if initialization check fails

    def simulate_orders(self):
        logging.info("Simulating orders with buy/sell logic...")
        new_trades = []
        now = datetime.now()
        transaction_id = self._get_next_transaction_id()
        timestamp = now.strftime("%H:%M:%S")
        date = now.strftime("%d-%m-%y")
        prev_portfolio = self.portfolio.copy() if hasattr(self, 'portfolio') else {}
        prev_holdings = self.holdings.copy()
        prev_cash = self.cash
        # Fetch prices for all symbols in union of old and new allocations
        all_symbols = set(prev_holdings.keys()).union(set(self.portfolio.keys()))
        prices = {}
        for symbol in all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                prices[symbol] = ticker.info.get('regularMarketPrice')
            except Exception as e:
                logging.warning(f"Failed to fetch price for {symbol}: {e}")
                prices[symbol] = None
        # Process all symbols in union of old and new allocations
        cash = prev_cash
        for symbol in all_symbols:
            alloc = self.portfolio.get(symbol, 0)
            price = prices.get(symbol, None)
            target_amount = self.max_investment * alloc
            prev_shares = prev_holdings.get(symbol, 0)
            prev_alloc = prev_portfolio.get(symbol, 0)
            shares_held = prev_shares
            action = 'Hold'
            shares_changed = 0
            amount = 0
            # Sentiment-based buy/sell gating
            last_sent = getattr(self, 'last_sentiment', {}).get(symbol, 1.0)
            curr_sent = getattr(self, 'current_sentiment', {}).get(symbol, 1.0)
            drastic_change = abs(curr_sent - last_sent) > 0.3 or (last_sent >= 1.0 and curr_sent < 1.0) or (last_sent < 1.0 and curr_sent >= 1.0)
            if price and price > 0:
                target_shares = target_amount / price
                shares_changed = target_shares - prev_shares
                shares_held = target_shares
                amount = abs(shares_changed) * price
                if shares_changed > 0.0001:
                    if drastic_change or prev_shares == 0:
                        action = 'Buy'
                        max_affordable_shares = cash / price if price > 0 else 0
                        if shares_changed * price > cash:
                            shares_changed = max_affordable_shares
                            shares_held = prev_shares + shares_changed
                            amount = abs(shares_changed) * price
                            logging.warning(f"Attempted to buy more {symbol} than cash allows. Adjusted purchase to available cash.")
                        cash -= amount
                        if cash < 0:
                            logging.warning(f"Cash went negative after buying {symbol}. Setting cash to 0.")
                            cash = 0
                    else:
                        action = 'Hold'
                        shares_changed = 0
                elif shares_changed < -0.0001:
                    if drastic_change:
                        action = 'Sell'
                        cash += amount
                    else:
                        action = 'Hold'
                        shares_changed = 0
                else:
                    action = 'Hold'
            elif alloc == 0 and prev_shares > 0:
                if drastic_change:
                    action = 'Sell'
                    shares_changed = -prev_shares
                    shares_held = 0
                    amount = abs(shares_changed) * (price if price else 0)
                    cash += amount
                else:
                    action = 'Hold'
                    shares_changed = 0
            self.holdings[symbol] = shares_held
            if action != 'Hold' or alloc > 0:
                trade = {
                    "transaction_id": transaction_id,
                    "time": timestamp,
                    "date": date,
                    "symbol": symbol,
                    "action": action,
                    "shares_changed": shares_changed,
                    "shares_held": shares_held,
                    "current_price": price,
                    "amount": amount,
                    "allocation": alloc,
                    "cash": cash,
                    "sentiment": getattr(self, 'current_sentiment', {}).get(symbol, 1.0),
                    "last_sentiment": getattr(self, 'last_sentiment', {}).get(symbol, 1.0)
                }
                self.trade_log.append(trade)
                new_trades.append(trade)
                logging.info(f"{action} {abs(shares_changed):.4f} shares of {symbol} @ ${price if price is not None else 'N/A'} (now holding {shares_held:.4f}), cash: ${cash:.2f}")
        portfolio_value = cash
        for symbol, shares in self.holdings.items():
            price = prices.get(symbol, None)
            if price and price > 0:
                portfolio_value += shares * price
        for trade in new_trades:
            trade['portfolio_value'] = portfolio_value
            trade['final_cash'] = cash
        self.cash = cash
        self.last_sentiment = getattr(self, 'current_sentiment', {})
        self._log_trades_to_json(new_trades)
        self.publish_trades_to_mcp()

    def publish_trades_to_mcp(self):
        if self.trade_log:
            result = self.mcp.save_trades(self.trade_log)
            if result['success']:
                logging.info(f"Saved {result['inserted_count']} trades to database")
            else:
                logging.error(f"Error saving trades: {result['error']}")

    def _log_trades_to_json(self, new_trades):
        # Save trades to database via MCP server
        if new_trades:
            result = self.mcp.save_trades(new_trades)
            if result['success']:
                logging.info(f"Saved {result['inserted_count']} trades to database")
            else:
                logging.error(f"Error saving trades: {result['error']}")

    def initialize_trading_system(self):
        """Initialize the trading system with starting cash and clear previous trades."""
        logging.info(f"Initializing trading system with ${self.max_investment} starting cash")
        
        # Create initial trade record with starting cash
        now = datetime.now()
        transaction_id = self._get_next_transaction_id()
        initial_trade = {
            "transaction_id": transaction_id,
            "time": now.strftime("%H:%M:%S"),
            "date": now.strftime("%d-%m-%y"),
            "symbol": "CASH_INIT",
            "action": "Initialize",
            "shares_changed": 0,
            "shares_held": 0,
            "current_price": 1.0,
            "amount": self.max_investment,
            "allocation": 0,
            "cash": self.max_investment,
            "final_cash": self.max_investment,
            "portfolio_value": self.max_investment,
            "sentiment": 1.0,
            "last_sentiment": 1.0
        }
        
        # Save to database
        result = self.mcp.save_trades([initial_trade])
        if result['success']:
            logging.info("Trading system initialized successfully")
            self.cash = self.max_investment
            self.holdings = {}
        else:
            logging.error(f"Failed to initialize trading system: {result['error']}")
    
    def should_rebalance(self):
        return (datetime.now() - self.last_rebalance) >= timedelta(days=1)

    def run(self, simulate=True):
        if self.should_rebalance():
            self.generate_portfolio_with_llm()
            if self.portfolio:
                if simulate:
                    self.simulate_orders()
                else:
                    self.rebalance_portfolio()
                self.last_rebalance = datetime.now()
            else:
                logging.warning("No portfolio generated.")
        else:
            logging.info("No rebalance needed today.")

    def run_continuous(self, simulate=True, interval_minutes=10):
        logging.info("Starting continuous trading agent loop.")
        try:
            while True:
                self.generate_portfolio_with_llm()
                if self.portfolio:
                    if simulate:
                        self.simulate_orders()
                    else:
                        self.rebalance_portfolio()
                    self.last_rebalance = datetime.now()
                else:
                    logging.warning("No portfolio generated.")
                logging.info(f"Sleeping for {interval_minutes} minutes before next update.")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            logging.info("Continuous trading agent loop stopped by user.")

if __name__ == "__main__":
    api_key = "YOUR_M1_API_KEY"
    agent = SmartM1TradingAgent(api_key, llm_url="http://localhost:11534", newsapi_key="af484810771a4d8692a2db9b4672288e")
    agent.run_continuous(simulate=True, interval_minutes=2)