"""
System Setup Utilities for AI Trading Agent

This module handles automatic installation of system dependencies including:
- Node.js and npm
- Python requirements
- System package managers detection
"""

import subprocess
import platform
import os
import sys

def get_system_info():
    """Get system information for package installation"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'darwin':  # macOS
        return 'macos'
    elif system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    else:
        return 'unknown'

def check_package_manager():
    """Check which package manager is available"""
    managers = []
    
    # Check for common package managers
    package_managers = [
        ('brew', ['brew', '--version']),
        ('apt', ['apt', '--version']),
        ('dnf', ['dnf', '--version']),
        ('yum', ['yum', '--version']),
        ('pacman', ['pacman', '--version']),
        ('zypper', ['zypper', '--version']),
        ('choco', ['choco', '--version']),
        ('winget', ['winget', '--version'])
    ]
    
    for manager, cmd in package_managers:
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            managers.append(manager)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    return managers

def check_node_installed():
    """Check if Node.js and npm are installed"""
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, check=True, text=True)
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, check=True, text=True)
        
        node_version = node_result.stdout.strip()
        npm_version = npm_result.stdout.strip()
        
        print(f"✅ Node.js {node_version} found")
        print(f"✅ npm {npm_version} found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_nodejs():
    """Attempt to install Node.js automatically"""
    print("🔧 Attempting to install Node.js...")
    
    system = get_system_info()
    package_managers = check_package_manager()
    
    # macOS installation
    if system == 'macos':
        if 'brew' in package_managers:
            print("📦 Installing Node.js via Homebrew...")
            try:
                subprocess.run(['brew', 'install', 'node'], check=True)
                print("✅ Node.js installed successfully via Homebrew")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via Homebrew: {e}")
        else:
            print("⚠️  Homebrew not found. Please install Homebrew first or use the official installer.")
    
    # Linux installation
    elif system == 'linux':
        if 'apt' in package_managers:
            print("📦 Installing Node.js via APT...")
            try:
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'nodejs', 'npm'], check=True)
                print("✅ Node.js installed successfully via APT")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via APT: {e}")
        
        elif 'dnf' in package_managers:
            print("📦 Installing Node.js via DNF...")
            try:
                subprocess.run(['sudo', 'dnf', 'install', '-y', 'nodejs', 'npm'], check=True)
                print("✅ Node.js installed successfully via DNF")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via DNF: {e}")
        
        elif 'yum' in package_managers:
            print("📦 Installing Node.js via YUM...")
            try:
                subprocess.run(['sudo', 'yum', 'install', '-y', 'nodejs', 'npm'], check=True)
                print("✅ Node.js installed successfully via YUM")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via YUM: {e}")
        
        elif 'pacman' in package_managers:
            print("📦 Installing Node.js via Pacman...")
            try:
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'nodejs', 'npm'], check=True)
                print("✅ Node.js installed successfully via Pacman")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via Pacman: {e}")
        
        elif 'zypper' in package_managers:
            print("📦 Installing Node.js via Zypper...")
            try:
                subprocess.run(['sudo', 'zypper', 'install', '-y', 'nodejs', 'npm'], check=True)
                print("✅ Node.js installed successfully via Zypper")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via Zypper: {e}")
    
    # Windows installation
    elif system == 'windows':
        if 'choco' in package_managers:
            print("📦 Installing Node.js via Chocolatey...")
            try:
                subprocess.run(['choco', 'install', 'nodejs', '-y'], check=True)
                print("✅ Node.js installed successfully via Chocolatey")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via Chocolatey: {e}")
        
        elif 'winget' in package_managers:
            print("📦 Installing Node.js via Winget...")
            try:
                subprocess.run(['winget', 'install', 'OpenJS.NodeJS'], check=True)
                print("✅ Node.js installed successfully via Winget")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js via Winget: {e}")
    
    # If automatic installation fails, provide manual instructions
    print("❌ Automatic Node.js installation failed or not supported on this system")
    print_manual_nodejs_instructions(system)
    return False

def print_manual_nodejs_instructions(system):
    """Print manual installation instructions for Node.js"""
    print("\n📋 Manual Installation Instructions:")
    print("   • Visit: https://nodejs.org/")
    print("   • Download the LTS version for your operating system")
    print("   • Follow the installation instructions")
    print("   • Restart your terminal after installation")
    
    if system == 'macos':
        print("\n🍺 macOS Options:")
        print("   • Homebrew: brew install node")
        print("   • Official installer: https://nodejs.org/")
        print("   • MacPorts: sudo port install nodejs18")
    elif system == 'linux':
        print("\n🐧 Linux Options:")
        print("   • Ubuntu/Debian: sudo apt install nodejs npm")
        print("   • RHEL/CentOS/Fedora: sudo dnf install nodejs npm")
        print("   • Arch Linux: sudo pacman -S nodejs npm")
        print("   • openSUSE: sudo zypper install nodejs npm")
        print("   • Official installer: https://nodejs.org/")
    elif system == 'windows':
        print("\n🪟 Windows Options:")
        print("   • Official installer: https://nodejs.org/")
        print("   • Chocolatey: choco install nodejs")
        print("   • Winget: winget install OpenJS.NodeJS")
        print("   • Scoop: scoop install nodejs")

def check_mongodb_installed():
    """Check if MongoDB is installed and running"""
    try:
        # Check if mongod is installed
        subprocess.run(['mongod', '--version'], capture_output=True, check=True)
        
        # Check if MongoDB is running by trying to connect
        try:
            result = subprocess.run(['mongosh', '--eval', 'db.runCommand("ping")'], 
                                  capture_output=True, check=True, text=True, timeout=5)
            if 'ok' in result.stdout.lower():
                print("✅ MongoDB is installed and running")
                return True
            else:
                print("⚠️  MongoDB is installed but not running")
                return False
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("⚠️  MongoDB is installed but not running or not accessible")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ MongoDB is not installed")
        return False

def install_mongodb():
    """Attempt to install MongoDB automatically"""
    print("🔧 Attempting to install MongoDB...")
    
    system = get_system_info()
    package_managers = check_package_manager()
    
    # macOS installation
    if system == 'macos':
        if 'brew' in package_managers:
            print("📦 Installing MongoDB via Homebrew...")
            try:
                subprocess.run(['brew', 'tap', 'mongodb/brew'], check=True)
                subprocess.run(['brew', 'install', 'mongodb-community'], check=True)
                print("✅ MongoDB installed successfully via Homebrew")
                
                # Start MongoDB service
                print("🚀 Starting MongoDB service...")
                subprocess.run(['brew', 'services', 'start', 'mongodb-community'], check=True)
                print("✅ MongoDB service started")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install MongoDB via Homebrew: {e}")
        else:
            print("⚠️  Homebrew not found. Please install Homebrew first or use the official installer.")
    
    # Linux installation
    elif system == 'linux':
        if 'apt' in package_managers:
            print("📦 Installing MongoDB via APT...")
            try:
                # Import MongoDB GPG key
                subprocess.run(['wget', '-qO', '-', 'https://www.mongodb.org/static/pgp/server-7.0.asc'], 
                             capture_output=True, check=True)
                subprocess.run(['sudo', 'apt-key', 'add', '-'], input=subprocess.PIPE, check=True)
                
                # Add MongoDB repository
                subprocess.run(['echo', 'deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse'], 
                             capture_output=True, check=True)
                
                # Install MongoDB
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'mongodb-org'], check=True)
                
                # Start MongoDB service
                subprocess.run(['sudo', 'systemctl', 'start', 'mongod'], check=True)
                subprocess.run(['sudo', 'systemctl', 'enable', 'mongod'], check=True)
                
                print("✅ MongoDB installed and started successfully via APT")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install MongoDB via APT: {e}")
        
        elif 'dnf' in package_managers:
            print("📦 Installing MongoDB via DNF...")
            try:
                subprocess.run(['sudo', 'dnf', 'install', '-y', 'mongodb-org'], check=True)
                subprocess.run(['sudo', 'systemctl', 'start', 'mongod'], check=True)
                subprocess.run(['sudo', 'systemctl', 'enable', 'mongod'], check=True)
                print("✅ MongoDB installed and started successfully via DNF")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install MongoDB via DNF: {e}")
        
        elif 'pacman' in package_managers:
            print("📦 Installing MongoDB via Pacman...")
            try:
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'mongodb'], check=True)
                subprocess.run(['sudo', 'systemctl', 'start', 'mongodb'], check=True)
                subprocess.run(['sudo', 'systemctl', 'enable', 'mongodb'], check=True)
                print("✅ MongoDB installed and started successfully via Pacman")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install MongoDB via Pacman: {e}")
    
    # Windows installation
    elif system == 'windows':
        if 'choco' in package_managers:
            print("📦 Installing MongoDB via Chocolatey...")
            try:
                subprocess.run(['choco', 'install', 'mongodb', '-y'], check=True)
                print("✅ MongoDB installed successfully via Chocolatey")
                print("🔧 Please start MongoDB service manually from Services panel")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install MongoDB via Chocolatey: {e}")
        
        elif 'winget' in package_managers:
            print("📦 Installing MongoDB via Winget...")
            try:
                subprocess.run(['winget', 'install', 'MongoDB.Server'], check=True)
                print("✅ MongoDB installed successfully via Winget")
                print("🔧 Please start MongoDB service manually from Services panel")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install MongoDB via Winget: {e}")
    
    # If automatic installation fails, provide manual instructions
    print("❌ Automatic MongoDB installation failed or not supported on this system")
    print_manual_mongodb_instructions(system)
    return False

def print_manual_mongodb_instructions(system):
    """Print manual installation instructions for MongoDB"""
    print("\n📋 Manual MongoDB Installation Instructions:")
    print("   • Visit: https://www.mongodb.com/try/download/community")
    print("   • Download MongoDB Community Server for your operating system")
    print("   • Follow the installation instructions")
    print("   • Start MongoDB service")
    
    if system == 'macos':
        print("\n🍺 macOS Options:")
        print("   • Homebrew: brew tap mongodb/brew && brew install mongodb-community")
        print("   • Start service: brew services start mongodb-community")
        print("   • Official installer: https://www.mongodb.com/try/download/community")
    elif system == 'linux':
        print("\n🐧 Linux Options:")
        print("   • Ubuntu/Debian: Follow MongoDB official installation guide")
        print("   • RHEL/CentOS/Fedora: sudo dnf install mongodb-org")
        print("   • Arch Linux: sudo pacman -S mongodb")
        print("   • Start service: sudo systemctl start mongod")
        print("   • Enable service: sudo systemctl enable mongod")
        print("   • Official guide: https://docs.mongodb.com/manual/installation/")
    elif system == 'windows':
        print("\n🪟 Windows Options:")
        print("   • Official installer: https://www.mongodb.com/try/download/community")
        print("   • Chocolatey: choco install mongodb")
        print("   • Start service from Services panel or run: net start MongoDB")
    
    print("\n🔍 Verify Installation:")
    print("   • Test connection: mongosh --eval \"db.runCommand('ping')\"")
    print("   • Check service status (Linux/macOS): sudo systemctl status mongod")

def check_python_requirements():
    """Check if Python requirements are installed"""
    requirements_file = 'requirements.txt'
    
    if not os.path.exists(requirements_file):
        print(f"⚠️  {requirements_file} not found")
        return False
    
    try:
        # Read requirements file
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Check each requirement
        missing_packages = []
        # Map package names to their import names when they differ
        import_name_map = {
            'python-dotenv': 'dotenv',
            'pillow': 'PIL',
            'beautifulsoup4': 'bs4',
            'scikit-learn': 'sklearn',
            'opencv-python': 'cv2',
            'pyopenssl': 'OpenSSL'
        }
        
        for requirement in requirements:
            package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
            # Get the actual import name
            import_name = import_name_map.get(package_name, package_name.replace('-', '_'))
            try:
                __import__(import_name)
            except ImportError:
                missing_packages.append(requirement)
        
        if missing_packages:
            print(f"⚠️  Missing Python packages: {', '.join(missing_packages)}")
            return False
        else:
            print("✅ All Python requirements are satisfied")
            return True
            
    except Exception as e:
        print(f"❌ Error checking requirements: {e}")
        return False

def install_python_requirements():
    """Install Python requirements from requirements.txt"""
    requirements_file = 'requirements.txt'
    
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found")
        return False
    
    print("📦 Installing Python requirements...")
    try:
        # Use pip to install requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], check=True)
        print("✅ Python requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python requirements: {e}")
        return False

def install_react_dependencies(react_dashboard_dir):
    """Install React dashboard dependencies if needed"""
    if not os.path.exists(react_dashboard_dir):
        print(f"❌ React dashboard directory not found: {react_dashboard_dir}")
        return False
    
    node_modules_path = os.path.join(react_dashboard_dir, 'node_modules')
    package_json_path = os.path.join(react_dashboard_dir, 'package.json')
    
    if not os.path.exists(package_json_path):
        print(f"❌ package.json not found in {react_dashboard_dir}")
        return False
    
    if not os.path.exists(node_modules_path):
        print("📦 Installing React dashboard dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=react_dashboard_dir, check=True)
            print("✅ React dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install React dependencies: {e}")
            return False
    else:
        print("✅ React dependencies already installed")
    
    return True

def setup_system_dependencies(react_dashboard_dir, interactive=True):
    """
    Complete system setup including Python, Node.js, and MongoDB dependencies
    
    Args:
        react_dashboard_dir: Path to React dashboard directory
        interactive: Whether to prompt user for installations
    
    Returns:
        dict: Status of each component setup
    """
    setup_status = {
        'python_requirements': False,
        'nodejs': False,
        'react_dependencies': False,
        'mongodb': False
    }
    
    print("🔧 Checking system dependencies...")
    print("=" * 50)
    
    # Check and install Python requirements
    if not check_python_requirements():
        if interactive:
            try:
                response = input("🐍 Install missing Python packages? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    setup_status['python_requirements'] = install_python_requirements()
                else:
                    print("⏭️  Skipping Python requirements installation")
            except KeyboardInterrupt:
                print("\n⏭️  Skipping Python requirements installation")
        else:
            setup_status['python_requirements'] = install_python_requirements()
    else:
        setup_status['python_requirements'] = True
    
    # Check and install MongoDB
    if not check_mongodb_installed():
        if interactive:
            try:
                response = input("🍃 Install MongoDB automatically? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    if install_mongodb():
                        print("🔄 Verifying MongoDB installation...")
                        # Give MongoDB a moment to start
                        import time
                        time.sleep(3)
                        setup_status['mongodb'] = check_mongodb_installed()
                    else:
                        print("❌ MongoDB installation failed")
                else:
                    print("⏭️  Skipping MongoDB installation")
            except KeyboardInterrupt:
                print("\n⏭️  Skipping MongoDB installation")
        else:
            if install_mongodb():
                import time
                time.sleep(3)
                setup_status['mongodb'] = check_mongodb_installed()
    else:
        setup_status['mongodb'] = True
    
    # Check and install Node.js
    if not check_node_installed():
        if interactive:
            try:
                response = input("🟢 Install Node.js automatically? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    if install_nodejs():
                        print("🔄 Verifying Node.js installation...")
                        setup_status['nodejs'] = check_node_installed()
                    else:
                        print("❌ Node.js installation failed")
                else:
                    print("⏭️  Skipping Node.js installation")
            except KeyboardInterrupt:
                print("\n⏭️  Skipping Node.js installation")
        else:
            if install_nodejs():
                setup_status['nodejs'] = check_node_installed()
    else:
        setup_status['nodejs'] = True
    
    # Install React dependencies if Node.js is available
    if setup_status['nodejs']:
        setup_status['react_dependencies'] = install_react_dependencies(react_dashboard_dir)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Setup Summary:")
    print(f"├── Python Requirements: {'✅ Ready' if setup_status['python_requirements'] else '❌ Missing'}")
    print(f"├── MongoDB: {'✅ Ready' if setup_status['mongodb'] else '❌ Missing'}")
    print(f"├── Node.js: {'✅ Ready' if setup_status['nodejs'] else '❌ Missing'}")
    print(f"└── React Dependencies: {'✅ Ready' if setup_status['react_dependencies'] else '❌ Missing'}")
    
    return setup_status

if __name__ == "__main__":
    # Test the setup functions
    print("🧪 Testing system setup utilities...")
    
    # Test system detection
    system = get_system_info()
    print(f"System: {system}")
    
    # Test package manager detection
    managers = check_package_manager()
    print(f"Package managers: {managers}")
    
    # Test Node.js check
    nodejs_available = check_node_installed()
    print(f"Node.js available: {nodejs_available}")
    
    # Test Python requirements check
    python_ok = check_python_requirements()
    print(f"Python requirements satisfied: {python_ok}") 