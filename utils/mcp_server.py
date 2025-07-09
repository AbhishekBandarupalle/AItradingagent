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
from utils.trade_log_utils import load_trade_log

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Ollama API endpoint
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'mistral')

log_dir = 'logging'
os.makedirs(log_dir, exist_ok=True)

@app.route('/mcp', methods=['POST'])
def mcp():
    data = request.get_json()
    prompt = data.get('prompt', '')
    logging.info(f"Received prompt: {prompt}")

    if prompt.startswith('RECORD_TRADES:'):
        # Just acknowledge, since agent logs trades to file
        return jsonify({'result': 'trades recorded (json)'}), 200

    elif prompt == 'GET_LATEST_TRADES':
        # Read trades from JSON log
        log_data = load_trade_log()
        trades = log_data.get('trades', [])
        # Ensure all trades have a 'verified' field
        for trade in trades:
            if 'verified' not in trade:
                trade['verified'] = False
        return jsonify({'result': json.dumps(trades)})

    elif prompt.startswith('MARK_TRADES_VERIFIED'):
        # Optionally support: MARK_TRADES_VERIFIED:transaction_id
        log_data = load_trade_log()
        trades = log_data.get('trades', [])
        parts = prompt.split(':')
        if len(parts) == 2:
            up_to_id = parts[1]
            for trade in trades:
                if int(trade['transaction_id']) <= int(up_to_id):
                    trade['verified'] = True
        else:
            for trade in trades:
                trade['verified'] = True
        log_data['trades'] = trades
        save_trade_log(log_data)
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

@app.route('/trades', methods=['GET'])
def view_trades():
    log_data = load_trade_log()
    trades = log_data.get('trades', [])
    # Group trades by transaction_id
    transactions = defaultdict(list)
    for trade in trades:
        transactions[trade['transaction_id']].append(trade)
    sorted_ids = sorted(transactions.keys(), key=lambda x: int(x))
    # Compute total and delta per transaction
    transaction_summaries = []
    prev_total = None
    for tid in sorted_ids:
        batch = transactions[tid]
        t_time = batch[0]['time']
        t_date = batch[0]['date']
        total = sum(trade['amount'] for trade in batch)
        delta = total - prev_total if prev_total is not None else None
        transaction_summaries.append({
            'transaction_id': tid,
            'time': t_time,
            'date': t_date,
            'total': total,
            'delta': delta,
            'trades': batch
        })
        prev_total = total
    latest_total = transaction_summaries[-1]['total'] if transaction_summaries else 0
    html = '''
    <html>
    <head><title>Trade Log</title></head>
    <body>
    <h2>Trade Log</h2>
    {% if transaction_summaries %}
    <h3>Current Portfolio Value: ${{ '%.2f'|format(latest_total) }}</h3>
    {% for tx in transaction_summaries %}
    <h4>Transaction {{ tx.transaction_id }} at {{ tx.time }} on {{ tx.date }} | Total: ${{ '%.2f'|format(tx.total) }}{% if tx.delta is not none %} ({{ '+' if tx.delta >= 0 else '' }}{{ '%.2f'|format(tx.delta) }}){% endif %}</h4>
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
    return render_template_string(html, transaction_summaries=transaction_summaries, latest_total=latest_total)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11534) 