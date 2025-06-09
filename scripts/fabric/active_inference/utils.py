"""
Utility functions for the Active Inference YouTube Channel Analyzer.

This module contains common helper functions used across the application.
"""

import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)


def extract_video_id_from_url(youtube_url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.
    
    Args:
        youtube_url: YouTube URL in various formats
        
    Returns:
        Video ID if found, None otherwise
    """
    if not youtube_url or not isinstance(youtube_url, str):
        return None
    
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        # Handle YouTube live stream URLs
        r'youtube\.com/live/([a-zA-Z0-9_-]{11})',
        r'www\.youtube\.com/live/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    logger.warning(f"Could not extract video ID from URL: {youtube_url}")
    return None


def parse_youtube_duration(duration_str: str) -> int:
    """
    Parse YouTube duration format (PT1H30M45S) to minutes.
    
    Args:
        duration_str: YouTube duration string
        
    Returns:
        Duration in minutes
    """
    if not duration_str:
        return 0
    
    # Extract hours, minutes, seconds using regex
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 60 + minutes + seconds / 60


def seconds_to_youtube_duration(seconds: int) -> str:
    """
    Convert seconds to YouTube duration format (PT1H30M45S).
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        YouTube duration string
    """
    if seconds == 0:
        return ''
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    duration = 'PT'
    if hours > 0:
        duration += f'{hours}H'
    if minutes > 0:
        duration += f'{minutes}M'
    if secs > 0:
        duration += f'{secs}S'
    
    return duration


def parse_date_string(date_str: str) -> str:
    """
    Parse date string from CSV into ISO format.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        ISO format date string
    """
    if not date_str:
        return datetime.now().isoformat()
    
    # Try different date formats
    formats = [
        "%m/%d/%Y %I:%M %p",  # 7/28/2020 10:00 AM
        "%m/%d/%Y",           # 7/28/2020
        "%Y-%m-%d",           # 2020-07-28
        "%Y-%m-%d %H:%M:%S",  # 2020-07-28 10:00:00
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    
    # If parsing fails, return current time
    logger.warning(f"Could not parse date: {date_str}")
    return datetime.now().isoformat()


def find_fabric_binary() -> str:
    """
    Find the Fabric binary location.
    
    Returns:
        Path to Fabric binary
        
    Raises:
        RuntimeError: If Fabric binary not found
    """
    locations = [
        shutil.which("fabric"),
        Path.home() / "go" / "bin" / "fabric",
        "./venv_fabric_foam/bin/fabric"
    ]
    
    for location in locations:
        if location and Path(location).exists():
            return str(location)
    
    raise RuntimeError("Fabric binary not found. Please install Fabric first.")


def run_fabric_command(binary_path: str, args: list, input_text: str = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """
    Run a Fabric command with proper error handling.
    
    Args:
        binary_path: Path to Fabric binary
        args: Command arguments
        input_text: Input text to pass to command
        timeout: Command timeout in seconds
        
    Returns:
        Completed process result
        
    Raises:
        subprocess.CalledProcessError: If command fails
        subprocess.TimeoutExpired: If command times out
    """
    full_args = [binary_path] + args
    
    logger.debug(f"Running Fabric command: {' '.join(full_args)}")
    
    result = subprocess.run(
        full_args,
        input=input_text,
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout
    )
    
    return result


def create_timestamp() -> str:
    """
    Create timestamp string for file naming.
    
    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def safe_filename(text: str, max_length: int = 100) -> str:
    """
    Create safe filename from text.
    
    Args:
        text: Input text
        max_length: Maximum length of filename
        
    Returns:
        Safe filename string
    """
    # Remove or replace unsafe characters
    safe_text = re.sub(r'[<>:"/\\|?*]', '_', text)
    safe_text = re.sub(r'\s+', '_', safe_text)
    safe_text = safe_text.strip('._')
    
    # Truncate if too long
    if len(safe_text) > max_length:
        safe_text = safe_text[:max_length].rstrip('._')
    
    return safe_text or 'unnamed'


def format_number(number: int) -> str:
    """
    Format number with thousands separators.
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string
    """
    return f"{number:,}"


def format_duration(minutes: float) -> str:
    """
    Format duration in minutes to human-readable string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string
    """
    if minutes < 60:
        return f"{minutes:.1f} minutes"
    
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f} hours"
    
    days = hours / 24
    return f"{days:.1f} days"


def calculate_percentage(part: int, total: int) -> float:
    """
    Calculate percentage with division by zero protection.
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        Percentage value
    """
    if total == 0:
        return 0.0
    return (part / total) * 100


def truncate_text(text: str, max_length: int = 300, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_json_string(text: str) -> str:
    """
    Clean text for JSON serialization by handling escape characters.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return text
    
    # Handle common JSON escape sequences
    text = text.replace('\\u0026', '&')
    text = text.replace('\\"', '"')
    text = text.replace('\\/', '/')
    text = text.replace('\\n', '\n')
    text = text.replace('\\t', '\t')
    
    return text


def validate_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format.
    
    Args:
        video_id: Video ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not video_id or not isinstance(video_id, str):
        return False
    
    # YouTube video IDs are 11 characters long and contain letters, numbers, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9_-]{11}$'
    return bool(re.match(pattern, video_id))


def find_foam_root() -> Path:
    """
    Find the Foam project root directory.
    
    Returns:
        Path to Foam root directory
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / "package.json").exists() and (current / "packages" / "foam-vscode").exists():
            return current
        current = current.parent
    return Path.cwd()


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def backup_file(file_path: Path) -> Optional[Path]:
    """
    Create backup of existing file.
    
    Args:
        file_path: File to backup
        
    Returns:
        Path to backup file, None if file doesn't exist
    """
    if not file_path.exists():
        return None
    
    timestamp = create_timestamp()
    backup_path = file_path.with_suffix(f'.{timestamp}.backup')
    
    try:
        shutil.copy2(file_path, backup_path)
        logger.debug(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.warning(f"Failed to create backup of {file_path}: {e}")
        return None 