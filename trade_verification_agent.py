import requests
import smtplib
from email.message import EmailMessage
import json
from mcp_client import MCPClient
from datetime import datetime
import os

class TradeVerificationAgent:
    """Agent that fetches trades from MCP and sends a summary email via Gmail SMTP."""
    def __init__(self, mcp_url="http://localhost:11434/mcp", email_to=None):
        """Initialize the agent with MCP URL and email configuration from environment variables."""
        self.mcp = MCPClient(mcp_url)
        self.email_to = email_to or os.environ.get("EMAIL_TO", "test@gmail.com")
        self.email_host = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
        self.email_port = int(os.environ.get("EMAIL_PORT", 587))
        self.email_user = os.environ.get("EMAIL_USER", "your@gmail.com")
        self.email_pass = os.environ.get("EMAIL_PASS", "your_app_password")  # Use an app password if 2FA is enabled

    def fetch_trades(self):
        """Fetch the latest trades from MCP."""
        result = self.mcp.get_latest_trades()
        try:
            trades = json.loads(result)
            return trades if isinstance(trades, list) else []
        except Exception as e:
            print(f"Failed to parse trades: {e}")
            return []

    def format_email_body(self, trades):
        """Format the email body with a summary of trades."""
        lines = ["Trade Summary - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ""]
        for trade in trades:
            lines.append(f"{trade['symbol']}: ${trade['amount']:.2f} at {trade['time']}")
        return "\n".join(lines)

    def send_email(self, body):
        """Send the summary email using SMTP."""
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
        """Fetch trades and send a summary email if trades are found."""
        trades = self.fetch_trades()
        if trades:
            email_body = self.format_email_body(trades)
            self.send_email(email_body)
        else:
            print("No trades found or failed to retrieve.")

if __name__ == "__main__":
    agent = TradeVerificationAgent()
    agent.run()