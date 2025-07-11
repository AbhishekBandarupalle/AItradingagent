#!/usr/bin/env python3
"""
Test script to verify MongoDB database setup and MCP server integration.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath('..'))

from utils import TradeDatabase, MCPClient

def test_database_direct():
    """Test direct database connectivity."""
    print("Testing direct database connectivity...")
    
    try:
        db = TradeDatabase()
        
        # Test saving a sample trade
        sample_trade = {
            "transaction_id": "99999",
            "time": "12:00:00",
            "date": "10-07-25",
            "symbol": "TEST",
            "action": "Buy",
            "shares_changed": 10.0,
            "shares_held": 10.0,
            "current_price": 100.0,
            "amount": 1000.0,
            "allocation": 0.1,
            "cash": 9000.0,
            "sentiment": 1.2,
            "last_sentiment": 1.0,
            "portfolio_value": 10000.0,
            "final_cash": 9000.0
        }
        
        result = db.save_trades([sample_trade])
        print(f"Save result: {result}")
        
        # Test retrieving trades
        result = db.get_all_trades()
        print(f"Retrieved {len(result['trades'])} trades")
        
        # Test getting last transaction ID
        result = db.get_last_transaction_id()
        print(f"Last transaction ID: {result}")
        
        # Test getting current holdings
        result = db.get_current_holdings()
        print(f"Current holdings: {result}")
        
        db.close()
        print("✅ Direct database test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Direct database test failed: {e}")
        return False

def test_mcp_client():
    """Test MCP client database endpoints."""
    print("\nTesting MCP client database endpoints...")
    
    try:
        mcp = MCPClient("http://localhost:11534")
        
        # Test getting trades
        result = mcp.get_trades()
        print(f"MCP get_trades result: {result['success']}, {len(result['trades'])} trades")
        
        # Test getting holdings
        result = mcp.get_current_holdings()
        print(f"MCP get_holdings result: {result}")
        
        # Test getting transaction ID
        result = mcp.get_last_transaction_id()
        print(f"MCP get_transaction_id result: {result}")
        
        print("✅ MCP client test passed!")
        return True
        
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        return False

def test_llm_integration():
    """Test LLM integration through MCP."""
    print("\nTesting LLM integration...")
    
    try:
        mcp = MCPClient("http://localhost:11534")
        
        # Test a simple LLM prompt
        prompt = "Respond with a JSON object: {\"test\": \"success\"}"
        result = mcp.send(prompt)
        print(f"LLM response: {result}")
        
        print("✅ LLM integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ LLM integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting database integration tests...\n")
    
    # Test 1: Direct database connectivity
    db_test = test_database_direct()
    
    # Test 2: MCP client (requires MCP server to be running)
    mcp_test = test_mcp_client()
    
    # Test 3: LLM integration (requires MCP server and LLM to be running)
    llm_test = test_llm_integration()
    
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"Direct Database: {'✅ PASS' if db_test else '❌ FAIL'}")
    print(f"MCP Client:      {'✅ PASS' if mcp_test else '❌ FAIL'}")
    print(f"LLM Integration: {'✅ PASS' if llm_test else '❌ FAIL'}")
    print("="*50)
    
    if all([db_test, mcp_test, llm_test]):
        print("🎉 All tests passed! Your system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the setup:")
        print("  - Make sure MongoDB is running (default: localhost:27017)")
        print("  - Make sure MCP server is running (python utils/mcp/mcp_server.py)")
        print("  - Make sure LLM server is running (e.g., Ollama)")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 