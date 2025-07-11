# Database Guide 🗄️

## Overview

The AI Trading Agent System uses MongoDB as its primary database for storing trade data, portfolio information, and system metadata. This guide covers setup, configuration, schema design, and operations.

## MongoDB Setup

### Installation

#### macOS (Homebrew)
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Verify installation
mongosh --eval "db.runCommand('ping')"
```

#### RHEL/Fedora
```bash
sudo dnf install -y mongodb mongodb-server
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
mongosh --eval "db.runCommand('ping')"
```

#### Windows
1. Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Run installer with default settings
3. Start MongoDB service from Services panel

### Configuration

#### Default Configuration
- **Host**: `localhost`
- **Port**: `27017`
- **Database**: `trading_agent`
- **Collections**: `trades`, `portfolio`

#### Custom Configuration
```bash
# Environment variables
export MONGODB_URL="mongodb://localhost:27017/"
export MONGODB_DB="trading_agent"

# Custom host/port
export MONGODB_URL="mongodb://custom-host:27018/"
```

## Database Schema

### Trades Collection

The primary collection storing all trading transactions:

```javascript
{
  "_id": ObjectId("..."),                    // MongoDB auto-generated ID
  "transaction_id": "00001",                 // Sequential transaction ID
  "time": "14:30:00",                        // Time of trade (HH:MM:SS)
  "date": "10-07-25",                        // Date of trade (DD-MM-YY)
  "symbol": "TSLA",                          // Stock/crypto symbol
  "action": "Buy",                           // Trade action: Buy/Sell/Hold
  "shares_changed": 5.0,                     // Number of shares bought/sold
  "shares_held": 5.0,                        // Total shares held after trade
  "current_price": 250.0,                    // Price per share at time of trade
  "amount": 1250.0,                          // Total trade amount (shares * price)
  "allocation": 0.125,                       // Portfolio allocation percentage (0-1)
  "cash": 8750.0,                           // Remaining cash after trade
  "sentiment": 1.2,                          // Current sentiment score
  "last_sentiment": 1.0,                     // Previous sentiment score
  "portfolio_value": 10000.0,               // Total portfolio value
  "final_cash": 8750.0                      // Final cash amount
}
```

### Indexes

Recommended indexes for optimal performance:

```javascript
// Transaction ID index (for latest transaction queries)
db.trades.createIndex({ "transaction_id": -1 })

// Date/Time index (for chronological queries)
db.trades.createIndex({ "date": -1, "time": -1 })

// Symbol index (for symbol-specific queries)
db.trades.createIndex({ "symbol": 1 })

// Composite index for portfolio queries
db.trades.createIndex({ "transaction_id": -1, "symbol": 1 })
```

## Database Operations

### TradeDatabase Class

The `TradeDatabase` class provides all database operations:

```python
from utils.db_utils import TradeDatabase

# Initialize connection
db = TradeDatabase()

# Save trades
trades = [{"transaction_id": "00001", ...}]
result = db.save_trades(trades)

# Get all trades
result = db.get_all_trades()

# Get latest transaction
result = db.get_latest_transaction()

# Get current holdings
result = db.get_current_holdings()

# Get last transaction ID
result = db.get_last_transaction_id()

# Close connection
db.close()
```

### Common Operations

#### Inserting Trades
```python
# Single trade
trade = {
    "transaction_id": "00001",
    "symbol": "TSLA",
    "action": "Buy",
    # ... other fields
}
result = db.save_trades([trade])

# Multiple trades (transaction)
trades = [
    {"transaction_id": "00001", "symbol": "TSLA", ...},
    {"transaction_id": "00001", "symbol": "NVDA", ...},
]
result = db.save_trades(trades)
```

#### Querying Trades
```python
# All trades (sorted by date/time)
result = db.get_all_trades()
trades = result['trades']

# Latest N trades
result = db.get_latest_trades(limit=10)

# Latest complete transaction
result = db.get_latest_transaction()
```

#### Portfolio Operations
```python
# Current holdings
result = db.get_current_holdings()
holdings = result['holdings']  # {symbol: {shares, price, value}}
cash = result['cash']

# Last transaction ID
result = db.get_last_transaction_id()
last_id = result['transaction_id']
```

## Data Migration

### From JSON Files

If migrating from the old JSON-based system:

```python
# Migration script
from utils.db_utils import TradeDatabase
from utils.trade_log_utils import load_trade_log
import json

def migrate_json_to_mongodb():
    # Load existing JSON data
    try:
        with open('trade_log.json', 'r') as f:
            data = json.load(f)
        trades = data.get('trades', [])
    except FileNotFoundError:
        print("No JSON file found")
        return
    
    # Save to MongoDB
    db = TradeDatabase()
    result = db.save_trades(trades)
    
    if result['success']:
        print(f"Migrated {result['inserted_count']} trades to MongoDB")
    else:
        print(f"Migration failed: {result['error']}")
    
    db.close()

# Run migration
migrate_json_to_mongodb()
```

### Backup and Restore

#### Creating Backups
```bash
# Full database backup
mongodump --db trading_agent --out backup/

# Specific collection backup
mongodump --db trading_agent --collection trades --out backup/

# Compressed backup
mongodump --db trading_agent --gzip --out backup/
```

#### Restoring Backups
```bash
# Full database restore
mongorestore --db trading_agent backup/trading_agent/

# Specific collection restore
mongorestore --db trading_agent --collection trades backup/trading_agent/trades.bson

# Drop existing data before restore
mongorestore --db trading_agent --drop backup/trading_agent/
```

## Performance Optimization

### Query Optimization

#### Efficient Queries
```python
# Good: Use indexes
db.trades.find({"transaction_id": "00001"})

# Good: Limit results
db.trades.find().sort({"date": -1}).limit(10)

# Avoid: Full collection scans
db.trades.find({"amount": {"$gt": 1000}})  # Without index
```

#### Aggregation Pipelines
```python
# Portfolio summary by symbol
pipeline = [
    {"$match": {"transaction_id": "00001"}},
    {"$group": {
        "_id": "$symbol",
        "total_shares": {"$sum": "$shares_held"},
        "total_value": {"$sum": "$amount"}
    }}
]
result = db.trades.aggregate(pipeline)
```

### Connection Management

#### Connection Pooling
```python
from pymongo import MongoClient

# Configure connection pool
client = MongoClient(
    'mongodb://localhost:27017/',
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000
)
```

#### Connection Best Practices
- Reuse connections across operations
- Close connections properly
- Handle connection errors gracefully
- Use connection timeouts

## Monitoring

### Database Statistics
```bash
# Database size and stats
mongosh trading_agent --eval "db.stats()"

# Collection statistics
mongosh trading_agent --eval "db.trades.stats()"

# Index usage statistics
mongosh trading_agent --eval "db.trades.getIndexes()"
```

### Performance Monitoring
```bash
# Current operations
mongosh --eval "db.currentOp()"

# Slow query profiling
mongosh trading_agent --eval "db.setProfilingLevel(2, {slowms: 100})"
mongosh trading_agent --eval "db.system.profile.find().pretty()"
```

## Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check port availability
netstat -tlnp | grep 27017

# Check MongoDB logs
tail -f /var/log/mongodb/mongod.log
```

#### Database Access Issues
```python
# Test connection
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.trading_agent
    result = db.command('ping')
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

#### Performance Issues
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check MongoDB memory usage
mongosh --eval "db.serverStatus().mem"
```

### Error Resolution

#### Duplicate Key Errors
```python
# Handle duplicate insertions
try:
    result = db.save_trades(trades)
except pymongo.errors.DuplicateKeyError:
    print("Trade already exists")
```

#### Timeout Errors
```python
# Increase timeout
client = MongoClient(
    'mongodb://localhost:27017/',
    serverSelectionTimeoutMS=5000,
    socketTimeoutMS=5000
)
```

## Security

### Access Control

#### Enable Authentication
```bash
# Start MongoDB with auth
mongod --auth --dbpath /data/db

# Create admin user
mongosh admin --eval "
db.createUser({
  user: 'admin',
  pwd: 'password',
  roles: ['userAdminAnyDatabase']
})
"
```

#### Application User
```bash
# Create application-specific user
mongosh trading_agent --eval "
db.createUser({
  user: 'trading_app',
  pwd: 'app_password',
  roles: ['readWrite']
})
"
```

### Network Security
- Bind to localhost only for development
- Use TLS/SSL for production
- Configure firewall rules
- Use VPN for remote access

## Maintenance

### Regular Tasks

#### Data Cleanup
```python
# Remove old test data
db.trades.deleteMany({"transaction_id": "99999"})

# Archive old trades (older than 1 year)
cutoff_date = datetime.now() - timedelta(days=365)
# Implementation depends on date format
```

#### Index Maintenance
```bash
# Rebuild indexes
mongosh trading_agent --eval "db.trades.reIndex()"

# Check index usage
mongosh trading_agent --eval "db.trades.aggregate([{$indexStats: {}}])"
```

#### Health Checks
```python
# Automated health check script
def check_database_health():
    try:
        db = TradeDatabase()
        
        # Test connection
        result = db.get_last_transaction_id()
        assert result['success']
        
        # Test write operation
        test_trade = {"transaction_id": "99999", "symbol": "TEST", ...}
        result = db.save_trades([test_trade])
        assert result['success']
        
        # Cleanup test data
        db.trades_collection.delete_many({"transaction_id": "99999"})
        
        print("Database health check: PASSED")
        return True
        
    except Exception as e:
        print(f"Database health check: FAILED - {e}")
        return False
```

## Development

### Local Development Setup
```bash
# Start MongoDB for development
brew services start mongodb-community

# Create development database
mongosh trading_agent --eval "db.createCollection('trades')"

# Load sample data
python scripts/load_sample_data.py
```

### Testing
```python
# Unit tests for database operations
import pytest
from utils.db_utils import TradeDatabase

def test_save_trades():
    db = TradeDatabase("mongodb://localhost:27017/", "test_db")
    trades = [{"transaction_id": "00001", ...}]
    result = db.save_trades(trades)
    assert result['success']
    assert result['inserted_count'] == 1
```

### Production Deployment
- Use replica sets for high availability
- Configure proper backup schedules
- Monitor performance metrics
- Set up alerting for failures 