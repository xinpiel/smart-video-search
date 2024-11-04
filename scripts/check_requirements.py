import pkg_resources
import subprocess
import sys

def get_installed_packages():
    """Get dictionary of installed packages and their versions"""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def parse_requirements(filename):
    """Parse requirements file into package name and version"""
    requirements = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle different requirement formats
                if '>=' in line:
                    name = line.split('>=')[0]
                    version = line.split('>=')[1]
                elif '==' in line:
                    name = line.split('==')[0]
                    version = line.split('==')[1]
                else:
                    name = line
                    version = None
                requirements[name.lower()] = version
    return requirements

def check_and_install():
    """Check and install only missing packages"""
    print("Checking installed packages...")
    
    # Get currently installed packages
    installed = get_installed_packages()
    
    # Parse requirements file
    required = parse_requirements('requirements.txt')
    
    # Find missing packages
    to_install = []
    for package, version in required.items():
        if package not in installed:
            if version:
                to_install.append(f"{package}=={version}")
            else:
                to_install.append(package)
            print(f"Missing package: {package}")
    
    # Install missing packages
    if to_install:
        print("\nInstalling missing packages:")
        for package in to_install:
            print(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package}: {e}")
    else:
        print("\nAll required packages are already installed!")

if __name__ == "__main__":
    check_and_install()