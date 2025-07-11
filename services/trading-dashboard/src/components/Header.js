import React from 'react';
import styled from 'styled-components';
import { RefreshCw, Bell, User, TrendingUp, TrendingDown } from 'lucide-react';
import { useTradingContext } from '../context/TradingContext';

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const PortfolioSummary = styled.div`
  display: flex;
  align-items: center;
  gap: 2rem;
  
  @media (max-width: 768px) {
    gap: 1rem;
  }
`;

const MetricCard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  
  .metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .metric-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    
    @media (max-width: 768px) {
      font-size: 1rem;
    }
  }
  
  .metric-change {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    
    &.positive {
      color: var(--accent-green);
    }
    
    &.negative {
      color: var(--accent-red);
    }
    
    .change-icon {
      width: 14px;
      height: 14px;
    }
  }
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-card);
    color: var(--text-primary);
  }
  
  &.loading {
    animation: spin 1s linear infinite;
  }
  
  .icon {
    width: 20px;
    height: 20px;
  }
`;

const UserProfile = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-card);
  }
  
  .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--accent-blue);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 0.875rem;
  }
  
  .user-info {
    display: flex;
    flex-direction: column;
    
    .user-name {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--text-primary);
    }
    
    .user-role {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
  }
  
  @media (max-width: 768px) {
    .user-info {
      display: none;
    }
  }
`;

function Header() {
  const { portfolio, loading, refreshAllData } = useTradingContext();

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <HeaderContainer>
      <PortfolioSummary>
        <MetricCard>
          <div className="metric-label">Portfolio Value</div>
          <div className="metric-value">{formatCurrency(portfolio.totalValue)}</div>
          <div className={`metric-change ${portfolio.dayChangePercent >= 0 ? 'positive' : 'negative'}`}>
            {portfolio.dayChangePercent >= 0 ? (
              <TrendingUp className="change-icon" />
            ) : (
              <TrendingDown className="change-icon" />
            )}
            {formatPercent(portfolio.dayChangePercent)}
          </div>
        </MetricCard>
        
        <MetricCard>
          <div className="metric-label">Day Change</div>
          <div className="metric-value">{formatCurrency(portfolio.dayChange)}</div>
        </MetricCard>
        
        <MetricCard>
          <div className="metric-label">Cash Balance</div>
          <div className="metric-value">{formatCurrency(portfolio.cash)}</div>
        </MetricCard>
        
        <MetricCard>
          <div className="metric-label">Total Return</div>
          <div className="metric-value">{formatCurrency(portfolio.totalReturn)}</div>
          <div className={`metric-change ${portfolio.totalReturnPercent >= 0 ? 'positive' : 'negative'}`}>
            {portfolio.totalReturnPercent >= 0 ? (
              <TrendingUp className="change-icon" />
            ) : (
              <TrendingDown className="change-icon" />
            )}
            {formatPercent(portfolio.totalReturnPercent)}
          </div>
        </MetricCard>
      </PortfolioSummary>
      
      <HeaderActions>
        <ActionButton 
          onClick={refreshAllData} 
          className={loading ? 'loading' : ''}
          title="Refresh Data"
        >
          <RefreshCw className="icon" />
        </ActionButton>
        
        <ActionButton title="Notifications">
          <Bell className="icon" />
        </ActionButton>
        
        <UserProfile>
          <div className="avatar">
            <User size={16} />
          </div>
          <div className="user-info">
            <div className="user-name">AI Trader</div>
            <div className="user-role">Bot Account</div>
          </div>
        </UserProfile>
      </HeaderActions>
    </HeaderContainer>
  );
}

export default Header; 