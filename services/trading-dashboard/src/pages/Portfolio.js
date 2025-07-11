import React, { useState } from 'react';
import styled from 'styled-components';
import { TrendingUp, TrendingDown, Search, Filter, Eye, MoreHorizontal } from 'lucide-react';
import { useTradingContext } from '../context/TradingContext';

const PortfolioContainer = styled.div`
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
`;

const SearchBox = styled.div`
  position: relative;
  flex: 1;
  max-width: 300px;
  
  .search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    width: 16px;
    height: 16px;
  }
  
  input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 0.875rem;
    
    &:focus {
      outline: none;
      border-color: var(--accent-blue);
    }
    
    &::placeholder {
      color: var(--text-muted);
    }
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
  
  .filter-icon {
    width: 16px;
    height: 16px;
  }
`;

const PositionsTable = styled.div`
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
`;

const TableHeader = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr auto;
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
    grid-template-columns: 1fr 1fr 1fr;
    .hide-mobile {
      display: none;
    }
  }
`;

const TableRow = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr auto;
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
    grid-template-columns: 1fr 1fr 1fr;
    .hide-mobile {
      display: none;
    }
  }
`;

const SymbolCell = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  
  .symbol-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--accent-blue);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
    color: white;
  }
  
  .symbol-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .symbol-name {
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .symbol-type {
    font-size: 0.75rem;
    color: var(--text-muted);
  }
`;

const PriceCell = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  
  .current-price {
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .price-change {
    font-size: 0.875rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    
    &.positive {
      color: var(--accent-green);
    }
    
    &.negative {
      color: var(--accent-red);
    }
    
    .change-icon {
      width: 12px;
      height: 12px;
    }
  }
`;

const AllocationCell = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  
  .allocation-percent {
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .allocation-bar {
    width: 100%;
    height: 4px;
    background: var(--bg-tertiary);
    border-radius: 2px;
    overflow: hidden;
    
    .allocation-fill {
      height: 100%;
      background: var(--accent-blue);
      transition: width 0.3s ease;
    }
  }
`;

const ValueCell = styled.div`
  font-weight: 600;
  color: var(--text-primary);
`;

const SentimentBadge = styled.div`
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  
  &.positive {
    background: rgba(0, 212, 170, 0.1);
    color: var(--accent-green);
  }
  
  &.negative {
    background: rgba(255, 107, 107, 0.1);
    color: var(--accent-red);
  }
  
  &.neutral {
    background: rgba(255, 212, 59, 0.1);
    color: var(--accent-yellow);
  }
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }
  
  .action-icon {
    width: 16px;
    height: 16px;
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

function Portfolio() {
  const { positions, loading } = useTradingContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const filteredPositions = positions.filter(position => {
    const matchesSearch = position.symbol.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || position.sentiment === filter;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <PortfolioContainer>
        <div className="spinner" />
      </PortfolioContainer>
    );
  }

  return (
    <PortfolioContainer>
      <PageHeader>
        <div>
          <div className="page-title">Portfolio</div>
          <div className="page-subtitle">Your current positions and holdings</div>
        </div>
      </PageHeader>

      <Controls>
        <SearchBox>
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search positions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </SearchBox>
        
        <FilterButton onClick={() => setFilter(filter === 'all' ? 'positive' : 'all')}>
          <Filter className="filter-icon" />
          {filter === 'all' ? 'All Positions' : 'Filtered'}
        </FilterButton>
      </Controls>

      <PositionsTable>
        <TableHeader>
          <div>Symbol</div>
          <div>Price</div>
          <div className="hide-mobile">Shares</div>
          <div>Allocation</div>
          <div className="hide-mobile">Value</div>
          <div className="hide-mobile">Sentiment</div>
          <div></div>
        </TableHeader>

        {filteredPositions.length === 0 ? (
          <EmptyState>
            <Eye className="empty-icon" />
            <div className="empty-title">No positions found</div>
            <div className="empty-description">
              {searchTerm ? 'Try adjusting your search terms' : 'Your portfolio positions will appear here'}
            </div>
          </EmptyState>
        ) : (
          filteredPositions.map((position, index) => (
            <TableRow key={index}>
              <SymbolCell>
                <div className="symbol-icon">
                  {position.symbol.substring(0, 2)}
                </div>
                <div className="symbol-info">
                  <div className="symbol-name">{position.symbol}</div>
                  <div className="symbol-type">
                    {position.symbol.includes('BTC') || position.symbol.includes('ETH') ? 'Crypto' : 'Stock'}
                  </div>
                </div>
              </SymbolCell>

              <PriceCell>
                <div className="current-price">{formatCurrency(position.currentPrice)}</div>
                <div className="price-change positive">
                  <TrendingUp className="change-icon" />
                  +2.5%
                </div>
              </PriceCell>

              <div className="hide-mobile">
                {position.shares.toFixed(4)}
              </div>

              <AllocationCell>
                <div className="allocation-percent">{position.allocation.toFixed(1)}%</div>
                <div className="allocation-bar">
                  <div 
                    className="allocation-fill" 
                    style={{ width: `${Math.min(position.allocation, 100)}%` }}
                  />
                </div>
              </AllocationCell>

              <ValueCell className="hide-mobile">
                {formatCurrency(position.value)}
              </ValueCell>

              <div className="hide-mobile">
                <SentimentBadge className={position.sentiment}>
                  {position.sentiment}
                </SentimentBadge>
              </div>

              <ActionButton>
                <MoreHorizontal className="action-icon" />
              </ActionButton>
            </TableRow>
          ))
        )}
      </PositionsTable>
    </PortfolioContainer>
  );
}

export default Portfolio; 