import React from 'react';
import styled from 'styled-components';
import { useTheme } from '../context/ThemeContext';

const ToggleContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: var(--bg-tertiary);
  }
`;

const ToggleButton = styled.div`
  position: relative;
  width: 48px;
  height: 24px;
  background-color: var(--bg-tertiary);
  border-radius: 12px;
  border: 2px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 16px;
    height: 16px;
    background-color: var(--text-primary);
    border-radius: 50%;
    transition: all 0.3s ease;
    transform: translateX(${props => props.isDark ? '0' : '24px'});
  }
  
  &:hover {
    border-color: var(--accent-blue);
  }
`;

const Icon = styled.span`
  font-size: 1rem;
  color: var(--text-secondary);
  transition: color 0.2s ease;
  
  &:hover {
    color: var(--text-primary);
  }
`;

const ThemeToggle = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <ToggleContainer onClick={toggleTheme}>
      <Icon>{isDarkMode ? '🌙' : '☀️'}</Icon>
      <ToggleButton isDark={isDarkMode} />
    </ToggleContainer>
  );
};

export default ThemeToggle; 