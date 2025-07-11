"""
Utilities module for AI Trading Agent

This module provides various utility functions and classes for:
- System setup and dependency management
- Database operations
- Sentiment analysis
- LLM response processing
- Trade logging
- MCP (Model Context Protocol) client/server
"""

# Version info
__version__ = '1.0.0'

# System setup utilities
from .system_setup import (
    get_system_info,
    check_package_manager,
    check_node_installed,
    install_nodejs,
    check_python_requirements,
    install_python_requirements,
    install_react_dependencies,
    setup_system_dependencies,
    check_mongodb_installed,
    install_mongodb
)

# Database utilities
try:
    from .db_utils import TradeDatabase, cleanup_trading_database
except ImportError:
    pass

# Sentiment analysis utilities
try:
    from .finbert_sentiment import FinBertSentiment
except ImportError:
    pass

# LLM response utilities
from .llm_response_utils import (
    clean_llm_json,
    extract_json_from_streaming_response,
    validate_and_parse_json
)

# Trade logging utilities
from .trade_log_utils import load_trade_log, save_trade_log

# MCP utilities
try:
    from .mcp import MCPClient, mcp_server_app
except ImportError:
    pass
