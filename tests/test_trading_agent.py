import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from agents.trading_agent import SmartM1TradingAgent

class TestSmartM1TradingAgent(unittest.TestCase):
    @patch('agents.trading_agent.MCPClient')
    def test_generate_portfolio_with_llm(self, MockMCPClient):
        mock_mcp = MockMCPClient.return_value
        mock_mcp.send.return_value = '{"AAPL": 0.6, "MSFT": 0.4}'
        agent = SmartM1TradingAgent(api_key='dummy')
        agent.generate_portfolio_with_llm()
        self.assertEqual(agent.portfolio, {"AAPL": 0.6, "MSFT": 0.4})

if __name__ == '__main__':
    unittest.main() 