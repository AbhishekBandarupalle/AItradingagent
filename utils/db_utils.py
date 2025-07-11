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
        """Save trades to the database and update the portfolio."""
        try:
            inserted_count = 0
            for trade in trades:
                self.trades_collection.insert_one(trade)
                self.update_portfolio_from_trade(trade)
                inserted_count += 1
            logging.info(f"Saved {inserted_count} trades to database and updated portfolio")
            return {"success": True, "inserted_count": inserted_count}
        except Exception as e:
            logging.error(f"Error saving trades: {e}")
            return {"success": False, "error": str(e)}

    def update_portfolio_from_trade(self, trade):
        """Update the portfolio collection based on a new trade."""
        symbol = trade["symbol"]
        shares_changed = trade.get("shares_changed", 0)
        price = trade.get("current_price", 0)
        cash = trade.get("cash", None)
        # Handle cash init
        if symbol == "CASH_INIT":
            self.portfolio_collection.delete_many({})  # Reset portfolio
            self.portfolio_collection.insert_one({"symbol": "CASH", "shares": 0, "price": 1.0, "value": cash, "cash": cash})
            return
        # Update asset holding
        holding = self.portfolio_collection.find_one({"symbol": symbol})
        if holding:
            new_shares = holding.get("shares", 0) + shares_changed
            if new_shares > 0:
                self.portfolio_collection.update_one({"symbol": symbol}, {"$set": {"shares": new_shares, "price": price, "value": new_shares * price}})
            else:
                self.portfolio_collection.delete_one({"symbol": symbol})
        else:
            if shares_changed > 0:
                self.portfolio_collection.insert_one({"symbol": symbol, "shares": shares_changed, "price": price, "value": shares_changed * price})
        # Update cash if present
        if cash is not None:
            self.portfolio_collection.update_one({"symbol": "CASH"}, {"$set": {"cash": cash, "value": cash}}, upsert=True)

    def get_portfolio(self):
        """Return the current portfolio (all holdings with shares > 0 and cash)."""
        try:
            holdings = {}
            cash = 0
            for doc in self.portfolio_collection.find({}):
                if doc["symbol"] == "CASH":
                    cash = doc.get("cash", 0)
                elif doc.get("shares", 0) > 0:
                    holdings[doc["symbol"]] = {"shares": doc["shares"], "price": doc["price"], "value": doc["value"]}
            portfolio_value = sum(v["value"] for v in holdings.values()) + cash
            return {"success": True, "holdings": holdings, "cash": cash, "portfolio_value": portfolio_value}
        except Exception as e:
            logging.error(f"Error getting portfolio: {e}")
            return {"success": False, "error": str(e), "holdings": {}, "cash": 0, "portfolio_value": 0}

    def get_trades(self, limit=None):
        """Get trades from the database via MCP server."""
        try:
            query = {}
            cursor = self.trades_collection.find(query, {"_id": 0}).sort([("transaction_id", 1), ("time", 1)])
            if limit:
                cursor = cursor.limit(limit)
            trades = list(cursor)
            return {"success": True, "trades": trades}
        except Exception as e:
            logging.error(f"Error getting trades: {e}")
            return {"success": False, "error": str(e), "trades": []}

    def get_current_holdings(self):
        """Return the current portfolio (all holdings with shares > 0 and cash)."""
        return self.get_portfolio()
    
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
    
    def cleanup_all_trades(self):
        """Clean up all trades from the database."""
        try:
            result = self.trades_collection.delete_many({})
            logging.info(f"Cleaned up {result.deleted_count} trades from database")
            return {"success": True, "deleted_count": result.deleted_count}
        except Exception as e:
            logging.error(f"Error cleaning up trades: {e}")
            return {"success": False, "error": str(e), "deleted_count": 0}
    
    def cleanup_test_trades(self):
        """Clean up test trades (transaction_id 99999) from the database."""
        try:
            result = self.trades_collection.delete_many({"transaction_id": "99999"})
            logging.info(f"Cleaned up {result.deleted_count} test trades from database")
            return {"success": True, "deleted_count": result.deleted_count}
        except Exception as e:
            logging.error(f"Error cleaning up test trades: {e}")
            return {"success": False, "error": str(e), "deleted_count": 0}
    
    def cleanup_trades_by_date_range(self, start_date=None, end_date=None):
        """Clean up trades within a specific date range."""
        try:
            query = {}
            if start_date:
                query["date"] = {"$gte": start_date}
            if end_date:
                if "date" in query:
                    query["date"]["$lte"] = end_date
                else:
                    query["date"] = {"$lte": end_date}
            
            result = self.trades_collection.delete_many(query)
            logging.info(f"Cleaned up {result.deleted_count} trades from database for date range")
            return {"success": True, "deleted_count": result.deleted_count}
        except Exception as e:
            logging.error(f"Error cleaning up trades by date range: {e}")
            return {"success": False, "error": str(e), "deleted_count": 0}
    
    def reset_database(self):
        """Reset the database by dropping all collections and recreating them."""
        try:
            # Drop all collections
            self.trades_collection.drop()
            self.portfolio_collection.drop()
            
            # Recreate collections (they'll be created automatically on first insert)
            logging.info("Database reset completed - all collections dropped")
            return {"success": True, "message": "Database reset completed"}
        except Exception as e:
            logging.error(f"Error resetting database: {e}")
            return {"success": False, "error": str(e)} 

def cleanup_trading_database(connection_string="mongodb://localhost:27017/", db_name="trading_agent"):
    """
    Standalone function to clean up the trading database.
    Can be called independently without creating a TradeDatabase instance.
    """
    try:
        print("🧹 Cleaning up trading database...")
        db = TradeDatabase(connection_string, db_name)
        
        # Clean up test trades first
        test_result = db.cleanup_test_trades()
        if test_result['success'] and test_result['deleted_count'] > 0:
            print(f"✅ Cleaned up {test_result['deleted_count']} test trades")
        
        # Clean up all trades
        cleanup_result = db.cleanup_all_trades()
        if cleanup_result['success']:
            print(f"✅ Cleaned up {cleanup_result['deleted_count']} total trades from database")
        else:
            print(f"⚠️  Could not clean up all trades: {cleanup_result['error']}")
        
        # Reset entire database
        reset_result = db.reset_database()
        if reset_result['success']:
            print("✅ Database completely reset")
        else:
            print(f"⚠️  Could not reset database: {reset_result['error']}")
        
        db.close()
        print("🎉 Database cleanup completed successfully!")
        return {"success": True, "message": "Database cleanup completed"}
        
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Allow running this script directly to clean up database
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_trading_database() 