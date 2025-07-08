
# Smart M1 Trading Agent (LLM Driven)

This project uses a local LLM (e.g., LLaMA on Ollama) and inter-agent communication via an MCP server to make **all trading decisions**, verify them, and send email summaries.

## Features
- LLM-driven portfolio generation (via `mistral:latest` on Ollama)
- Simulated trading with visualization
- Trade logging for audit and analysis
- Trade verification agent with email reports
- Communication via MCP (local HTTP server)

## Requirements
- Python 3.8+
- `requests`, `matplotlib`
- A local MCP server (via container)
- A Gmail account for sending emails (app password required)

## Setup

### 1. Run MCP Server (as Docker container)
Assuming you have an MCP-compatible LLM (e.g. Ollama w/ Mistral):
```bash
docker run -d -p 11434:11434 --name mcp-server your-mcp-container
```
Ensure it's available at `http://localhost:11434/mcp`

### 2. Set Up Gmail for SMTP
Use an [App Password](https://support.google.com/accounts/answer/185833?hl=en) (2FA must be enabled).
Update the agent’s email config:
```python
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "your@gmail.com"
EMAIL_PASS = "your_app_password"
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the trading agent (simulated)
```bash
python smart_m1_trading_agent_llm.py
```

### 5. Run the verification agent
```bash
python trade_verification_agent.py
```

## Usage
- The trading agent generates portfolio decisions via LLM and posts trade logs
- The verification agent retrieves them via MCP and emails a report

## Notes
- Make sure both agents are running in the same MCP communication environment
- Adjust prompts to suit the model’s style and formatting

## Disclaimer
This tool is for educational purposes only. Use at your own risk.
