# AI Trading Dashboard

A modern, professional trading dashboard built with React.js that provides real-time portfolio monitoring, trading activity tracking, and comprehensive analytics for the AI Trading Agent system.

## 🚀 Features

### 📊 Dashboard Overview
- **Real-time Portfolio Metrics**: Live portfolio value, day change, cash balance, and total returns
- **Interactive Charts**: Portfolio performance over time with area charts and asset allocation pie charts
- **Recent Activity Feed**: Latest trading activities with visual indicators
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### 💼 Portfolio Management
- **Position Tracking**: Detailed view of all current holdings with allocation percentages
- **Search & Filter**: Find specific positions and filter by sentiment or asset type
- **Visual Allocation Bars**: Quick visual representation of portfolio allocation
- **Sentiment Analysis**: Color-coded sentiment indicators for each position

### 📈 Trading Activity
- **Complete Trade History**: Chronological view of all buy/sell transactions
- **Trade Statistics**: Total trades, buy/sell ratios, and volume metrics
- **Action Filtering**: Filter trades by buy, sell, or hold actions
- **Export Functionality**: Download trade history for analysis

### 🎨 Modern UI/UX
- **Dark Theme**: Professional dark interface optimized for trading
- **Smooth Animations**: Framer Motion powered transitions and interactions
- **Professional Icons**: Lucide React icons for consistent visual language
- **Styled Components**: CSS-in-JS for maintainable and themeable styles

## 🛠️ Technology Stack

- **Frontend**: React 18 with Hooks and Context API
- **Styling**: Styled Components with CSS Variables
- **Charts**: Recharts for responsive data visualization
- **Icons**: Lucide React for consistent iconography
- **Animations**: Framer Motion for smooth transitions
- **HTTP Client**: Axios for API communication
- **Real-time**: Socket.io for live data updates
- **Build Tool**: Create React App

## 🏗️ Architecture

```
trading-dashboard/
├── public/
│   ├── index.html          # Main HTML template
│   └── manifest.json       # PWA manifest
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Header.js      # Top navigation with portfolio summary
│   │   └── Sidebar.js     # Side navigation menu
│   ├── context/           # React Context for state management
│   │   └── TradingContext.js # Global trading data state
│   ├── pages/             # Main application pages
│   │   ├── Dashboard.js   # Overview dashboard
│   │   ├── Portfolio.js   # Portfolio positions
│   │   └── Trading.js     # Trading activity
│   ├── App.js             # Main application component
│   ├── index.js           # Application entry point
│   └── index.css          # Global styles and CSS variables
├── server.js              # Express.js backend server
├── package.json           # Dependencies and scripts
└── README.md             # This file
```

## 🚦 Getting Started

### Prerequisites
- Node.js 16+ and npm
- AI Trading Agent system running on port 11534
- MongoDB database configured

### Installation

1. **Navigate to the dashboard directory**:
   ```bash
   cd services/trading-dashboard
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development servers**:
   ```bash
   npm run dev
   ```

   This will start both the Express.js backend (port 3001) and React frontend (port 3000).

### Alternative: Start servers separately

**Backend only**:
```bash
npm run server
```

**Frontend only**:
```bash
npm start
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the dashboard root:

```env
REACT_APP_API_URL=http://localhost:3001
MCP_SERVER_URL=http://localhost:11534
PORT=3001
```

### API Endpoints
The dashboard connects to these backend endpoints:

- `GET /api/portfolio-summary` - Portfolio metrics and summary
- `GET /api/current-positions` - Current holdings and positions
- `GET /api/trades` - Complete trading history
- `GET /api/portfolio-history` - Historical portfolio values
- `WebSocket /` - Real-time updates

## 📱 Usage

### Navigation
- **Dashboard**: Overview of portfolio performance and recent activity
- **Portfolio**: Detailed view of current positions and holdings
- **Trading**: Complete trading history with filtering options

### Features
- **Real-time Updates**: Data refreshes automatically every minute
- **Search**: Find specific positions or trades quickly
- **Filtering**: Filter trades by action type (buy/sell/hold)
- **Responsive**: Works seamlessly on all device sizes

## 🎨 Customization

### Themes
Modify CSS variables in `src/index.css`:

```css
:root {
  --bg-primary: #0a0a0a;      /* Main background */
  --bg-secondary: #1a1a1a;    /* Secondary background */
  --bg-card: #1e1e1e;         /* Card background */
  --accent-green: #00d4aa;    /* Success/profit color */
  --accent-red: #ff6b6b;      /* Error/loss color */
  --accent-blue: #4dabf7;     /* Primary accent */
}
```

### Components
All components are built with Styled Components, making them easy to customize:

```jsx
const CustomCard = styled.div`
  background: var(--bg-card);
  border-radius: 12px;
  padding: 1.5rem;
  /* Add your custom styles */
`;
```

## 🔄 Data Flow

1. **React Context** manages global state
2. **Express.js server** fetches data from MCP server
3. **WebSocket connection** provides real-time updates
4. **Components** subscribe to context for reactive updates

## 🧪 Development

### Available Scripts
- `npm start` - Start React development server
- `npm run server` - Start Express.js backend
- `npm run dev` - Start both servers concurrently
- `npm run build` - Build for production
- `npm test` - Run test suite

### Adding New Features
1. Create new components in `src/components/`
2. Add new pages in `src/pages/`
3. Update routing in `src/App.js`
4. Add API endpoints in `server.js`

## 🚀 Production Deployment

### Build for Production
```bash
npm run build
```

### Deploy with PM2
```bash
pm2 start server.js --name "trading-dashboard"
```

### Environment Setup
- Set `NODE_ENV=production`
- Configure reverse proxy (nginx recommended)
- Set up SSL/TLS certificates
- Configure MongoDB connection

## 🔍 Troubleshooting

### Common Issues

**Dashboard not loading data**:
- Check MCP server is running on port 11534
- Verify MongoDB connection
- Check browser console for errors

**WebSocket connection failed**:
- Ensure backend server is running
- Check firewall settings
- Verify CORS configuration

**Charts not rendering**:
- Check data format in API responses
- Verify Recharts version compatibility
- Check browser console for errors

## 📊 Performance

- **Bundle Size**: ~2MB gzipped
- **Initial Load**: <3 seconds
- **Real-time Updates**: 30-second intervals
- **Mobile Optimized**: Touch-friendly interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the AI Trading Agent system. See the main project README for license information.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the main project documentation
3. Open an issue in the main repository

---

**Built with ❤️ for professional trading** 