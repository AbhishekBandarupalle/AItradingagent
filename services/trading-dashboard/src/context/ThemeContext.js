import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage for saved preference, default to dark mode
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  useEffect(() => {
    // Save theme preference to localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Apply theme to document root
    const root = document.documentElement;
    if (isDarkMode) {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.setAttribute('data-theme', 'light');
    }
  }, [isDarkMode]);

  const value = {
    isDarkMode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}; 