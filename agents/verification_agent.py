# Standard library imports
import os
import smtplib
import sys
from collections import defaultdict
from datetime import datetime
from email.message import EmailMessage

# Local imports
# Add project root to Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import MCPClient

log_dir = 'logging'
os.makedirs(log_dir, exist_ok=True)

class TradeVerificationAgent:
    """Agent that fetches trades from MCP and sends a summary email via Gmail SMTP."""
    def __init__(self, mcp_url="http://localhost:11534", email_to=None):
        """Initialize the agent with MCP URL and email configuration from environment variables."""
        self.mcp = MCPClient(mcp_url)
        self.email_to = email_to or os.environ.get("EMAIL_TO", "test@gmail.com")
        self.email_host = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
        self.email_port = int(os.environ.get("EMAIL_PORT", 587))
        self.email_user = os.environ.get("EMAIL_USER", "your@gmail.com")
        self.email_pass = os.environ.get("EMAIL_PASS", "your_app_password")  # Use an app password if 2FA is enabled

    def fetch_trades(self):
        # Get all trades from database via MCP
        result = self.mcp.get_trades()
        if not result['success']:
            print(f"Error fetching trades: {result['error']}")
            return []
        
        trades = result['trades']
        # Only return trades that are not verified
        unverified = [t for t in trades if not t.get('verified', False)]
        return unverified

    def mark_trades_verified(self, up_to_id=None):
        # Mark trades as verified via MCP
        # TODO: Implement verification marking in database
        # For now, use the legacy prompt-based approach
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
            # Use portfolio_value if available, otherwise sum amounts
            total = batch[0].get('portfolio_value', sum(trade['amount'] for trade in batch))
            delta = f" (+{total - prev_total:.2f})" if prev_total is not None else ""
            lines.append(f"Transaction {tid} at {t_time} on {t_date} | Portfolio Value: ${total:.2f}{delta}")
            for trade in batch:
                alloc_pct = f"{trade['allocation']*100:.1f}%"
                price = trade['current_price'] if trade['current_price'] is not None else 'N/A'
                shares_held = trade.get('shares_held', 0)
                action = trade.get('action', 'N/A')
                lines.append(f"  {trade['symbol']}: {action} | {alloc_pct} @ ${price} | Shares: {shares_held:.4f} | Amount: ${trade['amount']:.2f}")
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

    def run_continuous(self, interval_minutes=10):
        print(f"Starting continuous verification agent loop. Interval: {interval_minutes} minutes.")
        try:
            while True:
                self.run()
                print(f"Sleeping for {interval_minutes} minutes before next verification.")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("Continuous verification agent loop stopped by user.")

if __name__ == "__main__":
    import time
    agent = TradeVerificationAgent()
    agent.run_continuous(interval_minutes=2)