"""
CSV parser for the Active Inference YouTube Channel Analyzer.

This module handles loading and processing video data from the CSV file.
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict, Any

from models import VideoData, VideoDataCollection
from utils import extract_video_id_from_url, parse_date_string, validate_video_id

logger = logging.getLogger(__name__)


class CSVParsingError(Exception):
    """Raised when there's an error parsing the CSV file."""
    pass


class CSVParser:
    """Parser for Active Inference video information CSV files."""
    
    def __init__(self, csv_file_path: Path):
        """
        Initialize CSV parser.
        
        Args:
            csv_file_path: Path to the CSV file
        """
        self.csv_file_path = csv_file_path
        self.validate_csv_file()
    
    def validate_csv_file(self) -> None:
        """Validate that the CSV file exists and has required columns."""
        if not self.csv_file_path.exists():
            raise CSVParsingError(f"CSV file not found: {self.csv_file_path}")
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                
                required_columns = ['YouTube', 'Title or name of stream']
                missing_columns = [col for col in required_columns if col not in headers]
                
                if missing_columns:
                    raise CSVParsingError(f"Missing required columns: {missing_columns}")
                    
        except csv.Error as e:
            raise CSVParsingError(f"Error reading CSV file: {e}")
        except UnicodeDecodeError as e:
            raise CSVParsingError(f"Encoding error reading CSV file: {e}")
    
    def load_videos(self) -> VideoDataCollection:
        """
        Load video information from CSV file.
        
        Returns:
            Collection of video data
            
        Raises:
            CSVParsingError: If there's an error parsing the CSV
        """
        videos = VideoDataCollection()
        processed_count = 0
        skipped_count = 0
        
        logger.info(f"Loading videos from CSV: {self.csv_file_path}")
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
                    try:
                        video_data = self._parse_video_row(row, row_num)
                        if video_data:
                            videos.add_video(video_data)
                            processed_count += 1
                        else:
                            skipped_count += 1
                    except Exception as e:
                        logger.warning(f"Error parsing row {row_num}: {e}")
                        skipped_count += 1
                        continue
                        
        except Exception as e:
            raise CSVParsingError(f"Error reading CSV file: {e}")
        
        logger.info(f"Loaded {processed_count} videos, skipped {skipped_count} rows")
        return videos
    
    def _parse_video_row(self, row: Dict[str, str], row_num: int) -> VideoData:
        """
        Parse a single CSV row into a VideoData object.
        
        Args:
            row: CSV row data
            row_num: Row number for error reporting
            
        Returns:
            VideoData object, or None if row should be skipped
            
        Raises:
            ValueError: If row data is invalid
        """
        # Extract YouTube URL
        youtube_url = row.get('YouTube', '').strip()
        if not youtube_url:
            logger.debug(f"Row {row_num}: No YouTube URL, skipping")
            return None
        
        # Extract video ID
        video_id = extract_video_id_from_url(youtube_url)
        if not video_id:
            logger.warning(f"Row {row_num}: Could not extract video ID from URL: {youtube_url}")
            return None
        
        # Validate video ID
        if not validate_video_id(video_id):
            logger.warning(f"Row {row_num}: Invalid video ID format: {video_id}")
            return None
        
        # Extract title
        title = row.get('Title or name of stream', '').strip()
        if not title:
            logger.warning(f"Row {row_num}: No title, using video ID")
            title = f"Video {video_id}"
        
        # Parse date
        date_str = row.get('Date', '').strip()
        published_at = parse_date_string(date_str)
        
        # Create description from available fields
        event_name = row.get('Unique event name', '').strip()
        series = row.get('Series', '').strip()
        description_parts = []
        if event_name:
            description_parts.append(f"Event: {event_name}")
        if series:
            description_parts.append(f"Series: {series}")
        description = ", ".join(description_parts) if description_parts else title
        
        # Create VideoData object
        video_data = VideoData(
            video_id=video_id,
            title=title,
            description=description,
            published_at=published_at,
            youtube_url=youtube_url,
            unique_event_name=event_name,
            series=series,
            number=row.get('Number', '').strip(),
            guests=row.get('Guests', '').strip(),
            other_participants=row.get('Other Participants', '').strip()
        )
        
        logger.debug(f"Parsed video: {video_id} - {title}")
        return video_data
    
    def get_csv_summary(self) -> Dict[str, Any]:
        """
        Get summary information about the CSV file.
        
        Returns:
            Summary dictionary with file statistics
        """
        summary = {
            'file_path': str(self.csv_file_path),
            'file_size': self.csv_file_path.stat().st_size,
            'total_rows': 0,
            'columns': [],
            'series_counts': {},
            'date_range': {'earliest': None, 'latest': None}
        }
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                summary['columns'] = list(reader.fieldnames or [])
                
                dates = []
                for row in reader:
                    summary['total_rows'] += 1
                    
                    # Count series
                    series = row.get('Series', '').strip()
                    if series:
                        summary['series_counts'][series] = summary['series_counts'].get(series, 0) + 1
                    
                    # Track dates
                    date_str = row.get('Date', '').strip()
                    if date_str:
                        try:
                            parsed_date = parse_date_string(date_str)
                            dates.append(parsed_date)
                        except:
                            pass
                
                # Determine date range
                if dates:
                    dates.sort()
                    summary['date_range']['earliest'] = dates[0][:10]  # Just the date part
                    summary['date_range']['latest'] = dates[-1][:10]
                    
        except Exception as e:
            logger.error(f"Error generating CSV summary: {e}")
        
        return summary
    
    def validate_video_urls(self) -> Dict[str, Any]:
        """
        Validate all YouTube URLs in the CSV.
        
        Returns:
            Validation results
        """
        results = {
            'total_rows': 0,
            'valid_urls': 0,
            'invalid_urls': 0,
            'missing_urls': 0,
            'duplicate_video_ids': [],
            'invalid_url_examples': []
        }
        
        seen_video_ids = set()
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    results['total_rows'] += 1
                    
                    youtube_url = row.get('YouTube', '').strip()
                    if not youtube_url:
                        results['missing_urls'] += 1
                        continue
                    
                    video_id = extract_video_id_from_url(youtube_url)
                    if not video_id or not validate_video_id(video_id):
                        results['invalid_urls'] += 1
                        if len(results['invalid_url_examples']) < 5:
                            results['invalid_url_examples'].append({
                                'row': row_num,
                                'url': youtube_url,
                                'video_id': video_id
                            })
                        continue
                    
                    if video_id in seen_video_ids:
                        results['duplicate_video_ids'].append({
                            'video_id': video_id,
                            'row': row_num,
                            'url': youtube_url
                        })
                    else:
                        seen_video_ids.add(video_id)
                    
                    results['valid_urls'] += 1
                    
        except Exception as e:
            logger.error(f"Error validating URLs: {e}")
        
        return results

    def load_videos_from_csv(self, csv_file_path: Path) -> VideoDataCollection:
        """
        Load videos from a CSV file (alternative method name for compatibility).
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            Collection of video data
        """
        # Update the internal path and load
        self.csv_file_path = csv_file_path
        self.validate_csv_file()
        return self.load_videos()


def load_videos_from_csv(csv_file_path: Path) -> VideoDataCollection:
    """
    Convenience function to load videos from CSV file.
    
    Args:
        csv_file_path: Path to CSV file
        
    Returns:
        Collection of video data
    """
    parser = CSVParser(csv_file_path)
    return parser.load_videos()


def get_csv_info(csv_file_path: Path) -> Dict[str, Any]:
    """
    Get information about a CSV file without fully parsing it.
    
    Args:
        csv_file_path: Path to CSV file
        
    Returns:
        Information dictionary
    """
    parser = CSVParser(csv_file_path)
    return parser.get_csv_summary()


# Alias for backwards compatibility
VideoCSVParser = CSVParser 