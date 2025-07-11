# MCP Server Guide 🔄

## Overview

The Model Context Protocol (MCP) server acts as the central communication hub for the AI Trading Agent System. It provides a unified interface for LLM communication, database operations, and inter-agent messaging.

## Architecture

### MCP Server Components

```
┌────────────────────────────────────────┐
│               MCP Server               │
│            (Port 11534)                │
├────────────────────────────────────────┤
│  HTTP Endpoints                        │
│  ├── /mcp (LLM & Legacy)               │
│  ├── /api/trades (Database)            │
│  ├── /api/holdings (Portfolio)         │
│  └── /api/transaction-id (Metadata)    │
├────────────────────────────────────────┤
│  Backend Integrations                  │
│  ├── MongoDB (Database)                │
│  ├── Ollama/Mistral (LLM)              │
│  └── Database Utils                    │
└────────────────────────────────────────┘
```

### Communication Flow

1. **Agent** → **MCPClient** → **HTTP Request** → **MCP Server**
2. **MCP Server** → **Database/LLM** → **Response** → **Agent**

## API Endpoints

### Database Endpoints

#### `POST /api/trades`
Save trades to the database.

**Request:**
```json
{
  "trades": [
    {
      "transaction_id": "00001",
      "time": "14:30:00",
      "date": "10-07-25",
      "symbol": "TSLA",
      "action": "Buy",
      "shares_changed": 5.0,
      "shares_held": 5.0,
      "current_price": 250.0,
      "amount": 1250.0,
      "allocation": 0.125,
      "cash": 8750.0,
      "sentiment": 1.2,
      "last_sentiment": 1.0,
      "portfolio_value": 10000.0,
      "final_cash": 8750.0
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "inserted_count": 1
}
```

#### `GET /api/trades`
Get all trades from the database.

**Query Parameters:**
- `limit` (optional): Maximum number of trades to return

**Response:**
```json
{
  "success": true,
  "trades": [...]
}
```

#### `GET /api/trades/latest`
Get the latest transaction (all trades with the same transaction_id).

**Response:**
```json
{
  "success": true,
  "trades": [...]
}
```

#### `GET /api/holdings`
Get current portfolio holdings.

**Response:**
```json
{
  "success": true,
  "holdings": {
    "TSLA": {
      "shares": 5.0,
      "price": 250.0,
      "value": 1250.0
    }
  },
  "cash": 8750.0
}
```

#### `GET /api/transaction-id`
Get the last transaction ID.

**Response:**
```json
{
  "success": true,
  "transaction_id": 1
}
```

### LLM Endpoints

#### `POST /mcp`
Send prompts to the LLM and handle legacy commands.

**Request:**
```json
{
  "prompt": "You are a financial strategist. List 5 promising stocks..."
}
```

**Response:**
```json
{
  "result": "{\"symbols\": [\"TSLA\", \"NVDA\", \"AAPL\", \"MSFT\", \"GOOGL\"]}"
}
```

### Legacy Endpoints

#### `GET /trades`
HTML view of all trades (for debugging).

**Response:** HTML page with trade visualization

## MCPClient Usage

### Basic Usage

```python
from utils.mcp_client import MCPClient

# Initialize client
mcp = MCPClient("http://localhost:11534")

# Save trades
result = mcp.save_trades(trades_list)

# Get trades
result = mcp.get_trades(limit=10)

# Get current holdings
result = mcp.get_current_holdings()

# Send LLM prompt
response = mcp.send("Generate a portfolio allocation...")
```

### Error Handling

```python
result = mcp.get_trades()
if result['success']:
    trades = result['trades']
    # Process trades
else:
    print(f"Error: {result['error']}")
```

## Configuration

### Environment Variables

```bash
# MCP Server
MCP_SERVER_PORT=11534
MCP_SERVER_HOST=0.0.0.0

# LLM Integration
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral

# Database
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB=trading_agent
```

### Server Startup

```python
# Direct startup
python utils/mcp_server.py

# Via system controller
python aitrading.py start
```

## Implementation Details

### Database Integration

The MCP server uses `TradeDatabase` class for all database operations:

```python
from utils.db_utils import TradeDatabase

db = TradeDatabase()
result = db.save_trades(trades)
```

### LLM Integration

LLM requests are forwarded to Ollama with response processing:

```python
payload = {
    'model': OLLAMA_MODEL,
    'prompt': prompt
}
response = requests.post(OLLAMA_URL, json=payload)
```

### Response Processing

The server extracts JSON from LLM responses using regex:

```python
match = re.search(r'\{.*\}', response_text, re.DOTALL)
if match:
    return match.group(0)
```

## Security Considerations

### Access Control
- Server runs on localhost by default
- No authentication required for local development
- Production deployment should add authentication

### Data Validation
- Input validation for all endpoints
- JSON schema validation for trade data
- Error handling for malformed requests

## Monitoring & Logging

### Log Files
- **Location**: `logging/mcp_server.log`
- **Format**: Timestamped INFO/ERROR messages
- **Rotation**: Daily rotation with 7-day retention

### Health Checks

```bash
# Server status
curl http://localhost:11534/api/trades

# Database connectivity
curl http://localhost:11534/api/holdings

# LLM connectivity
curl -X POST http://localhost:11534/mcp \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port 11534
lsof -i :11534
kill -9 <PID>
```

**Database Connection Errors**
```bash
# Check MongoDB status
mongosh --eval "db.runCommand('ping')"
```

**LLM Connection Errors**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags
```

### Debug Mode

Enable debug logging:
```bash
export DEBUG=1
python utils/mcp_server.py
```

## Development

### Adding New Endpoints

1. **Define route** in `mcp_server.py`:
```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    # Implementation
    return jsonify(result)
```

2. **Add client method** in `mcp_client.py`:
```python
def new_method(self, data):
    response = requests.post(f"{self.api_base}/new-endpoint", json=data)
    return response.json()
```

3. **Update documentation** and tests

### Testing

```python
# Unit tests
python -m pytest tests/test_mcp_server.py

# Integration tests
python tests/test_db_integration.py
```

## Performance Considerations

### Optimization Tips
- Use connection pooling for database
- Implement caching for frequent queries
- Add request rate limiting
- Monitor memory usage for large datasets

### Scaling
- Horizontal scaling with load balancer
- Database sharding for large datasets
- Microservice decomposition for complex workflows 