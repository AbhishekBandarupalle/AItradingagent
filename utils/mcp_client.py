
import requests
import json
import logging

class MCPClient:
    def __init__(self, mcp_url="http://localhost:11534"):
        self.mcp_url = mcp_url
        self.mcp_endpoint = f"{mcp_url}/mcp"
        self.api_base = f"{mcp_url}/api"

    def send(self, prompt):
        """Send a prompt to the MCP server (for LLM requests)."""
        response = requests.post(self.mcp_endpoint, json={"prompt": prompt}, timeout=30)
        if response.status_code == 200:
            return response.json().get("result", "")
        else:
            return f"Error: {response.status_code}"

    def save_trades(self, trades):
        """Save trades to the database via MCP server."""
        try:
            response = requests.post(f"{self.api_base}/trades", json={"trades": trades}, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logging.error(f"Error saving trades: {e}")
            return {"success": False, "error": str(e)}

    def get_trades(self, limit=None):
        """Get trades from the database via MCP server."""
        try:
            url = f"{self.api_base}/trades"
            if limit:
                url += f"?limit={limit}"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}", "trades": []}
        except Exception as e:
            logging.error(f"Error getting trades: {e}")
            return {"success": False, "error": str(e), "trades": []}

    def get_latest_transaction(self):
        """Get the latest transaction from the database via MCP server."""
        try:
            response = requests.get(f"{self.api_base}/trades/latest", timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}", "trades": []}
        except Exception as e:
            logging.error(f"Error getting latest transaction: {e}")
            return {"success": False, "error": str(e), "trades": []}

    def get_current_holdings(self):
        """Get current holdings from the database via MCP server."""
        try:
            response = requests.get(f"{self.api_base}/holdings", timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}", "holdings": {}, "cash": 0}
        except Exception as e:
            logging.error(f"Error getting holdings: {e}")
            return {"success": False, "error": str(e), "holdings": {}, "cash": 0}

    def get_last_transaction_id(self):
        """Get the last transaction ID from the database via MCP server."""
        try:
            response = requests.get(f"{self.api_base}/transaction-id", timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}", "transaction_id": 0}
        except Exception as e:
            logging.error(f"Error getting transaction ID: {e}")
            return {"success": False, "error": str(e), "transaction_id": 0}

    def record_trades(self, trades):
        """Legacy method for backward compatibility - uses new save_trades method."""
        return self.save_trades(trades)
