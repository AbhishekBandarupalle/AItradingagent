import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from agents.trading_agent import SmartM1TradingAgent

class TestSmartM1TradingAgent(unittest.TestCase):
    @patch('agents.trading_agent.FinBertSentiment')
    @patch('agents.trading_agent.SmartM1TradingAgent.get_top_movers')
    @patch('agents.trading_agent.SmartM1TradingAgent.fetch_news_sentiment_batch')
    @patch('agents.trading_agent.MCPClient')
    def test_generate_portfolio_with_llm(self, MockMCPClient, mock_news, mock_movers, MockFinBert):
        mock_mcp = MockMCPClient.return_value
        mock_mcp.send.side_effect = [
            '{"funds": ["SPY"]}',
            '{"AAPL": 0.6, "MSFT": 0.4}'
        ]
        mock_movers.return_value = (["AAPL"], ["MSFT"])
        mock_news.return_value = {
            "AAPL": (["h1"], 1.1),
            "MSFT": (["h2"], 1.1)
        }
        MockFinBert.return_value.aggregate_score.return_value = {"positive":1.0,"negative":0.0,"neutral":0.0}
        agent = SmartM1TradingAgent(api_key='dummy')
        agent.generate_portfolio_with_llm()
        self.assertEqual(agent.portfolio, {"AAPL": 0.6, "MSFT": 0.4})

if __name__ == '__main__':
    unittest.main() 