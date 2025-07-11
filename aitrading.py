import sys
import subprocess
import os
import signal
import time
import json

# Import our system setup utilities
from utils import (
    setup_system_dependencies,
    check_node_installed,
    check_python_requirements,
    check_mongodb_installed,
    cleanup_trading_database
)

# Paths to scripts
MCP_SERVER = os.path.join('utils', 'mcp', 'mcp_server.py')
TRADING_AGENT = os.path.join('agents', 'trading_agent.py')
VERIFICATION_AGENT = os.path.join('agents', 'verification_agent.py')
REACT_DASHBOARD_DIR = os.path.join('services', 'trading-dashboard')
LOG_DIR = 'logging'

# Log files
MCP_LOG = os.path.join(LOG_DIR, 'mcp_server.log')
TRADING_LOG = os.path.join(LOG_DIR, 'trading_agent.log')
VERIFICATION_LOG = os.path.join(LOG_DIR, 'verification_agent.log')
REACT_BACKEND_LOG = os.path.join(LOG_DIR, 'react_backend.log')
REACT_FRONTEND_LOG = os.path.join(LOG_DIR, 'react_frontend.log')

# Process names for stopping
PROCESS_NAMES = [
    MCP_SERVER,
    TRADING_AGENT,
    VERIFICATION_AGENT,
    'node',  # For React dashboard processes
    'npm'    # For npm processes
]

def cleanup_database_on_stop():
    """Clean up database when AI trading system is stopped."""
    try:
        print("🧹 Cleaning up database...")
        cleanup_trading_database()
        
    except Exception as e:
        print(f"⚠️  Database cleanup failed: {e}")
        # Don't stop the process if database cleanup fails

def start_all():
    """Start all AI trading system services"""
    # Remove the logging directory if it exists to clear all previous cache/logs
    if os.path.exists(LOG_DIR):
        import shutil
        import logging
        # Close all logging handlers
        for handler in logging.root.handlers[:]:
            try:
                handler.close()
            except Exception as e:
                print(f"Error closing handler: {e}")
            logging.root.removeHandler(handler)
        # Try to delete the directory
        try:
            shutil.rmtree(LOG_DIR)
        except Exception as e:
            print(f"Failed to delete {LOG_DIR}: {e}")
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("🚀 Starting AI Trading System...")
    print("=" * 50)
    
    # Setup system dependencies (Python requirements, Node.js, React dependencies)
    setup_status = setup_system_dependencies(REACT_DASHBOARD_DIR, interactive=True)
    
    if not setup_status['python_requirements']:
        print("❌ Python requirements not satisfied. Please install them manually.")
        print("   Run: pip install -r requirements.txt")
        return
    
    print("\n🔧 Starting Core Services...")
    print("=" * 50)
    
    # Trading agent will auto-initialize if needed
    print("🔍 Trading agent will auto-initialize if needed...")
    
    # Start core Python services
    procs = [
        (['python3', MCP_SERVER], MCP_LOG, "MCP Server"),
        (['python3', TRADING_AGENT], TRADING_LOG, "Trading Agent"),
        (['python3', VERIFICATION_AGENT], VERIFICATION_LOG, "Verification Agent"),
    ]
    
    for cmd, logfile, name in procs:
        with open(logfile, 'a') as f:
            subprocess.Popen(cmd, stdout=f, stderr=f, cwd=os.path.abspath('.'))
        print(f"✅ {name} started")
    
    # Start React dashboard if available
    if setup_status['nodejs'] and setup_status['react_dependencies']:
        print("\n🌐 Starting React Dashboard...")
        print("=" * 30)
        
        # Start React dashboard backend (Express.js)
        print("🔧 Starting Dashboard Backend...")
        with open(REACT_BACKEND_LOG, 'a') as f:
            subprocess.Popen(['npm', 'run', 'server'], 
                           stdout=f, stderr=f, cwd=REACT_DASHBOARD_DIR)
        print("✅ React Backend started")
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start React dashboard frontend (development server)
        print("⚛️  Starting Dashboard Frontend...")
        with open(REACT_FRONTEND_LOG, 'a') as f:
            # Set environment variable to avoid opening browser automatically
            env = os.environ.copy()
            env['BROWSER'] = 'none'
            subprocess.Popen(['npm', 'start'], 
                           stdout=f, stderr=f, cwd=REACT_DASHBOARD_DIR, env=env)
        print("✅ React Frontend started")
    else:
        print("\n⚠️  React dashboard not available")
        if not setup_status['nodejs']:
            print("   • Node.js is required")
        if not setup_status['react_dependencies']:
            print("   • React dependencies need to be installed")
    
    print("\n" + "=" * 50)
    print("🎉 AI Trading System Started Successfully!")
    print("=" * 50)
    
    # Display service information
    print("\n📊 Running Services:")
    print(f"├── MCP Server: Running (logs: {MCP_LOG})")
    print(f"├── Trading Agent: Running (logs: {TRADING_LOG})")
    print(f"├── Verification Agent: Running (logs: {VERIFICATION_LOG})")
    
    if setup_status['nodejs'] and setup_status['react_dependencies']:
        print(f"└── Trading Dashboard: http://localhost:3000 (logs: {REACT_FRONTEND_LOG})")
        print(f"    └── Dashboard API: http://localhost:3001 (logs: {REACT_BACKEND_LOG})")
    else:
        print("└── Trading Dashboard: Not available")
    
    print("\n💡 Tips:")
    print("   • Use 'python aitrading.py stop' to stop all services")
    print("   • Use 'python aitrading.py restart' to restart all services")
    print("   • Use 'python aitrading.py status' to check service status")
    print("   • Check log files for detailed information")
    if setup_status['nodejs'] and setup_status['react_dependencies']:
        print("   • Access the dashboard at http://localhost:3000")
    else:
        print("   • Install Node.js to access the trading dashboard")

def stop_all():
    """Stop all AI trading system services"""
    print("🛑 Stopping AI Trading System...")
    print("=" * 50)
    
    # Find and kill all relevant processes
    import psutil
    killed = 0
    killed_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if not cmdline:
                continue
            
            # Check for Python scripts
            for script in PROCESS_NAMES:
                if script.endswith('.py') and any(script in arg for arg in cmdline):
                    process_name = os.path.basename(script).replace('.py', '')
                    print(f"🔴 Stopping {process_name} (PID: {proc.pid})")
                    proc.kill()
                    killed += 1
                    killed_processes.append(process_name)
                    break
            
            # Check for Node.js processes (React dashboard)
            if proc.info['name'] in ['node', 'npm'] and cmdline:
                # Check if it's related to our React dashboard
                if any('trading-dashboard' in arg for arg in cmdline) or \
                   any('react-scripts' in arg for arg in cmdline) or \
                   any('server.js' in arg for arg in cmdline):
                    print(f"🔴 Stopping React Dashboard process (PID: {proc.pid})")
                    proc.kill()
                    killed += 1
                    killed_processes.append("React Dashboard")
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if killed == 0:
        print("ℹ️  No running processes found.")
    else:
        print(f"\n✅ Successfully stopped {killed} processes:")
        for process in set(killed_processes):
            print(f"   • {process}")
    
    print("\n🧹 Cleaning up...")
    
    # Clean up database when stopping the system
    cleanup_database_on_stop()
    
    # Clean up log files
    if os.path.exists(LOG_DIR):
        try:
            import shutil
            shutil.rmtree(LOG_DIR)
            print("✅ Log files cleaned up")
        except Exception as e:
            print(f"⚠️  Could not clean up logs: {e}")
    
    print("\n" + "=" * 50)
    print("✅ AI Trading System Stopped Successfully!")
    print("=" * 50)

def status():
    """Check the status of all services"""
    print("📊 AI Trading System Status")
    print("=" * 50)
    
    import psutil
    running_services = []
    
    # Check Python services
    python_services = {
        MCP_SERVER: "MCP Server",
        TRADING_AGENT: "Trading Agent", 
        VERIFICATION_AGENT: "Verification Agent"
    }
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if not cmdline:
                continue
                
            for script, name in python_services.items():
                if any(script in arg for arg in cmdline):
                    running_services.append((name, proc.pid, "Python"))
                    break
                    
            # Check React dashboard processes
            if proc.info['name'] in ['node', 'npm'] and cmdline:
                if any('trading-dashboard' in arg for arg in cmdline):
                    if any('server.js' in arg for arg in cmdline):
                        running_services.append(("React Backend", proc.pid, "Node.js"))
                    elif any('react-scripts' in arg for arg in cmdline):
                        running_services.append(("React Frontend", proc.pid, "Node.js"))
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if running_services:
        print("🟢 Running Services:")
        for service, pid, runtime in running_services:
            print(f"   • {service:<20} (PID: {pid}, {runtime})")
    else:
        print("🔴 No services currently running")
    
    # Check system dependencies
    print(f"\n🔧 System Dependencies:")
    python_ok = check_python_requirements()
    mongodb_ok = check_mongodb_installed()
    nodejs_ok = check_node_installed()
    react_deps_ok = os.path.exists(os.path.join(REACT_DASHBOARD_DIR, 'node_modules'))
    
    print(f"   • Python Requirements: {'✅ Ready' if python_ok else '❌ Missing'}")
    print(f"   • MongoDB: {'✅ Ready' if mongodb_ok else '❌ Missing'}")
    print(f"   • Node.js: {'✅ Ready' if nodejs_ok else '❌ Missing'}")
    print(f"   • React Dependencies: {'✅ Ready' if react_deps_ok else '❌ Missing'}")
    
    # Only show dashboard availability if services are running
    if running_services:
        dashboard_running = any("React" in service for service, _, _ in running_services)
        print(f"\n🌐 Available Dashboard:")
        if dashboard_running and nodejs_ok and react_deps_ok:
            print(f"   • Trading Dashboard: http://localhost:3000")
        elif nodejs_ok and react_deps_ok:
            print(f"   • Trading Dashboard: Dependencies ready (not running)")
            print(f"     Run 'python aitrading.py start' to launch")
        else:
            print(f"   • Trading Dashboard: Not available")
            if not nodejs_ok:
                print(f"     - Node.js required")
            if not react_deps_ok:
                print(f"     - React dependencies need installation")
            print(f"     Run 'python aitrading.py start' to set up and launch")

def setup():
    """Setup system dependencies without starting services"""
    print("🔧 Setting up AI Trading System Dependencies...")
    print("=" * 50)
    
    setup_status = setup_system_dependencies(REACT_DASHBOARD_DIR, interactive=True)
    
    print("\n" + "=" * 50)
    print("🎯 Setup Complete!")
    print("=" * 50)
    
    if all(setup_status.values()):
        print("✅ All dependencies are ready!")
        print("   Run 'python aitrading.py start' to launch the system")
    else:
        print("⚠️  Some dependencies are missing:")
        if not setup_status['python_requirements']:
            print("   • Python requirements: Run 'pip install -r requirements.txt'")
        if not setup_status['mongodb']:
            print("   • MongoDB: Visit https://www.mongodb.com/try/download/community for installation")
        if not setup_status['nodejs']:
            print("   • Node.js: Visit https://nodejs.org/ for installation")
        if not setup_status['react_dependencies']:
            print("   • React dependencies: Run 'npm install' in services/trading-dashboard/")

def restart_all():
    """Restart all AI trading system services"""
    print("🔄 Restarting AI Trading System...")
    print("=" * 50)
    
    # First stop all services
    print("🛑 Stopping all services...")
    stop_all()
    
    # Wait a moment for processes to fully terminate
    time.sleep(2)
    
    # Optionally initialize the trading system (uncomment if needed)
    # print("\n🔧 Initializing trading system...")
    # subprocess.run(['python3', 'initialize_trading_system.py'], check=True)
    
    # Then start all services
    print("\n🚀 Starting all services...")
    start_all()

def main():
    """Main entry point"""
    if len(sys.argv) != 2 or sys.argv[1] not in ('start', 'stop', 'status', 'setup', 'restart'):
        print("Usage: python aitrading.py [start|stop|status|setup|restart]")
        print("\nCommands:")
        print("  start   - Start all AI trading services")
        print("  stop    - Stop all AI trading services") 
        print("  restart - Restart all AI trading services")
        print("  status  - Check status of all services")
        print("  setup   - Setup system dependencies only")
        sys.exit(1)
        
    if sys.argv[1] == 'start':
        start_all()
    elif sys.argv[1] == 'stop':
        stop_all()
    elif sys.argv[1] == 'restart':
        restart_all()
    elif sys.argv[1] == 'status':
        status()
    elif sys.argv[1] == 'setup':
        setup()

if __name__ == '__main__':
    main()