function Dashboard() {
  const [trades, setTrades] = React.useState([]);

  React.useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 60000);
    return () => clearInterval(id);
  }, []);

  function fetchData() {
    fetch('http://localhost:11534/api/trades')
      .then(res => res.json())
      .then(res => {
        if (res.success) {
          setTrades(res.trades);
        }
      })
      .catch(() => {});
  }

  React.useEffect(() => {
    if (!trades.length) return;

    const totals = {};
    trades.forEach(t => {
      totals[t.transaction_id] = (totals[t.transaction_id] || 0) + t.amount;
    });
    const ids = Object.keys(totals).sort((a,b) => parseInt(a) - parseInt(b));
    const lineLabels = ids;
    const lineValues = ids.map(id => totals[id]);

    const lastId = ids[ids.length - 1];
    const lastTrades = trades.filter(t => t.transaction_id === lastId);
    const pieLabels = lastTrades.map(t => t.symbol);
    const pieValues = lastTrades.map(t => t.allocation);

    const ctx1 = document.getElementById('valueChart').getContext('2d');
    new Chart(ctx1, {
      type: 'line',
      data: { labels: lineLabels, datasets: [{ label: 'Portfolio Value', data: lineValues, borderColor: '#00ADB5', backgroundColor: 'rgba(0,173,181,0.2)' }] },
      options: { scales: { y: { beginAtZero: true } } }
    });

    const ctx2 = document.getElementById('allocChart').getContext('2d');
    new Chart(ctx2, {
      type: 'pie',
      data: { labels: pieLabels, datasets: [{ data: pieValues, backgroundColor: ['#00ADB5', '#393E46', '#222831', '#EEEEEE'] }] },
    });
  }, [trades]);

  if (!trades.length) {
    return React.createElement('div', null, 'Loading...');
  }

  const lastTxId = trades[trades.length - 1].transaction_id;
  const latest = trades.filter(t => t.transaction_id === lastTxId);
  const lastTrade = latest[latest.length - 1];

  return (
    <div>
      <header>
        <h1>AI Trading Dashboard</h1>
        <h3>Portfolio Value: ${lastTrade.portfolio_value.toFixed(2)} | Cash: ${lastTrade.final_cash.toFixed(2)}</h3>
      </header>
      <div className="chart-container">
        <canvas id="valueChart" width="400" height="300"></canvas>
        <canvas id="allocChart" width="400" height="300"></canvas>
      </div>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Allocation (%)</th>
            <th>Current Price</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          {latest.map((t, i) => (
            <tr key={i}>
              <td>{t.symbol}</td>
              <td>{(t.allocation * 100).toFixed(1)}</td>
              <td>{t.current_price !== null ? t.current_price : 'N/A'}</td>
              <td>{t.amount.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<Dashboard />);

