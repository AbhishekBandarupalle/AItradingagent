#!/bin/bash
# Example: Run the trading agent with environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
python ../smart_m1_trading_agent_llm.py 