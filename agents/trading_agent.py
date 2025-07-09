import requests
import time
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import re
import yfinance as yf
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.mcp_client import MCPClient
from utils.trade_log_utils import load_trade_log, save_trade_log

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
    def __init__(self, api_key=None, max_investment=1000, llm_url="http://localhost:11534/mcp"):
        self.api_key = api_key  # Not used in simulation mode
        self.max_investment = max_investment
        self.portfolio = {}
        self.last_rebalance = datetime.min
        self.trade_log = []
        self.mcp = MCPClient(llm_url)
        self.transaction_id = self._get_last_transaction_id()
        self.holdings = self._get_last_holdings()
        self.cash = self._get_last_cash()

    def _get_last_transaction_id(self):
        # Read the last transaction ID from the JSON log file
        log_data = load_trade_log()
        trades = log_data["trades"]
        if trades:
            last_id = trades[-1].get('transaction_id', '00000')
            return int(last_id)
        return 0

    def _get_next_transaction_id(self):
        self.transaction_id += 1
        return f"{self.transaction_id:05d}"

    def query_llm(self, prompt):
        return self.mcp.send(prompt)

    def generate_portfolio_with_llm(self):
        prompt = (
            "You are an expert in financial matters including Stocks, Options, and Crypto trading. "
            "Your goal is to aggressively maximize short-term profitability. "
            "Fetch or infer current market sentiment, news, technical trends, and volatility insights. "
            "Prioritize opportunities with high momentum and explosive upside potential. "
            "Focus especially on low-cap or trending cryptocurrencies that are likely to 'blow up' in the short term. "
            "Evaluate the best assets (stocks, options, or crypto) to buy right now for strong returns within the next few days. "
            "Reply ONLY with a JSON object like: {\"AAPL\": 0.4, \"DOGE-USD\": 0.3, \"TSLA\": 0.3} representing recommended allocation ratios. "
            "Avoid explanations or disclaimers."
        )
        result = self.query_llm(prompt)
        logging.info(f"Raw LLM result: {result}")
        try:
            # Try to extract JSON object from the result string
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                json_str = match.group(0)
                portfolio = json.loads(json_str)
                if isinstance(portfolio, dict):
                    self.portfolio = portfolio
                    logging.info(f"LLM generated portfolio: {self.portfolio}")
                else:
                    logging.warning("Invalid format returned from LLM.")
            else:
                raise ValueError("No JSON object found in LLM output")
        except Exception as e:
            logging.error(f"Error parsing LLM output: {e}")
            self.portfolio = {}

    def _get_last_holdings(self):
        # Read last holdings from the JSON log file
        holdings = {}
        log_data = load_trade_log()
        trades = log_data["trades"]
        if trades:
            last_tid = trades[-1]['transaction_id']
            last_trades = [t for t in trades if t['transaction_id'] == last_tid]
            for t in last_trades:
                holdings[t['symbol']] = t.get('shares_held', 0)
        return holdings

    def _get_last_cash(self):
        # Read last cash from the JSON log file
        log_data = load_trade_log()
        trades = log_data["trades"]
        if trades:
            last_tid = trades[-1]['transaction_id']
            last_trades = [t for t in trades if t['transaction_id'] == last_tid]
            return last_trades[0].get('cash', self.max_investment)
        return self.max_investment

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
        all_symbols = set(prev_holdings.keys()).union(self.portfolio.keys())
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
            if price and price > 0:
                target_shares = target_amount / price
                shares_changed = target_shares - prev_shares
                shares_held = target_shares
                amount = abs(shares_changed) * price
                if shares_changed > 0.0001:
                    action = 'Buy'
                    cash -= amount
                elif shares_changed < -0.0001:
                    action = 'Sell'
                    cash += amount
                else:
                    action = 'Hold'
            elif alloc == 0 and prev_shares > 0:
                # Sell all if allocation is now zero
                action = 'Sell'
                shares_changed = -prev_shares
                shares_held = 0
                amount = abs(shares_changed) * (price if price else 0)
                cash += amount
            # Update holdings
            self.holdings[symbol] = shares_held
            # Only log if action is not Hold or if it's a new allocation
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
                    "cash": cash  # cash after this trade
                }
                self.trade_log.append(trade)
                new_trades.append(trade)
                logging.info(f"{action} {abs(shares_changed):.4f} shares of {symbol} @ ${price if price is not None else 'N/A'} (now holding {shares_held:.4f}), cash: ${cash:.2f}")
        # After all trades, compute portfolio value
        portfolio_value = cash
        for symbol, shares in self.holdings.items():
            price = prices.get(symbol, None)
            if price and price > 0:
                portfolio_value += shares * price
        # Add portfolio_value and final cash to all trades in this transaction
        for trade in new_trades:
            trade['portfolio_value'] = portfolio_value
            trade['final_cash'] = cash
        self.cash = cash
        self._log_trades_to_json(new_trades)
        self.publish_trades_to_mcp()

    def publish_trades_to_mcp(self):
        if self.trade_log:
            result = self.mcp.record_trades(self.trade_log)
            logging.info(f"Posted trades to MCP: {result}")

    def _log_trades_to_json(self, new_trades):
        # Unified log structure: {"new_trade": true/false, "trades": [...]}
        log_data = load_trade_log()
        # Append new trades
        log_data["trades"].extend(new_trades)
        # Set new_trade flag if any buy/sell
        if any(trade['action'] in ('Buy', 'Sell') for trade in new_trades):
            log_data["new_trade"] = True
        save_trade_log(log_data)
        logging.info(f"Trade log saved to {os.environ.get('TRADE_LOG_JSON', 'trade_log.json')}")

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
    agent = SmartM1TradingAgent(api_key, llm_url="http://localhost:11534/mcp")
    agent.run_continuous(simulate=True, interval_minutes=2)