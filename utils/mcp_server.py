import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify, render_template_string
import requests
import logging
import json
import csv
import re
from collections import defaultdict
from utils.db_utils import TradeDatabase

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Ollama API endpoint
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'mistral')

# Initialize database
db = TradeDatabase()

log_dir = 'logging'
os.makedirs(log_dir, exist_ok=True)

@app.route('/mcp', methods=['POST'])
def mcp():
    data = request.get_json()
    prompt = data.get('prompt', '')
    logging.info(f"Received prompt: {prompt}")

    if prompt.startswith('RECORD_TRADES:'):
        # Extract trades from the prompt and save to database
        trades_json = prompt.replace('RECORD_TRADES:', '')
        try:
            trades = json.loads(trades_json)
            result = db.save_trades(trades)
            if result['success']:
                return jsonify({'result': 'trades recorded (database)'}), 200
            else:
                return jsonify({'result': f'error: {result["error"]}'}), 500
        except Exception as e:
            logging.error(f"Error parsing trades: {e}")
            return jsonify({'result': f'error parsing trades: {str(e)}'}), 400

    elif prompt == 'GET_LATEST_TRADES':
        # Get trades from database
        result = db.get_all_trades()
        if result['success']:
            trades = result['trades']
            # Ensure all trades have a 'verified' field
            for trade in trades:
                if 'verified' not in trade:
                    trade['verified'] = False
            return jsonify({'result': json.dumps(trades)})
        else:
            return jsonify({'result': f'error: {result["error"]}'}), 500

    elif prompt.startswith('MARK_TRADES_VERIFIED'):
        # TODO: Implement verification marking in database
        return jsonify({'result': 'trades marked as verified'}), 200

    else:
        # Forward to Ollama
        payload = {
            'model': OLLAMA_MODEL,
            'prompt': prompt
        }
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
            resp.raise_for_status()
            # Concatenate all 'response' fields from the streamed JSON lines
            response_text = ""
            lines = resp.text.strip().splitlines()
            for line in lines:
                try:
                    obj = json.loads(line)
                    if 'response' in obj:
                        response_text += obj['response']
                except Exception:
                    continue
            # Now try to extract JSON from the concatenated response_text
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                llm_result = match.group(0)
                return jsonify({'result': llm_result})
            else:
                return jsonify({'result': 'llm error'}), 500
        except Exception as e:
            logging.error(f"Ollama request failed: {e}")
            return jsonify({'result': 'llm error'}), 500

# New database endpoints
@app.route('/api/trades', methods=['POST'])
def save_trades():
    """Save trades to the database."""
    data = request.get_json()
    trades = data.get('trades', [])
    result = db.save_trades(trades)
    return jsonify(result)

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get all trades from the database."""
    limit = request.args.get('limit', type=int)
    if limit:
        result = db.get_latest_trades(limit)
    else:
        result = db.get_all_trades()
    return jsonify(result)

@app.route('/api/trades/latest', methods=['GET'])
def get_latest_transaction():
    """Get the latest transaction (all trades with same transaction_id)."""
    result = db.get_latest_transaction()
    return jsonify(result)

@app.route('/api/holdings', methods=['GET'])
def get_current_holdings():
    """Get current holdings from the latest transaction."""
    result = db.get_current_holdings()
    return jsonify(result)

@app.route('/api/transaction-id', methods=['GET'])
def get_last_transaction_id():
    """Get the last transaction ID."""
    result = db.get_last_transaction_id()
    return jsonify(result)

@app.route('/trades', methods=['GET'])
def view_trades():
    result = db.get_all_trades()
    if not result['success']:
        return f"Error loading trades: {result['error']}", 500
    
    trades = result['trades']
    # Group trades by transaction_id
    transactions = defaultdict(list)
    for trade in trades:
        transactions[trade['transaction_id']].append(trade)
    sorted_ids = sorted(transactions.keys(), key=lambda x: int(x))
    
    # Compute total and delta per transaction
    transaction_summaries = []
    prev_portfolio_value = None
    for tid in sorted_ids:
        batch = transactions[tid]
        t_time = batch[0]['time']
        t_date = batch[0]['date']
        # Use portfolio_value from the first trade in the batch if available
        portfolio_value = batch[0].get('portfolio_value')
        delta = portfolio_value - prev_portfolio_value if (prev_portfolio_value is not None and portfolio_value is not None) else None
        transaction_summaries.append({
            'transaction_id': tid,
            'time': t_time,
            'date': t_date,
            'portfolio_value': portfolio_value,
            'delta': delta,
            'trades': batch
        })
        prev_portfolio_value = portfolio_value
    
    latest_portfolio_value = transaction_summaries[-1]['portfolio_value'] if transaction_summaries and transaction_summaries[-1]['portfolio_value'] is not None else 0
    
    html = '''
    <html>
    <head><title>Trade Log</title></head>
    <body>
    <h2>Trade Log</h2>
    {% if transaction_summaries %}
    <h3>Current Portfolio Value: ${{ '%.2f'|format(latest_portfolio_value) }}</h3>
    {% for tx in transaction_summaries %}
    <h4>Transaction {{ tx.transaction_id }} at {{ tx.time }} on {{ tx.date }} | Portfolio Value: ${{ '%.2f'|format(tx.portfolio_value) }}{% if tx.delta is not none %} ({{ '+' if tx.delta >= 0 else '' }}{{ '%.2f'|format(tx.delta) }}){% endif %}</h4>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Stock Symbol</th>
            <th>Allocation (%)</th>
            <th>Current Price</th>
            <th>Amount</th>
        </tr>
        {% for trade in tx.trades %}
        <tr>
            <td>{{ trade.symbol }}</td>
            <td>{{ '%.1f'|format(trade.allocation * 100) }}</td>
            <td>{{ trade.current_price if trade.current_price is not none else 'N/A' }}</td>
            <td>{{ '%.2f'|format(trade.amount) }}</td>
        </tr>
        {% endfor %}
    </table>
    <br/>
    {% endfor %}
    {% else %}
    <p>No trades found.</p>
    {% endif %}
    </body>
    </html>
    '''
    return render_template_string(html, transaction_summaries=transaction_summaries, latest_portfolio_value=latest_portfolio_value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11534) 