import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  Wallet, 
  Settings, 
  Activity,
  Bot
} from 'lucide-react';

const SidebarContainer = styled.div`
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 280px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  padding: 2rem 0;
  z-index: 1000;
  
  @media (max-width: 768px) {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 2rem;
  margin-bottom: 3rem;
  
  .logo-icon {
    width: 32px;
    height: 32px;
    color: var(--accent-blue);
  }
  
  .logo-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
  }
`;

const NavSection = styled.div`
  margin-bottom: 2rem;
`;

const NavTitle = styled.h3`
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0 2rem;
  margin-bottom: 1rem;
`;

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 2rem;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border-right: 3px solid transparent;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
  
  &.active {
    background: var(--bg-tertiary);
    color: var(--accent-blue);
    border-right-color: var(--accent-blue);
  }
  
  .nav-icon {
    width: 20px;
    height: 20px;
  }
`;

const StatusIndicator = styled.div`
  position: absolute;
  bottom: 2rem;
  left: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--bg-card);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: ${props => props.connected ? 'var(--accent-green)' : 'var(--accent-red)'};
  }
  
  .status-text {
    font-size: 0.875rem;
    color: var(--text-secondary);
  }
`;

function Sidebar() {
  const location = useLocation();
  
  // Mock connection status - in real app, this would come from context
  const connected = true;

  return (
    <SidebarContainer>
      <Logo>
        <Bot className="logo-icon" />
        <span className="logo-text">AI Trading</span>
      </Logo>
      
      <NavSection>
        <NavTitle>Overview</NavTitle>
        <NavItem to="/" className={location.pathname === '/' ? 'active' : ''}>
          <BarChart3 className="nav-icon" />
          Dashboard
        </NavItem>
        <NavItem to="/portfolio" className={location.pathname === '/portfolio' ? 'active' : ''}>
          <PieChart className="nav-icon" />
          Portfolio
        </NavItem>
      </NavSection>
      
      <NavSection>
        <NavTitle>Trading</NavTitle>
        <NavItem to="/trading" className={location.pathname === '/trading' ? 'active' : ''}>
          <TrendingUp className="nav-icon" />
          Trading Activity
        </NavItem>
      </NavSection>
      
      <NavSection>
        <NavTitle>Account</NavTitle>
        <NavItem to="/wallet" className={location.pathname === '/wallet' ? 'active' : ''}>
          <Wallet className="nav-icon" />
          Wallet
        </NavItem>
        <NavItem to="/settings" className={location.pathname === '/settings' ? 'active' : ''}>
          <Settings className="nav-icon" />
          Settings
        </NavItem>
      </NavSection>
      
      <StatusIndicator connected={connected}>
        <div className="status-dot" />
        <div className="status-text">
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </StatusIndicator>
    </SidebarContainer>
  );
}

export default Sidebar; 