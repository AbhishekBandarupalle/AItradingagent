import requests
import smtplib
from email.message import EmailMessage
import json
import os
import sys
from datetime import datetime
from collections import defaultdict
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.mcp_client import MCPClient
# Remove: from utils.trade_log_utils import load_trade_log, save_trade_log

log_dir = 'logging'
os.makedirs(log_dir, exist_ok=True)

class TradeVerificationAgent:
    """Agent that fetches trades from MCP and sends a summary email via Gmail SMTP."""
    def __init__(self, mcp_url="http://localhost:11534/mcp", email_to=None):
        """Initialize the agent with MCP URL and email configuration from environment variables."""
        self.mcp = MCPClient(mcp_url)
        self.email_to = email_to or os.environ.get("EMAIL_TO", "test@gmail.com")
        self.email_host = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
        self.email_port = int(os.environ.get("EMAIL_PORT", 587))
        self.email_user = os.environ.get("EMAIL_USER", "your@gmail.com")
        self.email_pass = os.environ.get("EMAIL_PASS", "your_app_password")  # Use an app password if 2FA is enabled

    def fetch_trades(self):
        # Query MCP for latest trades
        result = self.mcp.send("GET_LATEST_TRADES")
        try:
            trades = json.loads(result)
        except Exception:
            trades = []
        # Only return trades that are not verified
        unverified = [t for t in trades if not t.get('verified', False)]
        return unverified

    def mark_trades_verified(self, up_to_id=None):
        # Mark trades as verified via MCP
        if up_to_id:
            prompt = f"MARK_TRADES_VERIFIED:{up_to_id}"
        else:
            prompt = "MARK_TRADES_VERIFIED"
        self.mcp.send(prompt)

    def format_email_body(self, trades):
        # Group trades by transaction_id
        transactions = defaultdict(list)
        for trade in trades:
            transactions[trade['transaction_id']].append(trade)
        # Sort by transaction_id (as int)
        sorted_ids = sorted(transactions.keys(), key=lambda x: int(x))
        lines = [f"Trade Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
        prev_total = None
        for tid in sorted_ids:
            batch = transactions[tid]
            # Assume all trades in batch have same time/date
            t_time = batch[0]['time']
            t_date = batch[0]['date']
            total = sum(trade['amount'] for trade in batch)
            delta = f" (+{total - prev_total:.2f})" if prev_total is not None else ""
            lines.append(f"Transaction {tid} at {t_time} on {t_date} | Total: ${total:.2f}{delta}")
            for trade in batch:
                alloc_pct = f"{trade['allocation']*100:.1f}%"
                price = trade['current_price'] if trade['current_price'] is not None else 'N/A'
                if price != 'N/A' and price != 0:
                    shares = trade['amount'] / price
                    shares_str = f"{shares:.4f} shares"
                else:
                    shares_str = "N/A shares"
                lines.append(f"  {trade['symbol']}: {alloc_pct} @ ${price} | Amount: ${trade['amount']:.2f} | {shares_str}")
            lines.append("")
            prev_total = total
        return "\n".join(lines)

    def send_email(self, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = "Daily Trade Verification Report"
        msg["From"] = self.email_user
        msg["To"] = self.email_to

        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            print("Verification email sent.")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def run(self):
        trades = self.fetch_trades()
        if trades:
            email_body = self.format_email_body(trades)
            self.send_email(email_body)
            # Mark all trades up to the latest transaction_id as verified
            last_id = max(int(t['transaction_id']) for t in trades)
            self.mark_trades_verified(up_to_id=last_id)
        else:
            print("No new trades to verify.")

if __name__ == "__main__":
    agent = TradeVerificationAgent()
    agent.run()