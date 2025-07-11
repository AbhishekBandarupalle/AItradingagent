# API Reference 📚

## Overview

The AI Trading Agent System provides a RESTful API through the MCP (Model Context Protocol) server. This reference documents all available endpoints, request/response formats, and usage examples.

**Base URL**: `http://localhost:11534`

## Authentication

Currently, no authentication is required for local development. All endpoints are accessible without credentials.

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true|false,
  "data": {...},           // Present on success
  "error": "error message" // Present on failure
}
```

## Endpoints

### Database Operations

#### Save Trades
Save one or more trades to the database.

**Endpoint**: `POST /api/trades`

**Request Body**:
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

**Response**:
```json
{
  "success": true,
  "inserted_count": 1
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Invalid trade data format"
}
```

**Example**:
```bash
curl -X POST http://localhost:11534/api/trades \
  -H "Content-Type: application/json" \
  -d '{"trades": [{"transaction_id": "00001", "symbol": "TSLA", ...}]}'
```

---

#### Get All Trades
Retrieve all trades from the database.

**Endpoint**: `GET /api/trades`

**Query Parameters**:
- `limit` (optional): Maximum number of trades to return

**Response**:
```json
{
  "success": true,
  "trades": [
    {
      "transaction_id": "00001",
      "time": "14:30:00",
      "date": "10-07-25",
      "symbol": "TSLA",
      "action": "Buy",
      // ... full trade object
    }
  ]
}
```

**Examples**:
```bash
# Get all trades
curl http://localhost:11534/api/trades

# Get latest 10 trades
curl "http://localhost:11534/api/trades?limit=10"
```

---

#### Get Latest Transaction
Retrieve all trades from the most recent transaction.

**Endpoint**: `GET /api/trades/latest`

**Response**:
```json
{
  "success": true,
  "trades": [
    {
      "transaction_id": "00001",
      "symbol": "TSLA",
      // ... trade data
    },
    {
      "transaction_id": "00001",
      "symbol": "NVDA",
      // ... trade data
    }
  ]
}
```

**Example**:
```bash
curl http://localhost:11534/api/trades/latest
```

---

#### Get Current Holdings
Retrieve current portfolio holdings and cash balance.

**Endpoint**: `GET /api/holdings`

**Response**:
```json
{
  "success": true,
  "holdings": {
    "TSLA": {
      "shares": 5.0,
      "price": 250.0,
      "value": 1250.0
    },
    "NVDA": {
      "shares": 3.0,
      "price": 400.0,
      "value": 1200.0
    }
  },
  "cash": 8750.0
}
```

**Example**:
```bash
curl http://localhost:11534/api/holdings
```

---

#### Get Last Transaction ID
Retrieve the ID of the most recent transaction.

**Endpoint**: `GET /api/transaction-id`

**Response**:
```json
{
  "success": true,
  "transaction_id": 1
}
```

**Example**:
```bash
curl http://localhost:11534/api/transaction-id
```

---

### LLM Operations

#### Send LLM Prompt
Send a prompt to the local LLM for processing.

**Endpoint**: `POST /mcp`

**Request Body**:
```json
{
  "prompt": "You are a financial strategist. List 5 promising stocks for trading."
}
```

**Response**:
```json
{
  "result": "{\"symbols\": [\"TSLA\", \"NVDA\", \"AAPL\", \"MSFT\", \"GOOGL\"]}"
}
```

**Error Response**:
```json
{
  "result": "llm error"
}
```

**Example**:
```bash
curl -X POST http://localhost:11534/mcp \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Generate a portfolio allocation as JSON"}'
```

---

### Legacy Operations

#### Record Trades (Legacy)
Legacy endpoint for recording trades via prompt.

**Endpoint**: `POST /mcp`

**Request Body**:
```json
{
  "prompt": "RECORD_TRADES:[{\"transaction_id\": \"00001\", ...}]"
}
```

**Response**:
```json
{
  "result": "trades recorded (database)"
}
```

---

#### Get Latest Trades (Legacy)
Legacy endpoint for retrieving trades via prompt.

**Endpoint**: `POST /mcp`

**Request Body**:
```json
{
  "prompt": "GET_LATEST_TRADES"
}
```

**Response**:
```json
{
  "result": "[{\"transaction_id\": \"00001\", ...}]"
}
```

---

#### Mark Trades Verified (Legacy)
Legacy endpoint for marking trades as verified.

**Endpoint**: `POST /mcp`

**Request Body**:
```json
{
  "prompt": "MARK_TRADES_VERIFIED:00001"
}
```

**Response**:
```json
{
  "result": "trades marked as verified"
}
```

---

### Utility Endpoints

#### View Trades (HTML)
Web interface for viewing trades.

**Endpoint**: `GET /trades`

**Response**: HTML page with trade visualization

**Example**:
```bash
# Open in browser
open http://localhost:11534/trades
```

---

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request format
- `500 Internal Server Error`: Server error

### Application Error Messages

- `"Invalid trade data format"`: Trade object missing required fields
- `"llm error"`: LLM request failed or returned invalid response
- `"No JSON object found in LLM output"`: LLM response couldn't be parsed
- `"Database connection failed"`: MongoDB connection error

## Data Types

### Trade Object

```typescript
interface Trade {
  transaction_id: string;      // Sequential ID (e.g., "00001")
  time: string;               // Time in HH:MM:SS format
  date: string;               // Date in DD-MM-YY format
  symbol: string;             // Stock/crypto symbol
  action: "Buy" | "Sell" | "Hold";
  shares_changed: number;     // Number of shares bought/sold
  shares_held: number;        // Total shares held after trade
  current_price: number;      // Price per share
  amount: number;            // Total trade amount
  allocation: number;        // Portfolio allocation (0-1)
  cash: number;              // Remaining cash
  sentiment: number;         // Current sentiment score
  last_sentiment: number;    // Previous sentiment score
  portfolio_value: number;   // Total portfolio value
  final_cash: number;        // Final cash amount
}
```

### Holdings Object

```typescript
interface Holdings {
  [symbol: string]: {
    shares: number;     // Number of shares held
    price: number;      // Current price per share
    value: number;      // Total value (shares * price)
  }
}
```

## Usage Examples

### Python Client

```python
import requests
import json

class TradingAPIClient:
    def __init__(self, base_url="http://localhost:11534"):
        self.base_url = base_url
    
    def save_trades(self, trades):
        response = requests.post(
            f"{self.base_url}/api/trades",
            json={"trades": trades}
        )
        return response.json()
    
    def get_holdings(self):
        response = requests.get(f"{self.base_url}/api/holdings")
        return response.json()
    
    def send_llm_prompt(self, prompt):
        response = requests.post(
            f"{self.base_url}/mcp",
            json={"prompt": prompt}
        )
        return response.json()

# Usage
client = TradingAPIClient()

# Save a trade
trade = {
    "transaction_id": "00001",
    "symbol": "TSLA",
    "action": "Buy",
    # ... other fields
}
result = client.save_trades([trade])

# Get current holdings
holdings = client.get_holdings()

# Send LLM prompt
response = client.send_llm_prompt("Generate portfolio allocation")
```

### JavaScript Client

```javascript
class TradingAPIClient {
    constructor(baseUrl = 'http://localhost:11534') {
        this.baseUrl = baseUrl;
    }
    
    async saveTrades(trades) {
        const response = await fetch(`${this.baseUrl}/api/trades`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ trades })
        });
        return response.json();
    }
    
    async getHoldings() {
        const response = await fetch(`${this.baseUrl}/api/holdings`);
        return response.json();
    }
    
    async sendLLMPrompt(prompt) {
        const response = await fetch(`${this.baseUrl}/mcp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });
        return response.json();
    }
}

// Usage
const client = new TradingAPIClient();

// Get holdings
client.getHoldings()
    .then(result => {
        if (result.success) {
            console.log('Holdings:', result.holdings);
            console.log('Cash:', result.cash);
        }
    });
```

### cURL Examples

```bash
# Save trades
curl -X POST http://localhost:11534/api/trades \
  -H "Content-Type: application/json" \
  -d '{
    "trades": [{
      "transaction_id": "00001",
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
      "final_cash": 8750.0,
      "time": "14:30:00",
      "date": "10-07-25"
    }]
  }'

# Get latest 5 trades
curl "http://localhost:11534/api/trades?limit=5"

# Get current holdings
curl http://localhost:11534/api/holdings

# Send LLM prompt
curl -X POST http://localhost:11534/mcp \
  -H "Content-Type: application/json" \
  -d '{"prompt": "You are a financial strategist. Recommend 5 stocks as JSON."}'
```

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing:

- Request rate limiting (e.g., 100 requests/minute)
- Concurrent connection limits
- Request size limits
- Timeout configurations

## Versioning

The API is currently unversioned. Future versions will use URL versioning:

- `/api/v1/trades` (future)
- `/api/v2/trades` (future)

## Support

For API support and issues:

1. Check server logs: `tail -f logging/mcp_server.log`
2. Verify MongoDB connection: `mongosh --eval "db.runCommand('ping')"`
3. Test LLM connectivity: `curl http://localhost:11434/api/tags`
4. Run integration tests: `python tests/test_db_integration.py` 