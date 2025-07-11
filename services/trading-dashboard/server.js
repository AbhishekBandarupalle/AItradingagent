const express = require('express');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');
const axios = require('axios');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3001;
const MCP_SERVER_URL = 'http://localhost:11534';

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'build')));

// Helper function to fetch data from MCP server
async function fetchFromMCP(endpoint) {
  try {
    const response = await axios.get(`${MCP_SERVER_URL}${endpoint}`);
    return { success: true, data: response.data };
  } catch (error) {
    console.error(`Error fetching from MCP ${endpoint}:`, error.message);
    return { success: false, error: error.message };
  }
}

// API Routes
app.get('/api/trades', async (req, res) => {
  const result = await fetchFromMCP('/api/trades');
  res.json(result);
});

app.get('/api/holdings', async (req, res) => {
  const result = await fetchFromMCP('/api/holdings');
  res.json(result);
});

app.get('/api/portfolio-summary', async (req, res) => {
  try {
    const tradesResult = await fetchFromMCP('/api/trades');
    
    if (!tradesResult.success) {
      return res.json({ success: false, error: tradesResult.error });
    }

    const trades = tradesResult.data.trades || [];
    
    if (trades.length === 0) {
      return res.json({
        success: true,
        data: {
          totalValue: 0,
          cash: 0,
          dayChange: 0,
          dayChangePercent: 0,
          totalReturn: 0,
          totalReturnPercent: 0
        }
      });
    }

    // Get latest transaction data
    const latestTx = trades.reduce((latest, trade) => {
      return parseInt(trade.transaction_id) > parseInt(latest.transaction_id) ? trade : latest;
    });

    // Calculate portfolio metrics
    const portfolioValue = latestTx.portfolio_value || 0;
    const cash = latestTx.final_cash || 0;
    
    // Calculate day change (simplified - using last two transactions)
    const sortedTrades = trades.sort((a, b) => parseInt(b.transaction_id) - parseInt(a.transaction_id));
    const prevValue = sortedTrades.length > 1 ? sortedTrades[1].portfolio_value || 0 : portfolioValue;
    const dayChange = portfolioValue - prevValue;
    const dayChangePercent = prevValue > 0 ? (dayChange / prevValue) * 100 : 0;

    res.json({
      success: true,
      data: {
        totalValue: portfolioValue,
        cash: cash,
        dayChange: dayChange,
        dayChangePercent: dayChangePercent,
        totalReturn: portfolioValue - 10000, // Assuming $10k initial investment
        totalReturnPercent: ((portfolioValue - 10000) / 10000) * 100
      }
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.get('/api/portfolio-history', async (req, res) => {
  try {
    const tradesResult = await fetchFromMCP('/api/trades');
    
    if (!tradesResult.success) {
      return res.json({ success: false, error: tradesResult.error });
    }

    const trades = tradesResult.data.trades || [];
    
    // Group by transaction_id and get portfolio value over time
    const txGroups = {};
    trades.forEach(trade => {
      const txId = trade.transaction_id;
      if (!txGroups[txId]) {
        txGroups[txId] = {
          transaction_id: txId,
          date: trade.date,
          time: trade.time,
          portfolio_value: trade.portfolio_value || 0,
          final_cash: trade.final_cash || 0
        };
      }
    });

    const history = Object.values(txGroups)
      .sort((a, b) => parseInt(a.transaction_id) - parseInt(b.transaction_id))
      .map(tx => ({
        timestamp: `${tx.date} ${tx.time}`,
        value: tx.portfolio_value,
        cash: tx.final_cash
      }));

    res.json({ success: true, data: history });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.get('/api/current-positions', async (req, res) => {
  try {
    const tradesResult = await fetchFromMCP('/api/trades');
    
    if (!tradesResult.success) {
      return res.json({ success: false, error: tradesResult.error });
    }

    const trades = tradesResult.data.trades || [];
    
    if (trades.length === 0) {
      return res.json({ success: true, data: [] });
    }

    // Get latest transaction positions
    const latestTxId = Math.max(...trades.map(t => parseInt(t.transaction_id)));
    const latestPositions = trades
      .filter(t => parseInt(t.transaction_id) === latestTxId && t.shares_held > 0)
      .map(trade => ({
        symbol: trade.symbol,
        shares: trade.shares_held,
        currentPrice: trade.current_price,
        allocation: trade.allocation * 100,
        value: trade.shares_held * trade.current_price,
        sentiment: trade.sentiment || 'neutral'
      }));

    res.json({ success: true, data: latestPositions });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

// WebSocket connection for real-time updates
io.on('connection', (socket) => {
  console.log('Client connected');
  
  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

// Broadcast updates every 30 seconds
setInterval(async () => {
  try {
    const summary = await fetchFromMCP('/api/trades');
    if (summary.success) {
      io.emit('portfolio-update', summary.data);
    }
  } catch (error) {
    console.error('Error broadcasting update:', error);
  }
}, 30000);

// Catch all handler for React Router
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

server.listen(PORT, () => {
  console.log(`🚀 Trading Dashboard Server running on port ${PORT}`);
  console.log(`📊 Dashboard available at http://localhost:${PORT}`);
}); 