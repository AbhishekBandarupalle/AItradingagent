import os
import json

LOG_DIR = 'logging'
os.makedirs(LOG_DIR, exist_ok=True)
TRADE_LOG_JSON = os.environ.get('TRADE_LOG_JSON', os.path.join(LOG_DIR, 'trade_log.json'))


def load_trade_log(log_path=TRADE_LOG_JSON):
    """
    Load the trade log from JSON file, migrating legacy list format to dict if needed.
    Always returns a dict with 'new_trade' and 'trades' keys.
    """
    if not os.path.exists(log_path):
        return {"new_trade": False, "trades": []}
    try:
        with open(log_path, 'r') as f:
            data = json.load(f)
        # If it's a list, migrate to dict format
        if isinstance(data, list):
            data = {"new_trade": False, "trades": data}
            with open(log_path, 'w') as f:
                json.dump(data, f, indent=2)
        # If it's empty or missing keys, reset
        if not isinstance(data, dict) or "trades" not in data:
            data = {"new_trade": False, "trades": []}
        return data
    except Exception:
        return {"new_trade": False, "trades": []}


def save_trade_log(log_data, log_path=TRADE_LOG_JSON):
    """
    Save the trade log to JSON file, ensuring correct format.
    """
    if not isinstance(log_data, dict):
        log_data = {"new_trade": False, "trades": []}
    if "trades" not in log_data:
        log_data["trades"] = []
    if "new_trade" not in log_data:
        log_data["new_trade"] = False
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=2) 