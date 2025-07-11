import React, { useState } from 'react';
import styled from 'styled-components';
import { Calendar, Filter, Download, TrendingUp, TrendingDown, Activity, Clock } from 'lucide-react';
import { useTradingContext } from '../context/TradingContext';

const TradingContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const PageHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: between;
  gap: 1rem;
  
  .page-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
  }
  
  .page-subtitle {
    color: var(--text-muted);
    font-size: 1rem;
  }
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    flex-wrap: wrap;
  }
`;

const FilterButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-tertiary);
    border-color: #444;
  }
  
  &.active {
    background: var(--accent-blue);
    color: white;
    border-color: var(--accent-blue);
  }
  
  .filter-icon {
    width: 16px;
    height: 16px;
  }
`;

const StatsRow = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  
  .stat-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .stat-icon {
    width: 20px;
    height: 20px;
    color: var(--accent-blue);
  }
  
  .stat-title {
    font-size: 0.875rem;
    color: var(--text-muted);
    font-weight: 500;
  }
  
  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
  }
`;

const TradesTable = styled.div`
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
`;

const TableHeader = styled.div`
  display: grid;
  grid-template-columns: auto 1fr 1fr 1fr 1fr 1fr 1fr;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  
  @media (max-width: 768px) {
    grid-template-columns: auto 1fr 1fr 1fr;
    .hide-mobile {
      display: none;
    }
  }
`;

const TableRow = styled.div`
  display: grid;
  grid-template-columns: auto 1fr 1fr 1fr 1fr 1fr 1fr;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s ease;
  
  &:hover {
    background: var(--bg-secondary);
  }
  
  &:last-child {
    border-bottom: none;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: auto 1fr 1fr 1fr;
    .hide-mobile {
      display: none;
    }
  }
`;

const ActionBadge = styled.div`
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  
  &.buy {
    background: rgba(0, 212, 170, 0.1);
    color: var(--accent-green);
  }
  
  &.sell {
    background: rgba(255, 107, 107, 0.1);
    color: var(--accent-red);
  }
  
  &.hold {
    background: rgba(255, 212, 59, 0.1);
    color: var(--accent-yellow);
  }
`;

const SymbolCell = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  .symbol-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--accent-blue);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.75rem;
    color: white;
  }
  
  .symbol-name {
    font-weight: 600;
    color: var(--text-primary);
  }
`;

const TimeCell = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  
  .date {
    font-weight: 500;
    color: var(--text-primary);
  }
  
  .time {
    font-size: 0.875rem;
    color: var(--text-muted);
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  
  .empty-icon {
    width: 64px;
    height: 64px;
    color: var(--text-muted);
    margin-bottom: 1rem;
  }
  
  .empty-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
  }
  
  .empty-description {
    color: var(--text-muted);
    font-size: 0.875rem;
  }
`;

function Trading() {
  const { trades, loading } = useTradingContext();
  const [filter, setFilter] = useState('all');

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  // Group trades by transaction_id and calculate buy/sell actions
  const processedTrades = React.useMemo(() => {
    const txGroups = {};
    trades.forEach(trade => {
      const txId = trade.transaction_id;
      if (!txGroups[txId]) {
        txGroups[txId] = [];
      }
      txGroups[txId].push(trade);
    });

    const processed = [];
    const sortedTxIds = Object.keys(txGroups).sort((a, b) => parseInt(b) - parseInt(a));
    
    let prevTx = null;
    for (const txId of sortedTxIds) {
      const currentTx = txGroups[txId];
      
      if (prevTx) {
        // Compare with previous transaction to determine actions
        const prevMap = {};
        prevTx.forEach(trade => {
          prevMap[trade.symbol] = trade.allocation;
        });
        
        currentTx.forEach(trade => {
          const prevAlloc = prevMap[trade.symbol] || 0;
          const currentAlloc = trade.allocation;
          const allocDiff = currentAlloc - prevAlloc;
          
          let action = 'hold';
          if (allocDiff > 0.01) action = 'buy';
          else if (allocDiff < -0.01) action = 'sell';
          
          processed.push({
            ...trade,
            action,
            allocChange: allocDiff
          });
        });
      } else {
        // First transaction - all are buys
        currentTx.forEach(trade => {
          processed.push({
            ...trade,
            action: 'buy',
            allocChange: trade.allocation
          });
        });
      }
      
      prevTx = currentTx;
    }
    
    return processed;
  }, [trades]);

  const filteredTrades = processedTrades.filter(trade => {
    if (filter === 'all') return true;
    return trade.action === filter;
  });

  // Calculate stats
  const totalTrades = processedTrades.length;
  const buyTrades = processedTrades.filter(t => t.action === 'buy').length;
  const sellTrades = processedTrades.filter(t => t.action === 'sell').length;
  const totalVolume = processedTrades.reduce((sum, trade) => sum + Math.abs(trade.amount), 0);

  if (loading) {
    return (
      <TradingContainer>
        <div className="spinner" />
      </TradingContainer>
    );
  }

  return (
    <TradingContainer>
      <PageHeader>
        <div>
          <div className="page-title">Trading Activity</div>
          <div className="page-subtitle">Your complete trading history and performance</div>
        </div>
      </PageHeader>

      <StatsRow>
        <StatCard>
          <div className="stat-header">
            <Activity className="stat-icon" />
            <div className="stat-title">Total Trades</div>
          </div>
          <div className="stat-value">{totalTrades}</div>
        </StatCard>

        <StatCard>
          <div className="stat-header">
            <TrendingUp className="stat-icon" />
            <div className="stat-title">Buy Orders</div>
          </div>
          <div className="stat-value">{buyTrades}</div>
        </StatCard>

        <StatCard>
          <div className="stat-header">
            <TrendingDown className="stat-icon" />
            <div className="stat-title">Sell Orders</div>
          </div>
          <div className="stat-value">{sellTrades}</div>
        </StatCard>

        <StatCard>
          <div className="stat-header">
            <Activity className="stat-icon" />
            <div className="stat-title">Total Volume</div>
          </div>
          <div className="stat-value">{formatCurrency(totalVolume)}</div>
        </StatCard>
      </StatsRow>

      <Controls>
        <FilterButton 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          <Filter className="filter-icon" />
          All Trades
        </FilterButton>
        
        <FilterButton 
          className={filter === 'buy' ? 'active' : ''}
          onClick={() => setFilter('buy')}
        >
          <TrendingUp className="filter-icon" />
          Buy Orders
        </FilterButton>
        
        <FilterButton 
          className={filter === 'sell' ? 'active' : ''}
          onClick={() => setFilter('sell')}
        >
          <TrendingDown className="filter-icon" />
          Sell Orders
        </FilterButton>
        
        <FilterButton>
          <Download className="filter-icon" />
          Export
        </FilterButton>
      </Controls>

      <TradesTable>
        <TableHeader>
          <div>Action</div>
          <div>Symbol</div>
          <div>Price</div>
          <div className="hide-mobile">Shares</div>
          <div className="hide-mobile">Amount</div>
          <div className="hide-mobile">Allocation</div>
          <div>Date/Time</div>
        </TableHeader>

        {filteredTrades.length === 0 ? (
          <EmptyState>
            <Activity className="empty-icon" />
            <div className="empty-title">No trades found</div>
            <div className="empty-description">
              Your trading activity will appear here
            </div>
          </EmptyState>
        ) : (
          filteredTrades.map((trade, index) => (
            <TableRow key={index}>
              <ActionBadge className={trade.action}>
                {trade.action}
              </ActionBadge>

              <SymbolCell>
                <div className="symbol-icon">
                  {trade.symbol.substring(0, 2)}
                </div>
                <div className="symbol-name">{trade.symbol}</div>
              </SymbolCell>

              <div>{formatCurrency(trade.current_price)}</div>

              <div className="hide-mobile">
                {trade.shares_held?.toFixed(4) || '0.0000'}
              </div>

              <div className="hide-mobile">
                {formatCurrency(Math.abs(trade.amount))}
              </div>

              <div className="hide-mobile">
                {(trade.allocation * 100).toFixed(1)}%
              </div>

              <TimeCell>
                <div className="date">{trade.date}</div>
                <div className="time">{trade.time}</div>
              </TimeCell>
            </TableRow>
          ))
        )}
      </TradesTable>
    </TradingContainer>
  );
}

export default Trading; 