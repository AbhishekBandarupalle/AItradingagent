import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from utils import MCPClient

class TestMCPClient(unittest.TestCase):
    @patch('utils.mcp.mcp_client.requests.post')
    def test_send_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'ok'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        client = MCPClient('http://fake-url')
        result = client.send('PROMPT')
        self.assertEqual(result, 'ok')

    @patch('utils.mcp.mcp_client.requests.post')
    def test_send_failure(self, mock_post):
        mock_post.side_effect = Exception('fail')
        client = MCPClient('http://fake-url')
        result = client.send('PROMPT')
        self.assertEqual(result, '')

if __name__ == '__main__':
    unittest.main() 