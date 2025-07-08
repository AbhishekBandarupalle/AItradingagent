import requests
import time
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mcp_client import MCPClient
import logging
from logging.handlers import TimedRotatingFileHandler

# Configure logging: log to both console and file, rotate daily, keep 7 days
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler with daily rotation
file_handler = TimedRotatingFileHandler('trading_agent.log', when='midnight', backupCount=7, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class SmartM1TradingAgent:
    def __init__(self, api_key, max_investment=1000, llm_url="http://localhost:11434/mcp"):
        self.api_key = api_key
        self.max_investment = max_investment
        self.portfolio = {}
        self.last_rebalance = datetime.min
        self.trade_log = []
        self.mcp = MCPClient(llm_url)

    def query_llm(self, prompt):
        return self.mcp.send(prompt)

    def generate_portfolio_with_llm(self):
        prompt = (
            "You are a financial trading assistant. Based on current market trends and economic news, "
            "suggest a portfolio allocation for a $1000 investment. "
            "Respond only in JSON format like: {\"AAPL\": 0.5, \"MSFT\": 0.5}"
        )
        result = self.query_llm(prompt)
        try:
            portfolio = json.loads(result)
            if isinstance(portfolio, dict):
                self.portfolio = portfolio
                logging.info(f"LLM generated portfolio: {self.portfolio}")
            else:
                logging.warning("Invalid format returned from LLM.")
        except Exception as e:
            logging.error(f"Error parsing LLM output: {e}")
            self.portfolio = {}

    def simulate_orders(self):
        logging.info("Simulating orders...")
        for symbol, allocation in self.portfolio.items():
            invest_amount = self.max_investment * allocation
            trade = {
                "time": datetime.now().isoformat(),
                "symbol": symbol,
                "amount": invest_amount
            }
            self.trade_log.append(trade)
            logging.info(f"Simulated order: {symbol} - ${invest_amount:.2f}")
        self.publish_trades_to_mcp()

    def publish_trades_to_mcp(self):
        if self.trade_log:
            result = self.mcp.record_trades(self.trade_log)
            logging.info(f"Posted trades to MCP: {result}")

    def visualize_trades(self):
        if not self.trade_log:
            logging.warning("No trades to visualize.")
            return
        symbols = [entry["symbol"] for entry in self.trade_log]
        amounts = [entry["amount"] for entry in self.trade_log]
        plt.figure(figsize=(8, 6))
        plt.bar(symbols, amounts)
        plt.xlabel("Symbol")
        plt.ylabel("Investment Amount ($)")
        plt.title("LLM-Driven Investment Allocation")
        plt.show()

    def log_trades_to_file(self, filename="trade_log.csv"):
        with open(filename, "w") as f:
            f.write("time,symbol,amount\n")
            for entry in self.trade_log:
                f.write(f"{entry['time']},{entry['symbol']},{entry['amount']}\n")
        logging.info(f"Trade log saved to {filename}")

    def should_rebalance(self):
        return (datetime.now() - self.last_rebalance) >= timedelta(days=1)

    def run(self, simulate=True):
        if self.should_rebalance():
            self.generate_portfolio_with_llm()
            if self.portfolio:
                if simulate:
                    self.simulate_orders()
                    self.visualize_trades()
                    self.log_trades_to_file()
                else:
                    self.rebalance_portfolio()
                self.last_rebalance = datetime.now()
            else:
                logging.warning("No portfolio generated.")
        else:
            logging.info("No rebalance needed today.")

if __name__ == "__main__":
    api_key = "YOUR_M1_API_KEY"
    agent = SmartM1TradingAgent(api_key)
    agent.run(simulate=True)