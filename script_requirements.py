import subprocess
import sys

def get_missing_packages(file_path):
    pkgs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [p.decode().split('==')[0] for p in pkgs.split()]
    missing_packages = []
    with open(file_path, 'r') as requirements_file:
        for line in requirements_file:
            package_name = line.strip()
            if package_name and not package_name in installed_packages:
                missing_packages.append(package_name)
    return missing_packages

def install_packages_from_requirements(file_path):
    missing_packages = get_missing_packages(file_path)
    if missing_packages:
        print("Installing missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            subprocess.run(["pip", "install", package])

install_packages_from_requirements("requirements.txt")
import script_main
script_main.start()

