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

# System setup utilities
from .system_setup import (
    get_system_info,
    check_package_manager,
    check_node_installed,
    install_nodejs,
    check_python_requirements,
    install_python_requirements,
    install_react_dependencies,
    setup_system_dependencies
)

# Database utilities
try:
    from .db_utils import TradeDatabase
    _DB_AVAILABLE = True
except ImportError as e:
    _DB_AVAILABLE = False
    print(f"Warning: Database utilities not available: {e}")

# Sentiment analysis utilities
try:
    from .finbert_sentiment import FinBertSentiment
    _SENTIMENT_AVAILABLE = True
except ImportError as e:
    _SENTIMENT_AVAILABLE = False
    print(f"Warning: Sentiment analysis not available: {e}")

# LLM response utilities
from .llm_response_utils import clean_llm_json

# Trade logging utilities
from .trade_log_utils import load_trade_log, save_trade_log

# MCP utilities
try:
    from .mcp import MCPClient
    try:
        from .mcp import mcp_server_app
        _MCP_SERVER_AVAILABLE = True
    except ImportError:
        _MCP_SERVER_AVAILABLE = False
    _MCP_CLIENT_AVAILABLE = True
except ImportError as e:
    _MCP_CLIENT_AVAILABLE = False
    _MCP_SERVER_AVAILABLE = False
    print(f"Warning: MCP utilities not available: {e}")

# Define what should be available when importing from utils
__all__ = [
    # System setup
    'get_system_info',
    'check_package_manager', 
    'check_node_installed',
    'install_nodejs',
    'check_python_requirements',
    'install_python_requirements',
    'install_react_dependencies',
    'setup_system_dependencies',
    
    # LLM utilities
    'clean_llm_json',
    
    # Trade logging
    'load_trade_log',
    'save_trade_log',
]

# Conditionally add database utilities
if _DB_AVAILABLE:
    __all__.append('TradeDatabase')

# Conditionally add sentiment analysis
if _SENTIMENT_AVAILABLE:
    __all__.append('FinBertSentiment')

# Conditionally add MCP utilities
if _MCP_CLIENT_AVAILABLE:
    __all__.append('MCPClient')
if _MCP_SERVER_AVAILABLE:
    __all__.append('mcp_server_app')

# Version info
__version__ = '1.0.0'
