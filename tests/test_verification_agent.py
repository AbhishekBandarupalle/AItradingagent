import unittest
from unittest.mock import patch, MagicMock
from trade_verification_agent import TradeVerificationAgent

class TestTradeVerificationAgent(unittest.TestCase):
    @patch('trade_verification_agent.MCPClient')
    def test_format_email_body(self, MockMCPClient):
        agent = TradeVerificationAgent()
        trades = [
            {"symbol": "AAPL", "amount": 500, "time": "2024-06-01T12:00:00"},
            {"symbol": "MSFT", "amount": 500, "time": "2024-06-01T12:00:00"}
        ]
        body = agent.format_email_body(trades)
        self.assertIn("AAPL", body)
        self.assertIn("MSFT", body)
        self.assertIn("$500.00", body)

if __name__ == '__main__':
    unittest.main() 