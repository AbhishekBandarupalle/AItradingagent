import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';

const TradingContext = createContext();

const initialState = {
  portfolio: {
    totalValue: 0,
    cash: 0,
    dayChange: 0,
    dayChangePercent: 0,
    totalReturn: 0,
    totalReturnPercent: 0
  },
  positions: [],
  trades: [],
  portfolioHistory: [],
  loading: false,
  error: null,
  connected: false
};

function tradingReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_PORTFOLIO':
      return { ...state, portfolio: action.payload };
    case 'SET_POSITIONS':
      return { ...state, positions: action.payload };
    case 'SET_TRADES':
      return { ...state, trades: action.payload };
    case 'SET_PORTFOLIO_HISTORY':
      return { ...state, portfolioHistory: action.payload };
    case 'SET_CONNECTED':
      return { ...state, connected: action.payload };
    case 'UPDATE_REAL_TIME':
      return {
        ...state,
        // Update real-time data when received via WebSocket
        trades: action.payload.trades || state.trades
      };
    default:
      return state;
  }
}

export function TradingProvider({ children }) {
  const [state, dispatch] = useReducer(tradingReducer, initialState);

  // API Functions
  const fetchPortfolioSummary = async () => {
    try {
      const response = await axios.get('/api/portfolio-summary');
      if (response.data.success) {
        dispatch({ type: 'SET_PORTFOLIO', payload: response.data.data });
      } else {
        dispatch({ type: 'SET_ERROR', payload: response.data.error });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchPositions = async () => {
    try {
      const response = await axios.get('/api/current-positions');
      if (response.data.success) {
        dispatch({ type: 'SET_POSITIONS', payload: response.data.data });
      } else {
        dispatch({ type: 'SET_ERROR', payload: response.data.error });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchTrades = async () => {
    try {
      const response = await axios.get('/api/trades');
      if (response.data.success) {
        dispatch({ type: 'SET_TRADES', payload: response.data.data.trades || [] });
      } else {
        dispatch({ type: 'SET_ERROR', payload: response.data.error });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchPortfolioHistory = async () => {
    try {
      const response = await axios.get('/api/portfolio-history');
      if (response.data.success) {
        dispatch({ type: 'SET_PORTFOLIO_HISTORY', payload: response.data.data });
      } else {
        dispatch({ type: 'SET_ERROR', payload: response.data.error });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const refreshAllData = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      await Promise.all([
        fetchPortfolioSummary(),
        fetchPositions(),
        fetchTrades(),
        fetchPortfolioHistory()
      ]);
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to refresh data' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // WebSocket connection
  useEffect(() => {
    const socket = io('http://localhost:3001');
    
    socket.on('connect', () => {
      dispatch({ type: 'SET_CONNECTED', payload: true });
      console.log('Connected to trading server');
    });

    socket.on('disconnect', () => {
      dispatch({ type: 'SET_CONNECTED', payload: false });
      console.log('Disconnected from trading server');
    });

    socket.on('portfolio-update', (data) => {
      dispatch({ type: 'UPDATE_REAL_TIME', payload: data });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Initial data fetch
  useEffect(() => {
    refreshAllData();
  }, []);

  // Periodic data refresh
  useEffect(() => {
    const interval = setInterval(() => {
      refreshAllData();
    }, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, []);

  const value = {
    ...state,
    refreshAllData,
    fetchPortfolioSummary,
    fetchPositions,
    fetchTrades,
    fetchPortfolioHistory
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
}

export function useTradingContext() {
  const context = useContext(TradingContext);
  if (!context) {
    throw new Error('useTradingContext must be used within a TradingProvider');
  }
  return context;
} 