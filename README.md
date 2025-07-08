# Smart M1 Trading Agent (LLM + MCP + Email Verification) 🧠💹  
![Python](https://img.shields.io/badge/python-3.8%2B-blue) 

This project contains two intelligent agents that collaborate using a shared local MCP server:

- 🤖 **Trading Agent** — Uses an LLM to generate a dynamic investment portfolio and posts simulated trades
- 📬 **Verification Agent** — Pulls those trades via MCP and sends a daily email summary

---

## ⚡️ LLM Simulator with Real Trading Potential

This project is currently an **LLM-based trade simulator**:
- The trading agent uses a local LLM to generate portfolio allocations and simulates trades (no real money is moved).
- All trades are logged, visualized, and posted to MCP for verification and reporting.
- The verification agent emails a summary of simulated trades.

**Extensibility:**
- The code is designed to be easily extended to use the M1 Finance API (or any brokerage API) for real trading.
- To enable real trading, replace the simulation logic in the trading agent with API calls to your brokerage (using the provided `api_key` parameter).
- The LLM can continue to generate portfolio recommendations, but execution can be real.

---

## ✨ Features

- Portfolio logic powered by your local LLM (e.g., `mistral:latest` via Ollama)
- Inter-agent communication using MCP over HTTP
- Trade visualization and CSV logging
- Email delivery of trade summaries via Gmail SMTP

---

## 📦 Components

- `smart_m1_trading_agent_llm.py` — Main LLM-based trading agent
- `trade_verification_agent.py` — Companion agent that sends email reports
- `mcp_client.py` — Shared helper for communicating over MCP
- `requirements.txt` — Dependencies

---

## 🚀 Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run MCP-compatible LLM server (e.g. Ollama + Mistral)

Using Ollama: 
```bash
ollama pull mistral
ollama run mistral
```
Using a Docker Container:
```bash
docker run -d -p 11434:11434 your-mcp-server
```
Verify if MCP server is listening at: http://localhost:11434/mcp

### 3. Configure Gmail for email reports

- Enable 2FA on your Gmail account
- Create an [App Password](https://support.google.com/accounts/answer/185833)
- Set the following environment variables (recommended for security):
    ```bash
    export EMAIL_USER="your@gmail.com"
    export EMAIL_PASS="your_app_password"
    export EMAIL_TO="recipient@gmail.com"
    export EMAIL_HOST="smtp.gmail.com"  # Optional, default is smtp.gmail.com
    export EMAIL_PORT=587               # Optional, default is 587
    ```
- You can add these lines to your `.env` or shell profile for convenience.

### 4. Run the agents

Simulate and log trades:
```bash
python smart_m1_trading_agent_llm.py
```
Send trade verification/update email:
```bash
python trade_verification_agent.py
```

---

## 🛠 Troubleshooting

**1. MCP server connection errors**
- Ensure your MCP server is running and accessible at the configured URL (default: http://localhost:11434/mcp).
- Check for firewall or port conflicts.

**2. Email not sending**
- Double-check your environment variables for email credentials.
- Make sure you have enabled 2FA and are using an App Password for Gmail.
- Check your spam folder and SMTP server logs for errors.

**3. LLM returns invalid JSON**
- Adjust your LLM prompt for stricter output formatting.
- Add error handling or fallback logic in the agent code.

**4. No trades found**
- Ensure the trading agent has run and posted trades to MCP before running the verification agent.

**5. Logging issues**
- Check that you have write permissions in the project directory for log files.
- Log files are rotated daily and kept for 7 days by default.

If you encounter other issues, please open an issue or pull request on the repository.