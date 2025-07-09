import os
import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
import json
import os
import pandas as pd
from dash.dependencies import Input, Output
from flask import Response
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.trade_log_utils import load_trade_log

TRADE_LOG_JSON = os.environ.get('TRADE_LOG_JSON', 'trade_log.json')

# Helper to load and process trades
def load_trades():
    log_data = load_trade_log()
    trades = log_data.get('trades', [])
    if not trades:
        return pd.DataFrame()
    df = pd.DataFrame(trades)
    if df.empty:
        return df
    # Group by transaction_id for portfolio value over time
    df['transaction_id'] = df['transaction_id'].astype(str)
    df['total'] = df.groupby('transaction_id')['amount'].transform('sum')
    df['datetime'] = df['date'] + ' ' + df['time']
    return df

def get_portfolio_value_trace(df):
    # Only one row per transaction_id
    df_tx = df.drop_duplicates('transaction_id')
    return go.Scatter(
        x=df_tx['datetime'],
        y=df_tx['total'],
        mode='lines+markers',
        name='Portfolio Value'
    )

def get_allocation_pie_trace(df):
    # Use the latest transaction
    latest_tx = df[df['transaction_id'] == df['transaction_id'].max()]
    return go.Pie(
        labels=latest_tx['symbol'],
        values=latest_tx['allocation'],
        name='Current Allocation',
        hole=0.4
    )

def get_trades_table(df):
    # Show the latest N trades
    latest_tx = df[df['transaction_id'] == df['transaction_id'].max()]
    return dash_table.DataTable(
        columns=[
            {"name": "Symbol", "id": "symbol"},
            {"name": "Allocation (%)", "id": "allocation"},
            {"name": "Current Price", "id": "current_price"},
            {"name": "Amount", "id": "amount"},
        ],
        data=[{
            "symbol": row['symbol'],
            "allocation": f"{row['allocation']*100:.1f}",
            "current_price": row['current_price'] if row['current_price'] is not None else 'N/A',
            "amount": f"{row['amount']:.2f}"
        } for _, row in latest_tx.iterrows()],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'},
    )

def get_buy_sell_table(df):
    # Sort by transaction_id and symbol
    df = df.sort_values(['transaction_id', 'symbol'])
    # Build a dict: {transaction_id: {symbol: trade}}
    tx_map = {}
    for tid, group in df.groupby('transaction_id'):
        tx_map[tid] = {row['symbol']: row for _, row in group.iterrows()}
    sorted_ids = sorted(tx_map.keys(), key=lambda x: int(x))
    rows = []
    prev_tx = None
    for tid in sorted_ids:
        tx = tx_map[tid]
        if prev_tx is not None:
            all_symbols = set(tx.keys()).union(prev_tx.keys())
            for symbol in all_symbols:
                prev_alloc = prev_tx.get(symbol, {}).get('allocation', 0)
                prev_price = prev_tx.get(symbol, {}).get('current_price', None)
                curr_alloc = tx.get(symbol, {}).get('allocation', 0)
                curr_price = tx.get(symbol, {}).get('current_price', None)
                alloc_delta = curr_alloc - prev_alloc
                price_delta = (curr_price - prev_price) if (curr_price is not None and prev_price is not None) else None
                if alloc_delta > 0:
                    action = 'Buy'
                elif alloc_delta < 0:
                    action = 'Sell'
                else:
                    action = 'Hold'
                rows.append({
                    'transaction_id': tid,
                    'symbol': symbol,
                    'action': action,
                    'alloc_change': f"{alloc_delta*100:+.1f}",
                    'price_change': f"{price_delta:+.2f}" if price_delta is not None else 'N/A',
                    'time': tx.get(symbol, {}).get('time', ''),
                    'date': tx.get(symbol, {}).get('date', ''),
                })
        prev_tx = tx
    if not rows:
        return html.P("No buy/sell actions yet.", style={'color': light_text})
    return dash_table.DataTable(
        columns=[
            {"name": "Transaction ID", "id": "transaction_id"},
            {"name": "Symbol", "id": "symbol"},
            {"name": "Action", "id": "action"},
            {"name": "Allocation Change (%)", "id": "alloc_change"},
            {"name": "Price Change ($)", "id": "price_change"},
            {"name": "Time", "id": "time"},
            {"name": "Date", "id": "date"},
        ],
        data=rows,
        style_table={'overflowX': 'auto', 'backgroundColor': dark_card},
        style_cell={'textAlign': 'center', 'backgroundColor': dark_card, 'color': light_text},
        style_header={'fontWeight': 'bold', 'backgroundColor': accent, 'color': dark_bg},
        page_size=20,
    )

app = dash.Dash(__name__)
app.title = "AI Trading Dashboard"

dark_bg = '#222831'
dark_card = '#393E46'
light_text = '#EEEEEE'
accent = '#00ADB5'

app.layout = html.Div([
    html.H1("AI Trading Dashboard", style={'color': accent}),
    dcc.Interval(id='interval', interval=60*1000, n_intervals=0),  # update every minute
    html.Div(id='portfolio-value-text', style={'fontSize': '2.5em', 'color': accent, 'marginBottom': '20px'}),
    html.Div([
        dcc.Graph(id='portfolio-value'),
        dcc.Graph(id='allocation-pie'),
    ], style={'display': 'flex', 'flexDirection': 'row'}),
    html.A(
        'View All Transactions (JSON)',
        href='/transactions',
        target='_blank',
        style={
            'display': 'inline-block',
            'margin': '20px 0',
            'padding': '10px 20px',
            'backgroundColor': accent,
            'color': dark_bg,
            'borderRadius': '5px',
            'textDecoration': 'none',
            'fontWeight': 'bold',
            'fontSize': '1.1em',
        }
    ),
    html.H2("Latest Trades", style={'color': accent}),
    html.Div(id='trades-table'),
], style={'backgroundColor': dark_bg, 'minHeight': '100vh', 'padding': '20px'})

# Remove buy-sell-table from callback and layout
@app.server.route('/transactions')
def serve_transactions():
    log_data = load_trade_log()
    from flask import jsonify
    return Response(json.dumps(log_data, indent=2), mimetype='application/json')

@app.callback(
    [Output('portfolio-value', 'figure'),
     Output('allocation-pie', 'figure'),
     Output('trades-table', 'children'),
     Output('portfolio-value-text', 'children')],
    [Input('interval', 'n_intervals')]
)
def update_dashboard(n):
    df = load_trades()
    if df.empty:
        return go.Figure(), go.Figure(), html.P("No trades found.", style={'color': light_text}), "Portfolio Value: $0.00 | Cash: $0.00"
    # Portfolio value line chart
    value_fig = go.Figure([get_portfolio_value_trace(df)])
    value_fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Time",
        yaxis_title="Total Value ($)",
        plot_bgcolor=dark_card,
        paper_bgcolor=dark_bg,
        font_color=light_text,
        title_font_color=accent,
        xaxis=dict(color=light_text),
        yaxis=dict(color=light_text),
    )
    # Allocation pie chart
    pie_fig = go.Figure([get_allocation_pie_trace(df)])
    pie_fig.update_layout(
        title="Current Allocation",
        plot_bgcolor=dark_card,
        paper_bgcolor=dark_bg,
        font_color=light_text,
        title_font_color=accent,
        legend=dict(font=dict(color=light_text)),
    )
    # Trades table
    latest_tx = df[df['transaction_id'] == df['transaction_id'].max()]
    trades_table = dash_table.DataTable(
        columns=[
            {"name": "Symbol", "id": "symbol"},
            {"name": "Allocation (%)", "id": "allocation"},
            {"name": "Current Price", "id": "current_price"},
            {"name": "Amount", "id": "amount"},
        ],
        data=[{
            "symbol": row['symbol'],
            "allocation": f"{row['allocation']*100:.1f}",
            "current_price": row['current_price'] if row['current_price'] is not None else 'N/A',
            "amount": f"{row['amount']:.2f}"
        } for _, row in latest_tx.iterrows()],
        style_table={'overflowX': 'auto', 'backgroundColor': dark_card},
        style_cell={'textAlign': 'center', 'backgroundColor': dark_card, 'color': light_text},
        style_header={'fontWeight': 'bold', 'backgroundColor': accent, 'color': dark_bg},
    )
    # Portfolio value and cash as text
    # Get the latest trade (by transaction_id and then by index)
    latest_trade = df[df['transaction_id'] == df['transaction_id'].max()].iloc[-1]
    portfolio_value = latest_trade.get('portfolio_value', 0)
    cash = latest_trade.get('final_cash', 0)
    value_text = f"Portfolio Value: ${portfolio_value:,.2f} | Cash: ${cash:,.2f}"
    return value_fig, pie_fig, trades_table, value_text

if __name__ == '__main__':
    app.run(port=8050) 