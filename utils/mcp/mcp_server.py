# Standard library imports
import csv
import json
import logging
import os
import re
import sys
from collections import defaultdict

# Third-party imports
import requests
from flask import Flask, request, jsonify, render_template_string

# Local imports
# Add project root to Python path (two levels up from utils/mcp/mcp_server.py)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils import TradeDatabase
from utils.llm_response_utils import extract_json_from_streaming_response, validate_and_parse_json

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
        # Forward to Ollama with improved response processing
        payload = {
            'model': OLLAMA_MODEL,
            'prompt': prompt
        }
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
            resp.raise_for_status()
            
            # Use improved response processing
            lines = resp.text.strip().splitlines()
            
            # Debug: Log first few lines to understand the format
            logging.info(f"Response lines count: {len(lines)}")
            logging.info(f"First 3 lines: {lines[:3]}")
            logging.info(f"Last 3 lines: {lines[-3:]}")
            
            response_text, json_result = extract_json_from_streaming_response(lines)
            
            logging.info(f"Full LLM response: {response_text}")
            logging.info(f"Extracted JSON result: {json_result}")
            
            if json_result:
                # Validate the JSON one more time
                parsed_json = validate_and_parse_json(json_result)
                if parsed_json:
                    logging.info(f"Extracted and validated JSON: {json_result}")
                    return jsonify({'result': json_result})
                else:
                    logging.error(f"Invalid JSON extracted: {json_result}")
                    return jsonify({'result': 'llm error: invalid json'}), 500
            else:
                logging.error(f"No JSON found in LLM response: {response_text}")
                # As a final fallback, try to extract JSON directly from the raw response
                from utils.llm_response_utils import clean_llm_json
                fallback_json = clean_llm_json(resp.text)
                if fallback_json:
                    logging.info(f"Fallback JSON extraction succeeded: {fallback_json}")
                    return jsonify({'result': fallback_json})
                # Return the raw response as fallback
                return jsonify({'result': response_text or 'llm error: no response'}), 500
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama request failed: {e}")
            return jsonify({'result': f'llm error: {str(e)}'}), 500
        except Exception as e:
            logging.error(f"Unexpected error in LLM processing: {e}")
            return jsonify({'result': f'llm error: {str(e)}'}), 500

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
        result = db.get_trades(limit)
    else:
        result = db.get_trades()
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
    result = db.get_trades()
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