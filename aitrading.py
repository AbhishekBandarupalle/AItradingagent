import sys
import subprocess
import os
import signal
import time

# Paths to scripts
MCP_SERVER = os.path.join('utils', 'mcp_server.py')
TRADING_AGENT = os.path.join('agents', 'trading_agent.py')
VERIFICATION_AGENT = os.path.join('agents', 'verification_agent.py')
DASHBOARD = os.path.join('services', 'dashboard.py')
LOG_DIR = 'logging'

# Log files
MCP_LOG = os.path.join(LOG_DIR, 'mcp_server.log')
TRADING_LOG = os.path.join(LOG_DIR, 'trading_agent.log')
VERIFICATION_LOG = os.path.join(LOG_DIR, 'verification_agent.log')
DASHBOARD_LOG = os.path.join(LOG_DIR, 'dashboard.log')

# Process names for stopping
PROCESS_NAMES = [
    MCP_SERVER,
    TRADING_AGENT,
    VERIFICATION_AGENT,
    DASHBOARD
]


def start_all():
    os.makedirs(LOG_DIR, exist_ok=True)
    procs = [
        (['python3', MCP_SERVER], MCP_LOG),
        (['python3', TRADING_AGENT], TRADING_LOG),
        (['python3', DASHBOARD], DASHBOARD_LOG),
        (['python3', VERIFICATION_AGENT], VERIFICATION_LOG),
    ]
    for cmd, logfile in procs:
        with open(logfile, 'a') as f:
            subprocess.Popen(cmd, stdout=f, stderr=f, cwd=os.path.abspath('.'))
    print("All services started in background.")
    print(f"MCP server log: {MCP_LOG}")
    print(f"Trading agent log: {TRADING_LOG}")
    print(f"Verification agent log: {VERIFICATION_LOG}")
    print(f"Dashboard log: {DASHBOARD_LOG}")
    print("Dashboard: http://localhost:8050")


def stop_all():
    # Find and kill all relevant python processes
    import psutil
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if not cmdline:
                continue
            for script in PROCESS_NAMES:
                if any(script in arg for arg in cmdline):
                    print(f"Killing {cmdline} (pid {proc.pid})")
                    proc.kill()
                    killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if killed == 0:
        print("No matching processes found.")
    else:
        print(f"Stopped {killed} processes.")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('start', 'stop'):
        print("Usage: python aitrading.py [start|stop]")
        sys.exit(1)
    if sys.argv[1] == 'start':
        start_all()
    elif sys.argv[1] == 'stop':
        stop_all()

if __name__ == '__main__':
    main() 