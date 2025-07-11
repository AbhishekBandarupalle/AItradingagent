from pymongo import MongoClient
from datetime import datetime
import logging
import os

class TradeDatabase:
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="trading_agent"):
        """Initialize MongoDB connection."""
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.trades_collection = self.db.trades
        self.portfolio_collection = self.db.portfolio
        
    def save_trades(self, trades):
        """Save trades to the database."""
        try:
            if trades:
                result = self.trades_collection.insert_many(trades)
                logging.info(f"Saved {len(result.inserted_ids)} trades to database")
                return {"success": True, "inserted_count": len(result.inserted_ids)}
            return {"success": True, "inserted_count": 0}
        except Exception as e:
            logging.error(f"Error saving trades: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_trades(self):
        """Get all trades from the database."""
        try:
            trades = list(self.trades_collection.find({}, {"_id": 0}).sort("date", -1).sort("time", -1))
            return {"success": True, "trades": trades}
        except Exception as e:
            logging.error(f"Error fetching trades: {e}")
            return {"success": False, "error": str(e), "trades": []}
    
    def get_latest_trades(self, limit=10):
        """Get the latest trades from the database."""
        try:
            trades = list(self.trades_collection.find({}, {"_id": 0}).sort([("date", -1), ("time", -1)]).limit(limit))
            return {"success": True, "trades": trades}
        except Exception as e:
            logging.error(f"Error fetching latest trades: {e}")
            return {"success": False, "error": str(e), "trades": []}
    
    def get_latest_transaction(self):
        """Get the latest transaction (all trades with the same transaction_id)."""
        try:
            latest_trade = self.trades_collection.find_one({}, {"_id": 0}, sort=[("transaction_id", -1)])
            if not latest_trade:
                return {"success": True, "trades": []}
            
            latest_transaction_id = latest_trade["transaction_id"]
            trades = list(self.trades_collection.find(
                {"transaction_id": latest_transaction_id}, 
                {"_id": 0}
            ).sort("symbol", 1))
            
            return {"success": True, "trades": trades}
        except Exception as e:
            logging.error(f"Error fetching latest transaction: {e}")
            return {"success": False, "error": str(e), "trades": []}
    
    def get_current_holdings(self):
        """Get current holdings from the latest transaction."""
        try:
            result = self.get_latest_transaction()
            if not result["success"]:
                return result
            
            holdings = {}
            cash = 0
            for trade in result["trades"]:
                if trade["shares_held"] > 0:
                    holdings[trade["symbol"]] = {
                        "shares": trade["shares_held"],
                        "price": trade["current_price"],
                        "value": trade["shares_held"] * trade["current_price"] if trade["current_price"] else 0
                    }
                cash = trade.get("cash", 0)  # All trades in same transaction have same cash
            
            return {"success": True, "holdings": holdings, "cash": cash}
        except Exception as e:
            logging.error(f"Error getting current holdings: {e}")
            return {"success": False, "error": str(e), "holdings": {}, "cash": 0}
    
    def get_last_transaction_id(self):
        """Get the last transaction ID."""
        try:
            latest_trade = self.trades_collection.find_one({}, {"transaction_id": 1}, sort=[("transaction_id", -1)])
            if latest_trade:
                return {"success": True, "transaction_id": int(latest_trade["transaction_id"])}
            return {"success": True, "transaction_id": 0}
        except Exception as e:
            logging.error(f"Error getting last transaction ID: {e}")
            return {"success": False, "error": str(e), "transaction_id": 0}
    
    def close(self):
        """Close the database connection."""
        self.client.close() 