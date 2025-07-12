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

    def generate_portfolio_with_llm(self):
        # Step 1: Ask LLM for recommended stocks and cryptos
        symbol_prompt = (
            "You are a financial strategist. List 20 promising stocks and 5 promising cryptos "
            "to consider for short-term aggressive trading, based on market momentum and trends. "
            "Respond ONLY with a valid JSON object of the form: {\"stocks\": [\"TSLA\", ...], \"cryptos\": [\"BTC-USD\", ...]}. "
            "Do not include any explanation or extra text. Use curly braces, double quotes for keys and values, and valid JSON syntax only."
        )
        symbol_response = self.query_llm(symbol_prompt)
        logging.info(f"LLM symbol response: {symbol_response}")
        try:
            cleaned = clean_llm_json(symbol_response)
            if not cleaned:
                # Try to fix common LLM mistakes
                fixed = self.try_fix_llm_response(symbol_response)
                try:
                    symbol_obj = json.loads(fixed)
                except Exception:
                    logging.error(f"Failed to parse LLM response even after fix: {symbol_response}")
                    self.portfolio = {}
                    return
            else:
                symbol_obj = json.loads(cleaned)
            stock_list = symbol_obj.get("stocks", [])
            crypto_list = symbol_obj.get("cryptos", [])
            if not isinstance(stock_list, list) or not isinstance(crypto_list, list):
                raise ValueError("'stocks' or 'cryptos' key is not a list")
        except Exception as e:
            logging.error(f"Failed to parse symbol list from LLM: {e}")
            logging.error(f"Raw LLM response (exception): {symbol_response}")
            self.portfolio = {}
            return

        # Step 2: Build news digest and filter by sentiment (more lenient threshold)
        news_digest = ""
        filtered_stocks = []
        filtered_cryptos = []
        sentiment_map = {}
        for symbol in stock_list:
            headlines, score = self.fetch_news_sentiment(symbol)
            sentiment_map[symbol] = score
            # More lenient sentiment threshold (0.5 instead of 0.8)
            if score >= 0.5:
                filtered_stocks.append(symbol)
                news_digest += f"\n[{symbol}] Sentiment Score: {score:.2f}\n" + "\n".join(f"- {h}" for h in headlines) + "\n"
            else:
                logging.info(f"Filtered out {symbol} due to low sentiment: {score:.2f}")
        for symbol in crypto_list:
            headlines, score = self.fetch_news_sentiment(symbol)
            sentiment_map[symbol] = score
            # More lenient sentiment threshold (0.5 instead of 0.8)
            if score >= 0.5:
                filtered_cryptos.append(symbol)
                news_digest += f"\n[{symbol}] Sentiment Score: {score:.2f}\n" + "\n".join(f"- {h}" for h in headlines) + "\n"
            else:
                logging.info(f"Filtered out {symbol} due to low sentiment: {score:.2f}")
        
        logging.info(f"Filtered stocks: {filtered_stocks}")
        logging.info(f"Filtered cryptos: {filtered_cryptos}")
        logging.info(f"News Digest for LLM allocation:\n{news_digest}")

        # Step 3: Ask LLM for allocations using the news context (filtered symbols only)
        allocation_prompt = (
            "You are an expert in financial markets: stocks, crypto, and options. "
            "Your task is to aggressively optimize for short-term profitability. "
            "Use the news headlines and sentiment scores provided to find high-momentum or undervalued opportunities. "
            "Prioritize crypto that may explode, and stocks with bullish trends or major events. "
            "Reply ONLY with a JSON object of allocation ratios (0 to 1 sum): "
            "{\"TSLA\": 0.3, \"DOGE-USD\": 0.4, \"NVDA\": 0.3}.\n\n"
            "News and sentiment context:\n"
            f"{news_digest}"
        )
        result = self.query_llm(allocation_prompt)
        logging.info(f"Raw LLM result: {result}")
        try:
            cleaned = clean_llm_json(result)
            if not cleaned:
                raise ValueError("No JSON object found in LLM output")
            portfolio = json.loads(cleaned)
            if isinstance(portfolio, dict):
                # Step 4: Enforce 80/20 allocation between stocks and cryptos
                stock_syms = [s for s in filtered_stocks if s in portfolio]
                crypto_syms = [s for s in filtered_cryptos if s in portfolio]
                stock_alloc = sum(portfolio[s] for s in stock_syms)
                crypto_alloc = sum(portfolio[s] for s in crypto_syms)
                # Normalize allocations
                total = stock_alloc + crypto_alloc
                if total == 0:
                    self.portfolio = {}
                    logging.warning("No valid allocations after filtering.")
                    return
                # Scale to 80/20
                for s in stock_syms:
                    portfolio[s] = 0.8 * (portfolio[s] / stock_alloc) if stock_alloc > 0 else 0
                for s in crypto_syms:
                    portfolio[s] = 0.2 * (portfolio[s] / crypto_alloc) if crypto_alloc > 0 else 0
                # Remove any not in filtered lists
                self.portfolio = {s: portfolio[s] for s in stock_syms + crypto_syms}
                logging.info(f"LLM generated portfolio (80/20): {self.portfolio}")
                self.last_sentiment = getattr(self, 'last_sentiment', {})
                self.current_sentiment = {s: sentiment_map[s] for s in self.portfolio}
            else:
                logging.warning("Invalid format returned from LLM.")
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
        # self._log_trades_to_json(new_trades)
        self.publish_trades_to_mcp(new_trades)

    def publish_trades_to_mcp(self, trades):
        """Send the provided trades to the MCP server for persistence."""
        if not trades:
            return

        result = self.mcp.save_trades(trades)
        if result['success']:
            logging.info(f"Saved {result['inserted_count']} trades to database")
        else:
            logging.error(f"Error saving trades: {result['error']}")

    # def _log_trades_to_json(self, new_trades):
    #     # Save trades to database via MCP server
    #     if new_trades:
    #         result = self.mcp.save_trades(new_trades)
    #         if result['success']:
    #             logging.info(f"Saved {result['inserted_count']} trades to database")
    #         else:
    #             logging.error(f"Error saving trades: {result['error']}")

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

    def rebalance_portfolio(self):
        """Rebalance the portfolio with actual trading (not simulation)."""
        logging.info("Rebalancing portfolio with actual trading...")
        # For now, this is a placeholder for actual trading implementation
        # In a real implementation, this would place actual orders
        self.simulate_orders()  # Use simulation for now
        logging.info("Portfolio rebalancing completed")

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
    newsapi_key = os.environ.get('NEWSAPI_KEY')
    agent = SmartM1TradingAgent(api_key, llm_url="http://localhost:11534", newsapi_key=newsapi_key)
    agent.run_continuous(simulate=True, interval_minutes=10)