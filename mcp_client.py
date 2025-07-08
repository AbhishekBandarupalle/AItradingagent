
import requests
import json

class MCPClient:
    def __init__(self, mcp_url="http://localhost:11434/mcp"):
        self.mcp_url = mcp_url

    def send(self, prompt):
        try:
            response = requests.post(self.mcp_url, json={"prompt": prompt}, timeout=30)
            response.raise_for_status()
            return response.json().get("result", "")
        except Exception as e:
            print(f"MCP request failed: {e}")
            return ""

    def record_trades(self, trades):
        prompt = f"RECORD_TRADES: {json.dumps(trades)}"
        return self.send(prompt)

    def get_latest_trades(self):
        return self.send("GET_LATEST_TRADES")
