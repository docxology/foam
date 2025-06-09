"""
Data models and structures for the Active Inference YouTube Channel Analyzer.

This module defines the core data structures used throughout the analysis pipeline.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json


@dataclass
class VideoData:
    """Data structure for storing comprehensive video information."""
    # Core identifiers
    video_id: str
    title: str
    description: str
    
    # Temporal data
    published_at: str
    
    # Video metrics
    duration: str = ""
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    
    # Content analysis
    transcript: str = ""
    transcript_length: int = 0
    fabric_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # CSV-specific fields
    unique_event_name: str = ""
    series: str = ""
    number: str = ""
    guests: str = ""
    other_participants: str = ""
    youtube_url: str = ""
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.transcript:
            self.transcript_length = len(self.transcript)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoData':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class AnalyticsResult:
    """Container for analytics and statistics."""
    summary: Dict[str, Any] = field(default_factory=dict)
    averages: Dict[str, Any] = field(default_factory=dict)
    timeline: Dict[str, Any] = field(default_factory=dict)
    series_analysis: Dict[str, Any] = field(default_factory=dict)
    top_performers: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class TranscriptStatus:
    """Status information about transcript availability."""
    total_videos: int
    with_transcripts: int
    without_transcripts: int
    videos_needing_transcripts: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def coverage_percentage(self) -> float:
        """Calculate transcript coverage percentage."""
        if self.total_videos == 0:
            return 0.0
        return (self.with_transcripts / self.total_videos) * 100


@dataclass
class ProcessingStats:
    """Statistics about the processing pipeline."""
    videos_processed: int = 0
    transcripts_downloaded: int = 0
    transcripts_cached: int = 0
    fabric_analyses_completed: int = 0
    errors_encountered: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # New attributes for hierarchical processing
    downloaded: int = 0
    cached: int = 0
    completed: int = 0
    errors: int = 0
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate processing duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class VisualizationConfig:
    """Configuration for visualization generation."""
    chart_types: List[str]
    style: str = "default"
    color_palette: str = "husl"
    dpi: int = 300
    figure_format: str = "png"
    output_dir: Optional[Path] = None


@dataclass
class FabricConfig:
    """Configuration for Fabric integration."""
    binary_path: Optional[str] = None
    patterns: List[str] = field(default_factory=list)
    timeout: int = 300
    retry_attempts: int = 3


@dataclass
class ProcessingConfig:
    """Configuration for video processing pipeline."""
    max_videos: Optional[int] = None
    force_download_transcripts: bool = False
    transcript_batch_size: int = 10
    rate_limit_delay: float = 2.0


class VideoDataCollection:
    """Collection of video data with utility methods."""
    
    def __init__(self, videos: List[VideoData] = None):
        """Initialize with optional list of videos."""
        self.videos: List[VideoData] = videos or []
    
    def add_video(self, video: VideoData) -> None:
        """Add a video to the collection."""
        self.videos.append(video)
    
    def get_by_id(self, video_id: str) -> Optional[VideoData]:
        """Get video by ID."""
        for video in self.videos:
            if video.video_id == video_id:
                return video
        return None
    
    def get_by_series(self, series: str) -> List[VideoData]:
        """Get all videos from a specific series."""
        return [video for video in self.videos if video.series == series]
    
    def get_with_transcripts(self) -> List[VideoData]:
        """Get videos that have transcripts."""
        return [video for video in self.videos if video.transcript.strip()]
    
    def get_without_transcripts(self) -> List[VideoData]:
        """Get videos that don't have transcripts."""
        return [video for video in self.videos if not video.transcript.strip()]
    
    def get_top_by_views(self, count: int = 10) -> List[VideoData]:
        """Get top videos by view count."""
        return sorted(self.videos, key=lambda v: v.view_count, reverse=True)[:count]
    
    def get_top_by_likes(self, count: int = 10) -> List[VideoData]:
        """Get top videos by like count."""
        return sorted(self.videos, key=lambda v: v.like_count, reverse=True)[:count]
    
    def get_series_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by series."""
        series_stats = {}
        for video in self.videos:
            series = video.series or 'Unknown'
            if series not in series_stats:
                series_stats[series] = {
                    'count': 0,
                    'total_views': 0,
                    'total_likes': 0,
                    'total_transcript_length': 0
                }
            
            series_stats[series]['count'] += 1
            series_stats[series]['total_views'] += video.view_count
            series_stats[series]['total_likes'] += video.like_count
            series_stats[series]['total_transcript_length'] += video.transcript_length
        
        return series_stats
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert collection to list of dictionaries."""
        return [video.to_dict() for video in self.videos]
    
    def __len__(self) -> int:
        """Return number of videos in collection."""
        return len(self.videos)
    
    def __iter__(self):
        """Make collection iterable."""
        return iter(self.videos)
    
    def __getitem__(self, index):
        """Allow indexing."""
        return self.videos[index] 