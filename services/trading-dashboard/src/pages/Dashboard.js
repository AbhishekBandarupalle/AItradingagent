import React from 'react';
import styled from 'styled-components';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { TrendingUp, TrendingDown, Activity, DollarSign, PieChart as PieChartIcon, BarChart3 } from 'lucide-react';
import { useTradingContext } from '../context/TradingContext';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #444;
    transform: translateY(-2px);
  }
  
  .stat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
  }
  
  .stat-title {
    font-size: 0.875rem;
    color: var(--text-muted);
    font-weight: 500;
  }
  
  .stat-icon {
    width: 20px;
    height: 20px;
    color: var(--accent-blue);
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
  }
  
  .stat-change {
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

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  
  .chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
  }
  
  .chart-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .chart-subtitle {
    font-size: 0.875rem;
    color: var(--text-muted);
  }
`;

const RecentActivity = styled.div`
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  
  .activity-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  
  .activity-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .activity-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: 8px;
    border: 1px solid var(--border-color);
  }
  
  .activity-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
  }
  
  .activity-details {
    flex: 1;
  }
  
  .activity-action {
    font-weight: 500;
    color: var(--text-primary);
  }
  
  .activity-time {
    font-size: 0.875rem;
    color: var(--text-muted);
  }
  
  .activity-amount {
    font-weight: 600;
    
    &.positive {
      color: var(--accent-green);
    }
    
    &.negative {
      color: var(--accent-red);
    }
  }
`;

const COLORS = ['#4dabf7', '#00d4aa', '#ff6b6b', '#ffd43b', '#9775fa', '#fd7e14'];

function Dashboard() {
  const { portfolio, portfolioHistory, positions, trades, loading } = useTradingContext();

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

  // Prepare chart data
  const chartData = portfolioHistory.map(item => ({
    time: new Date(item.timestamp).toLocaleDateString(),
    value: item.value,
    cash: item.cash
  }));

  const pieData = positions.map(position => ({
    name: position.symbol,
    value: position.value,
    allocation: position.allocation
  }));

  // Get recent trades for activity
  const recentTrades = trades
    .sort((a, b) => parseInt(b.transaction_id) - parseInt(a.transaction_id))
    .slice(0, 5);

  if (loading) {
    return (
      <DashboardContainer>
        <div className="spinner" />
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <StatsGrid>
        <StatCard>
          <div className="stat-header">
            <div className="stat-title">Portfolio Value</div>
            <DollarSign className="stat-icon" />
          </div>
          <div className="stat-value">{formatCurrency(portfolio.totalValue)}</div>
          <div className={`stat-change ${portfolio.dayChangePercent >= 0 ? 'positive' : 'negative'}`}>
            {portfolio.dayChangePercent >= 0 ? (
              <TrendingUp className="change-icon" />
            ) : (
              <TrendingDown className="change-icon" />
            )}
            {formatPercent(portfolio.dayChangePercent)}
          </div>
        </StatCard>

        <StatCard>
          <div className="stat-header">
            <div className="stat-title">Day Change</div>
            <Activity className="stat-icon" />
          </div>
          <div className="stat-value">{formatCurrency(portfolio.dayChange)}</div>
          <div className={`stat-change ${portfolio.dayChange >= 0 ? 'positive' : 'negative'}`}>
            {portfolio.dayChange >= 0 ? (
              <TrendingUp className="change-icon" />
            ) : (
              <TrendingDown className="change-icon" />
            )}
            Today
          </div>
        </StatCard>

        <StatCard>
          <div className="stat-header">
            <div className="stat-title">Cash Balance</div>
            <DollarSign className="stat-icon" />
          </div>
          <div className="stat-value">{formatCurrency(portfolio.cash)}</div>
          <div className="stat-change">
            Available for trading
          </div>
        </StatCard>

        <StatCard>
          <div className="stat-header">
            <div className="stat-title">Total Return</div>
            <BarChart3 className="stat-icon" />
          </div>
          <div className="stat-value">{formatCurrency(portfolio.totalReturn)}</div>
          <div className={`stat-change ${portfolio.totalReturnPercent >= 0 ? 'positive' : 'negative'}`}>
            {portfolio.totalReturnPercent >= 0 ? (
              <TrendingUp className="change-icon" />
            ) : (
              <TrendingDown className="change-icon" />
            )}
            {formatPercent(portfolio.totalReturnPercent)}
          </div>
        </StatCard>
      </StatsGrid>

      <ChartsGrid>
        <ChartCard>
          <div className="chart-header">
            <div>
              <div className="chart-title">Portfolio Performance</div>
              <div className="chart-subtitle">Value over time</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'var(--bg-card)', 
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#4dabf7" 
                fill="rgba(77, 171, 247, 0.1)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <div className="chart-header">
            <div>
              <div className="chart-title">Asset Allocation</div>
              <div className="chart-subtitle">Current positions</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, allocation }) => `${name} ${allocation.toFixed(1)}%`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => [formatCurrency(value), 'Value']}
                contentStyle={{ 
                  backgroundColor: 'var(--bg-card)', 
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </ChartsGrid>

      <RecentActivity>
        <div className="activity-header">
          <Activity size={20} />
          <div className="activity-title">Recent Trading Activity</div>
        </div>
        <div className="activity-list">
          {recentTrades.map((trade, index) => (
            <div key={index} className="activity-item">
              <div 
                className="activity-icon"
                style={{ 
                  backgroundColor: trade.action === 'buy' ? 'var(--accent-green)' : 'var(--accent-red)',
                  color: 'white'
                }}
              >
                {trade.symbol.substring(0, 2)}
              </div>
              <div className="activity-details">
                <div className="activity-action">
                  {trade.action?.toUpperCase() || 'TRADE'} {trade.symbol}
                </div>
                <div className="activity-time">
                  {trade.date} {trade.time}
                </div>
              </div>
              <div className={`activity-amount ${trade.amount >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(Math.abs(trade.amount))}
              </div>
            </div>
          ))}
        </div>
      </RecentActivity>
    </DashboardContainer>
  );
}

export default Dashboard; 