#!/bin/bash
# Example: Run the verification agent with environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
python ../trade_verification_agent.py 