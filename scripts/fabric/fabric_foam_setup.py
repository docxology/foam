#!/usr/bin/env python3
"""
Fabric and Foam Setup Script

This script clones the Fabric repository, sets up a virtual environment,
and installs both local Foam and Fabric with comprehensive logging and status reporting.

Author: AI Assistant
Version: 1.0.0
"""

import os
import sys
import subprocess
import logging
import tempfile
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class FabricFoamSetup:
    """
    A comprehensive setup manager for Fabric and Foam integration.
    
    This class handles the complete setup process including:
    - Repository cloning
    - Virtual environment creation
    - Package installation
    - Version verification
    - Status reporting
    """
    
    def __init__(self, work_dir: Optional[Path] = None):
        """
        Initialize the setup manager.
        
        Args:
            work_dir: Working directory for setup operations. Defaults to current directory.
        """
        self.work_dir = Path(work_dir or os.getcwd())
        self.foam_root = self._find_foam_root()
        self.venv_path = self.work_dir / "venv_fabric_foam"
        self.fabric_repo_path = self.work_dir / "fabric"
        self.fabric_repo_url = "https://github.com/danielmiessler/fabric.git"
        
        # Setup logging
        self._setup_logging()
        
    def _find_foam_root(self) -> Path:
        """Find the Foam project root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / "package.json").exists() and (current / "packages" / "foam-vscode").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _setup_logging(self) -> None:
        """Configure comprehensive logging with both file and console output."""
        log_dir = self.work_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"fabric_foam_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logging initialized. Log file: {log_file}")
    
    def _run_command(self, command: list[str], cwd: Optional[Path] = None, 
                    capture_output: bool = True) -> subprocess.CompletedProcess:
        """
        Execute a command with comprehensive logging and error handling.
        
        Args:
            command: Command to execute as list of strings
            cwd: Working directory for command execution
            capture_output: Whether to capture command output
            
        Returns:
            CompletedProcess object with execution results
            
        Raises:
            subprocess.CalledProcessError: If command execution fails
        """
        cmd_str = " ".join(command)
        self.logger.debug(f"Executing command: {cmd_str}")
        self.logger.debug(f"Working directory: {cwd or 'current'}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                check=True
            )
            
            if capture_output:
                self.logger.debug(f"Command output: {result.stdout}")
                if result.stderr:
                    self.logger.warning(f"Command stderr: {result.stderr}")
            
            self.logger.info(f"Command executed successfully: {cmd_str}")
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {cmd_str}")
            self.logger.error(f"Return code: {e.returncode}")
            self.logger.error(f"Stdout: {e.stdout}")
            self.logger.error(f"Stderr: {e.stderr}")
            raise
    
    def clone_fabric_repository(self) -> None:
        """Clone the Fabric repository from GitHub."""
        self.logger.info("Starting Fabric repository clone...")
        
        if self.fabric_repo_path.exists():
            self.logger.warning(f"Fabric repository already exists at {self.fabric_repo_path}")
            
            # Check if it's a valid git repository
            try:
                self._run_command(["git", "status"], cwd=self.fabric_repo_path)
                self.logger.info("Existing repository is valid, pulling latest changes...")
                self._run_command(["git", "pull"], cwd=self.fabric_repo_path)
            except subprocess.CalledProcessError:
                self.logger.warning("Existing directory is not a valid git repository, removing...")
                shutil.rmtree(self.fabric_repo_path)
                self._clone_fresh_repository()
        else:
            self._clone_fresh_repository()
        
        self.logger.info("Fabric repository clone completed successfully")
    
    def _clone_fresh_repository(self) -> None:
        """Clone a fresh copy of the Fabric repository."""
        self.logger.info(f"Cloning Fabric repository from {self.fabric_repo_url}")
        self._run_command([
            "git", "clone", self.fabric_repo_url, str(self.fabric_repo_path)
        ])
        self.logger.info(f"Repository cloned to {self.fabric_repo_path}")
    
    def setup_virtual_environment(self) -> None:
        """Create and configure a virtual environment for the project."""
        self.logger.info("Setting up virtual environment...")
        
        if self.venv_path.exists():
            self.logger.warning(f"Virtual environment already exists at {self.venv_path}")
            response = input("Remove existing virtual environment? (y/N): ").strip().lower()
            if response == 'y':
                shutil.rmtree(self.venv_path)
                self.logger.info("Existing virtual environment removed")
            else:
                self.logger.info("Using existing virtual environment")
                return
        
        # Create virtual environment
        self.logger.info(f"Creating virtual environment at {self.venv_path}")
        self._run_command([sys.executable, "-m", "venv", str(self.venv_path)])
        
        # Upgrade pip
        self.logger.info("Upgrading pip in virtual environment...")
        pip_path = self.venv_path / ("Scripts" if os.name == "nt" else "bin") / "pip"
        self._run_command([str(pip_path), "install", "--upgrade", "pip"])
        
        self.logger.info("Virtual environment setup completed successfully")
    
    def install_fabric(self) -> None:
        """Install Fabric from the cloned repository."""
        self.logger.info("Installing Fabric...")
        
        # Check if Go is installed
        try:
            result = self._run_command(["go", "version"])
            self.logger.info(f"Go version: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            self.logger.error("Go is not installed. Please install Go first.")
            self.logger.info("Visit https://go.dev/doc/install for installation instructions.")
            raise RuntimeError("Go is required to install Fabric")
        
        # Install Fabric using Go
        try:
            self.logger.info("Installing Fabric directly from the repository...")
            self._run_command([
                "go", "install", "github.com/danielmiessler/fabric@latest"
            ])
            self.logger.info("Fabric installation completed successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error("Failed to install Fabric using 'go install'")
            self.logger.info("Attempting to build from source...")
            
            # Fallback: build from source
            try:
                self._run_command(["go", "build", "-o", "fabric"], cwd=self.fabric_repo_path)
                
                # Move the binary to a location in PATH or create a symlink
                fabric_binary = self.fabric_repo_path / "fabric"
                if fabric_binary.exists():
                    # Create a bin directory in the virtual environment
                    venv_bin = self.venv_path / "bin"
                    venv_bin.mkdir(exist_ok=True)
                    
                    # Copy the binary
                    shutil.copy2(fabric_binary, venv_bin / "fabric")
                    self.logger.info(f"Fabric binary installed to {venv_bin / 'fabric'}")
                else:
                    raise RuntimeError("Failed to build Fabric binary")
                    
            except subprocess.CalledProcessError:
                self.logger.error("Failed to build Fabric from source")
                raise
    
    def install_foam_dependencies(self) -> None:
        """Install Foam dependencies if available."""
        self.logger.info("Installing Foam dependencies...")
        
        foam_requirements = self.foam_root / "requirements.txt"
        pip_path = self.venv_path / ("Scripts" if os.name == "nt" else "bin") / "pip"
        
        if foam_requirements.exists():
            self.logger.info(f"Installing from {foam_requirements}")
            self._run_command([
                str(pip_path), "install", "-r", str(foam_requirements)
            ])
        else:
            self.logger.info("No requirements.txt found for Foam, installing basic dependencies...")
            # Install common dependencies that might be needed
            common_deps = ["requests", "pyyaml", "click", "rich"]
            for dep in common_deps:
                try:
                    self._run_command([str(pip_path), "install", dep])
                except subprocess.CalledProcessError:
                    self.logger.warning(f"Failed to install {dep}")
        
        self.logger.info("Foam dependencies installation completed")
    
    def verify_installation(self) -> Dict[str, Any]:
        """
        Verify the installation and collect version information.
        
        Returns:
            Dictionary containing version and status information
        """
        self.logger.info("Verifying installation...")
        
        python_path = self.venv_path / ("Scripts" if os.name == "nt" else "bin") / "python"
        pip_path = self.venv_path / ("Scripts" if os.name == "nt" else "bin") / "pip"
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "setup_successful": True,
            "versions": {},
            "paths": {
                "venv": str(self.venv_path),
                "fabric_repo": str(self.fabric_repo_path),
                "foam_root": str(self.foam_root)
            },
            "errors": []
        }
        
        try:
            # Python version
            result = self._run_command([str(python_path), "--version"])
            status["versions"]["python"] = result.stdout.strip()
            
            # Pip version
            result = self._run_command([str(pip_path), "--version"])
            status["versions"]["pip"] = result.stdout.strip()
            
            # Go version
            try:
                result = self._run_command(["go", "version"])
                status["versions"]["go"] = result.stdout.strip()
            except subprocess.CalledProcessError:
                status["errors"].append("Go not found in PATH")
            
            # List installed Python packages
            result = self._run_command([str(pip_path), "list", "--format=json"])
            installed_packages = json.loads(result.stdout)
            status["installed_packages"] = {pkg["name"]: pkg["version"] for pkg in installed_packages}
            
            # Check for Fabric binary
            fabric_locations = [
                # Check in system PATH
                shutil.which("fabric"),
                # Check in Go bin
                Path.home() / "go" / "bin" / "fabric",
                # Check in venv bin
                self.venv_path / "bin" / "fabric"
            ]
            
            fabric_found = False
            for location in fabric_locations:
                if location and Path(location).exists():
                    try:
                        result = self._run_command([str(location), "--version"])
                        status["fabric_installed"] = True
                        status["versions"]["fabric"] = result.stdout.strip()
                        status["fabric_path"] = str(location)
                        fabric_found = True
                        self.logger.info(f"Fabric found at: {location}")
                        break
                    except subprocess.CalledProcessError:
                        continue
            
            if not fabric_found:
                status["fabric_installed"] = False
                status["errors"].append("Fabric binary not found in expected locations")
                
        except Exception as e:
            self.logger.error(f"Error during verification: {e}")
            status["setup_successful"] = False
            status["errors"].append(str(e))
        
        return status
    
    def generate_status_report(self, status: Dict[str, Any]) -> None:
        """
        Generate and display a comprehensive status report.
        
        Args:
            status: Status information dictionary from verify_installation
        """
        self.logger.info("=" * 60)
        self.logger.info("FABRIC AND FOAM SETUP STATUS REPORT")
        self.logger.info("=" * 60)
        
        self.logger.info(f"Setup Time: {status['timestamp']}")
        self.logger.info(f"Overall Status: {'SUCCESS' if status['setup_successful'] else 'FAILED'}")
        
        if status["errors"]:
            self.logger.error("Errors encountered:")
            for error in status["errors"]:
                self.logger.error(f"  - {error}")
        
        self.logger.info("\nPaths:")
        for path_name, path_value in status["paths"].items():
            self.logger.info(f"  {path_name}: {path_value}")
        
        self.logger.info("\nVersions:")
        for version_name, version_value in status["versions"].items():
            self.logger.info(f"  {version_name}: {version_value}")
        
        if "installed_packages" in status:
            self.logger.info(f"\nTotal Python packages installed: {len(status['installed_packages'])}")
            
            # Show key Python packages
            key_packages = ["requests", "pyyaml", "click", "rich"]
            installed_key = [pkg for pkg in key_packages if pkg in status["installed_packages"]]
            if installed_key:
                self.logger.info("Key Python packages installed:")
                for pkg in installed_key:
                    self.logger.info(f"  {pkg}: {status['installed_packages'][pkg]}")
        
        # Show Fabric installation status
        if status.get("fabric_installed"):
            self.logger.info(f"\nFabric Status: INSTALLED")
            if "fabric_path" in status:
                self.logger.info(f"Fabric Location: {status['fabric_path']}")
        else:
            self.logger.info(f"\nFabric Status: NOT FOUND")
        
        # Show Go status
        if "go" in status.get("versions", {}):
            self.logger.info(f"Go: {status['versions']['go']}")
        else:
            self.logger.info("Go: NOT FOUND")
        
        self.logger.info("=" * 60)
        
        # Save status to file
        status_file = self.work_dir / "fabric_foam_setup_status.json"
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        self.logger.info(f"Detailed status saved to: {status_file}")
    
    def run_complete_setup(self) -> None:
        """Execute the complete setup process."""
        try:
            self.logger.info("Starting Fabric and Foam setup process...")
            
            # Step 1: Clone Fabric repository
            self.clone_fabric_repository()
            
            # Step 2: Setup virtual environment
            self.setup_virtual_environment()
            
            # Step 3: Install Fabric
            self.install_fabric()
            
            # Step 4: Install Foam dependencies
            self.install_foam_dependencies()
            
            # Step 5: Verify installation and generate report
            status = self.verify_installation()
            self.generate_status_report(status)
            
            if status["setup_successful"]:
                self.logger.info("Setup completed successfully!")
                self.logger.info(f"Virtual environment activated with: source {self.venv_path}/bin/activate")
            else:
                self.logger.error("Setup completed with errors. Check the log for details.")
                
        except Exception as e:
            self.logger.error(f"Setup failed with exception: {e}")
            raise


def main():
    """Main entry point for the script."""
    try:
        setup_manager = FabricFoamSetup()
        setup_manager.run_complete_setup()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()