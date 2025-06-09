"""
Configuration management for the Active Inference YouTube Channel Analyzer.

This module handles loading, validation, and access to configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from models import FabricConfig, ProcessingConfig, VisualizationConfig


class ConfigurationError(Exception):
    """Raised when there's an error in configuration."""
    pass


class Config:
    """Configuration manager for the Active Inference analyzer."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file. Auto-detected if not provided.
        """
        self.config_file = config_file or self._find_config_file()
        self._config_data: Dict[str, Any] = {}
        self._load_config()
        self._validate_config()
    
    def _find_config_file(self) -> Path:
        """Find the configuration file."""
        script_dir = Path(__file__).parent
        possible_files = [
            script_dir / "config.yaml",
            script_dir / "config.yml",
            script_dir / "settings.yaml",
        ]
        
        for config_file in possible_files:
            if config_file.exists():
                return config_file
        
        raise ConfigurationError("Could not find configuration file")
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {self.config_file}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing configuration file: {e}")
    
    def _validate_config(self) -> None:
        """Validate configuration structure and values."""
        required_sections = ['data', 'output', 'processing', 'fabric', 'visualization', 'reporting']
        
        for section in required_sections:
            if section not in self._config_data:
                raise ConfigurationError(f"Missing required configuration section: {section}")
        
        # Validate data section
        data_config = self._config_data['data']
        if 'csv_file' not in data_config:
            raise ConfigurationError("Missing 'csv_file' in data configuration")
        
        # Validate fabric patterns
        fabric_config = self._config_data['fabric']
        if 'patterns' not in fabric_config or not fabric_config['patterns']:
            raise ConfigurationError("At least one Fabric pattern must be specified")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'data.csv_file')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self._config_data.get(section, {})
    
    @property
    def csv_file_path(self) -> Path:
        """Get CSV file path."""
        csv_file = self.get('data.csv_file')
        if not csv_file:
            raise ConfigurationError("CSV file not specified in configuration")
        
        # If relative path, make it relative to config file directory
        csv_path = Path(csv_file)
        if not csv_path.is_absolute():
            csv_path = self.config_file.parent / csv_path
        
        if not csv_path.exists():
            raise ConfigurationError(f"CSV file not found: {csv_path}")
        
        return csv_path
    
    @property
    def output_directory(self) -> Path:
        """Get output directory path."""
        base_dir = self.get('output.base_directory', 'output')
        output_path = Path(base_dir)
        
        # If relative path, make it relative to config file directory
        if not output_path.is_absolute():
            output_path = self.config_file.parent / output_path
        
        return output_path
    
    @property
    def youtube_api_key(self) -> Optional[str]:
        """Get YouTube API key from config or environment."""
        # Check environment variable first
        api_key = os.getenv('YOUTUBE_API_KEY')
        if api_key:
            return api_key
        
        # Check configuration file
        return self.get('data.youtube_api_key')
    
    @property
    def fabric_binary_path(self) -> Optional[str]:
        """Get Fabric binary path."""
        return self.get('fabric.binary_path')
    
    def get_fabric_config(self) -> FabricConfig:
        """Get Fabric configuration object."""
        fabric_section = self.get_section('fabric')
        return FabricConfig(
            binary_path=fabric_section.get('binary_path'),
            patterns=fabric_section.get('patterns', []),
            timeout=fabric_section.get('timeout', 300),
            retry_attempts=fabric_section.get('retry_attempts', 3)
        )
    
    def get_processing_config(self) -> ProcessingConfig:
        """Get processing configuration object."""
        processing_section = self.get_section('processing')
        return ProcessingConfig(
            max_videos=processing_section.get('max_videos'),
            force_download_transcripts=processing_section.get('force_download_transcripts', False),
            transcript_batch_size=processing_section.get('transcript_batch_size', 10),
            rate_limit_delay=processing_section.get('rate_limit_delay', 2.0)
        )
    
    def get_visualization_config(self) -> VisualizationConfig:
        """Get visualization configuration object."""
        viz_section = self.get_section('visualization')
        return VisualizationConfig(
            chart_types=viz_section.get('chart_types', []),
            style=viz_section.get('style', 'default'),
            color_palette=viz_section.get('color_palette', 'husl'),
            dpi=viz_section.get('dpi', 300),
            figure_format=viz_section.get('figure_format', 'png')
        )
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_config = self.get_section('logging')
        
        level = getattr(logging, log_config.get('level', 'INFO').upper())
        format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create logs directory
        logs_dir = self.output_directory / self.get('output.subdirectories.logs', 'logs')
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_file = logs_dir / f"active_inference_analysis_{self._get_timestamp()}.log"
        
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
        
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=handlers,
            force=True  # Override any existing configuration
        )
    
    def _get_timestamp(self) -> str:
        """Get timestamp for file naming."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def get_subdirectory(self, name: str) -> Path:
        """Get path to a specific output subdirectory."""
        subdir_name = self.get(f'output.subdirectories.{name}', name)
        subdir_path = self.output_directory / subdir_name
        subdir_path.mkdir(parents=True, exist_ok=True)
        return subdir_path
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(config_file={self.config_file})"


# Global configuration instance
_global_config: Optional[Config] = None


def get_config(config_file: Optional[Path] = None) -> Config:
    """
    Get global configuration instance.
    
    Args:
        config_file: Path to configuration file (only used on first call)
        
    Returns:
        Configuration instance
    """
    global _global_config
    
    if _global_config is None:
        _global_config = Config(config_file)
    
    return _global_config


def reload_config(config_file: Optional[Path] = None) -> Config:
    """
    Reload configuration from file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        New configuration instance
    """
    global _global_config
    _global_config = Config(config_file)
    return _global_config


def load_config(config_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration as dictionary for backwards compatibility.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_path = config_file or Path(__file__).parent / "config.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Error parsing configuration file: {e}") 