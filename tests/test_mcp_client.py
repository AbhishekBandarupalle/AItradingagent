# Standard library imports
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath('..'))

# Local imports
from utils import MCPClient

class TestMCPClient(unittest.TestCase):
    @patch('utils.mcp.mcp_client.requests.post')
    def test_send_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'ok'}
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        client = MCPClient('http://fake-url')
        result = client.send('PROMPT')
        self.assertEqual(result, 'ok')

    @patch('utils.mcp.mcp_client.requests.post')
    def test_send_failure(self, mock_post):
        mock_post.side_effect = Exception('fail')
        client = MCPClient('http://fake-url')
        with self.assertRaises(Exception):
            client.send('PROMPT')

if __name__ == '__main__':
    unittest.main() 