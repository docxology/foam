"""
Active Inference YouTube Channel Analyzer

A comprehensive toolkit for analyzing the Active Inference YouTube channel using Fabric AI.
"""

__version__ = "2.0.0"
__author__ = "AI Assistant"

from .models import VideoData, VideoDataCollection
from .config import get_config
from .csv_parser import load_videos_from_csv
from .downloader import TranscriptDownloader, MetadataFetcher
from .fabric_analyzer import FabricAnalyzer
from .visualizer import DataVisualizer
from .reporter import ReportGenerator

__all__ = [
    'VideoData',
    'VideoDataCollection', 
    'get_config',
    'load_videos_from_csv',
    'TranscriptDownloader',
    'MetadataFetcher',
    'FabricAnalyzer',
    'DataVisualizer',
    'ReportGenerator'
] 