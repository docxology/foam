"""
Downloader module for the Active Inference YouTube Channel Analyzer.

This module handles transcript downloading, metadata fetching, and caching
with hierarchical output structure (individual folders per video).
"""

import os
import re
import time
import json
import logging
import requests
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import yt_dlp
import requests
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable

from models import VideoData, VideoDataCollection, TranscriptStatus, ProcessingStats
from utils import (
    find_fabric_binary, 
    run_fabric_command, 
    parse_youtube_duration, 
    seconds_to_youtube_duration,
    ensure_directory,
    extract_video_id_from_url
)

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when there's an error downloading content."""
    pass


class HierarchicalTranscriptDownloader:
    """Downloads transcripts using multiple fallback methods for maximum coverage"""
    
    def __init__(self, fabric_binary_path: str, videos_dir: str, 
                 skip_existing: bool = True, rate_limit_delay: int = 1):
        self.fabric_binary_path = fabric_binary_path
        self.videos_dir = Path(videos_dir)
        self.skip_existing = skip_existing
        self.rate_limit_delay = rate_limit_delay
        
        # Statistics tracking
        self.stats = {
            'total_attempted': 0,
            'fabric_success': 0,
            'api_success': 0,
            'ytdlp_success': 0,
            'cached': 0,
            'failed': 0
        }
        
        logger.info("Hierarchical transcript downloader initialized")
        logger.info(f"Videos directory: {self.videos_dir}")
        logger.info(f"Fabric binary: {self.fabric_binary_path}")
        logger.info(f"Skip existing: {self.skip_existing}")

    def _download_transcript_fabric(self, video_url: str, video_id: str) -> Optional[str]:
        """Try downloading transcript using fabric"""
        try:
            logger.debug(f"Trying fabric for {video_id}")
            result = subprocess.run(
                [self.fabric_binary_path, '-y', video_url],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and result.stdout.strip():
                transcript = result.stdout.strip()
                # Check for actual transcript content vs error messages
                if (len(transcript) > 50 and 
                    "transcript not available" not in transcript.lower() and
                    "no transcript" not in transcript.lower() and
                    "(eof)" not in transcript.lower() and
                    not transcript.startswith("error")):
                    logger.debug(f"✅ Fabric success for {video_id}")
                    self.stats['fabric_success'] += 1
                    return transcript
            
            return None
            
        except Exception as e:
            logger.debug(f"Fabric failed for {video_id}: {e}")
            return None

    def _download_transcript_api(self, video_id: str) -> Optional[str]:
        """Try downloading transcript using youtube-transcript-api"""
        try:
            logger.debug(f"Trying YouTube Transcript API for {video_id}")
            
            # First try to get manually created transcripts, then auto-generated
            transcript_list = None
            
            # Try manual transcripts first
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id, 
                    languages=['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
                )
            except:
                # If manual transcripts fail, try auto-generated
                try:
                    all_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                    for transcript in all_transcripts:
                        if transcript.language_code.startswith('en'):
                            transcript_list = transcript.fetch()
                            break
                except:
                    pass
            
            if transcript_list:
                # Combine transcript segments
                transcript = ' '.join([item['text'] for item in transcript_list])
                
                if transcript and len(transcript) > 50:
                    logger.debug(f"✅ API success for {video_id}")
                    self.stats['api_success'] += 1
                    return transcript
            
            return None
            
        except (NoTranscriptFound, VideoUnavailable) as e:
            logger.debug(f"API failed for {video_id}: {e}")
            return None
        except Exception as e:
            logger.debug(f"API exception for {video_id}: {e}")
            return None

    def _download_transcript_ytdlp(self, video_url: str, video_id: str) -> Optional[str]:
        """Try downloading transcript using yt-dlp"""
        try:
            logger.debug(f"Trying yt-dlp for {video_id}")
            
            ydl_opts = {
                'writesubtitles': False,
                'writeautomaticsub': True,  # Enable automatic subtitles
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info
                info = ydl.extract_info(video_url, download=False)
                
                # Check automatic captions first, then manual subtitles
                automatic_captions = info.get('automatic_captions', {})
                subtitles = info.get('subtitles', {})
                
                # Try automatic captions first (more commonly available)
                captions_source = automatic_captions if automatic_captions else subtitles
                
                if captions_source:
                    
                    # Look for English subtitles/captions in order of preference
                    for lang in ['en', 'en-orig', 'en-US', 'en-GB', 'en-CA', 'en-AU']:
                        if lang in captions_source and captions_source[lang]:
                            sub_info = captions_source[lang][0]
                            if 'url' in sub_info:
                                # Download subtitle content
                                response = requests.get(sub_info['url'], timeout=30)
                                if response.status_code == 200:
                                    transcript = self._parse_subtitle_content(response.text)
                                    if transcript and len(transcript) > 50:
                                        logger.debug(f"✅ yt-dlp success for {video_id}")
                                        self.stats['ytdlp_success'] += 1
                                        return transcript
            
            return None
            
        except Exception as e:
            logger.debug(f"yt-dlp failed for {video_id}: {e}")
            return None

    def _parse_subtitle_content(self, content: str) -> Optional[str]:
        """Parse VTT/SRT subtitle content to extract text"""
        try:
            lines = content.split('\n')
            text_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip VTT headers, timestamps, and empty lines
                if (not line or 
                    line.startswith('WEBVTT') or 
                    line.startswith('NOTE') or
                    '-->' in line or
                    line.isdigit() or
                    line.startswith('<') or
                    line.startswith('Kind:') or
                    line.startswith('Language:')):
                    continue
                
                # Clean up common subtitle artifacts
                line = line.replace('<c>', '').replace('</c>', '')
                line = line.replace('&nbsp;', ' ')
                line = line.replace('&amp;', '&')
                line = line.replace('&lt;', '<')
                line = line.replace('&gt;', '>')
                
                if line:
                    text_lines.append(line)
            
            return ' '.join(text_lines) if text_lines else None
            
        except Exception as e:
            logger.debug(f"Error parsing subtitle content: {e}")
            return None

    def download_single_transcript(self, video_url: str, video_id: str, 
                                 video_title: str = "Unknown Title") -> Dict[str, Any]:
        """Download transcript for a single video using all available methods"""
        self.stats['total_attempted'] += 1
        
        # Ensure video directory exists
        video_dir = self.videos_dir / video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        transcript_file = video_dir / "transcript.txt"
        
        # Check if transcript already exists
        if transcript_file.exists() and self.skip_existing:
            logger.debug(f"Transcript already exists for {video_id}, skipping")
            self.stats['cached'] += 1
            return {
                'video_id': video_id,
                'success': True,
                'method': 'cached',
                'transcript_length': len(transcript_file.read_text(encoding='utf-8', errors='ignore')),
                'error': None
            }
        
        transcript = None
        method_used = None
        
        # Method 1: Try Fabric first (usually fastest)
        transcript = self._download_transcript_fabric(video_url, video_id)
        if transcript:
            method_used = 'fabric'
        else:
            logger.debug(f"Fabric failed for {video_id}")
        
        # Method 2: Try YouTube Transcript API
        if not transcript:
            transcript = self._download_transcript_api(video_id)
            if transcript:
                method_used = 'api'
            else:
                logger.debug(f"YouTube API failed for {video_id}")
        
        # Method 3: Try yt-dlp as final fallback
        if not transcript:
            transcript = self._download_transcript_ytdlp(video_url, video_id)
            if transcript:
                method_used = 'ytdlp'
            else:
                logger.debug(f"yt-dlp failed for {video_id}")
        
        # Log what methods were attempted
        if not transcript:
            logger.warning(f"All transcript methods failed for {video_id} ({video_title})")
        
        # Save transcript if we got one
        if transcript:
            try:
                transcript_file.write_text(transcript, encoding='utf-8')
                
                # Also save metadata
                metadata = {
                    'video_id': video_id,
                    'title': video_title,
                    'url': video_url,
                    'transcript_method': method_used,
                    'transcript_length': len(transcript),
                    'download_timestamp': time.time()
                }
                
                metadata_file = video_dir / "metadata.json"
                metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
                
                logger.info(f"✅ Downloaded transcript for {video_id} using {method_used} ({len(transcript)} chars)")
                
                return {
                    'video_id': video_id,
                    'success': True,
                    'method': method_used,
                    'transcript_length': len(transcript),
                    'error': None
                }
                
            except Exception as e:
                logger.error(f"Failed to save transcript for {video_id}: {e}")
                self.stats['failed'] += 1
                return {
                    'video_id': video_id,
                    'success': False,
                    'method': None,
                    'transcript_length': 0,
                    'error': f"Save error: {e}"
                }
        else:
            logger.warning(f"❌ Failed to get transcript for {video_id} with all methods")
            self.stats['failed'] += 1
            return {
                'video_id': video_id,
                'success': False,
                'method': None,
                'transcript_length': 0,
                'error': "All methods failed"
            }

    def download_batch_transcripts(self, videos: List[Dict], batch_size: int = 10) -> Dict[str, Any]:
        """Download transcripts for a batch of videos with improved error handling"""
        total_videos = len(videos)
        logger.info(f"Starting transcript download for {total_videos} videos")
        
        # Find videos that need transcripts
        videos_to_process = []
        for video in videos:
            video_url = video.get('url', '')
            video_id = extract_video_id_from_url(video_url)
            
            if not video_id:
                logger.warning(f"Could not extract video ID from URL: {video_url}")
                continue
                
            video_dir = self.videos_dir / video_id
            transcript_file = video_dir / "transcript.txt"
            
            if not self.skip_existing or not transcript_file.exists():
                videos_to_process.append(video)
            else:
                self.stats['cached'] += 1
        
        logger.info(f"Found {self.stats['cached']} existing transcripts")
        logger.info(f"Downloading transcripts for {len(videos_to_process)} videos")
        
        if not videos_to_process:
            logger.info("No new transcripts to download")
            return self._get_download_summary()
        
        # Process videos in batches
        num_batches = (len(videos_to_process) + batch_size - 1) // batch_size
        logger.info(f"Processing {len(videos_to_process)} videos in {num_batches} batches of {batch_size}")
        
        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(videos_to_process))
            batch_videos = videos_to_process[start_idx:end_idx]
            
            logger.info(f"=== BATCH {batch_num + 1}/{num_batches} ===")
            logger.info(f"Processing videos {start_idx + 1}-{end_idx} of {len(videos_to_process)}")
            
            for i, video in enumerate(batch_videos):
                video_url = video.get('url', '')
                video_id = extract_video_id_from_url(video_url)
                video_title = video.get('title', 'Unknown Title')
                
                current_video = start_idx + i + 1
                logger.info(f"Progress: {current_video}/{len(videos_to_process)} ({current_video/len(videos_to_process)*100:.1f}%) - {video_title}")
                
                try:
                    result = self.download_single_transcript(video_url, video_id, video_title)
                    
                    if not result['success']:
                        logger.warning(f"❌ Failed to download transcript for {video_id}: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    logger.error(f"❌ Exception during transcript download for {video_id}: {e}")
                    self.stats['failed'] += 1
                
                # Rate limiting
                if self.rate_limit_delay > 0:
                    time.sleep(self.rate_limit_delay)
            
            logger.info(f"Batch {batch_num + 1} complete. Downloaded: {self.stats['fabric_success'] + self.stats['api_success'] + self.stats['ytdlp_success']}, Errors: {self.stats['failed']}")
            
            # Brief pause between batches
            if batch_num < num_batches - 1:
                logger.info(f"Remaining batches: {num_batches - batch_num - 1}")
                time.sleep(2)
        
        return self._get_download_summary()

    def _get_download_summary(self) -> Dict[str, Any]:
        """Get download statistics summary"""
        total_successful = self.stats['fabric_success'] + self.stats['api_success'] + self.stats['ytdlp_success'] + self.stats['cached']
        
        summary = {
            'total_attempted': self.stats['total_attempted'],
            'total_successful': total_successful,
            'fabric_success': self.stats['fabric_success'],
            'api_success': self.stats['api_success'],
            'ytdlp_success': self.stats['ytdlp_success'],
            'cached': self.stats['cached'],
            'failed': self.stats['failed'],
            'success_rate': (total_successful / max(self.stats['total_attempted'], 1)) * 100
        }
        
        logger.info("Transcript download complete: {} downloaded, {} cached, {} errors".format(
            self.stats['fabric_success'] + self.stats['api_success'] + self.stats['ytdlp_success'],
            self.stats['cached'],
            self.stats['failed']
        ))
        
        logger.info(f"Method breakdown - Fabric: {self.stats['fabric_success']}, API: {self.stats['api_success']}, yt-dlp: {self.stats['ytdlp_success']}")
        logger.info(f"Overall success rate: {summary['success_rate']:.1f}%")
        
        return summary


class MetadataFetcher:
    """Handles fetching additional video metadata from various sources."""
    
    def __init__(self, youtube_api_key: Optional[str] = None):
        """
        Initialize metadata fetcher.
        
        Args:
            youtube_api_key: YouTube API key for enhanced metadata
        """
        self.youtube_api_key = youtube_api_key
        logger.info(f"Metadata fetcher initialized")
    
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """
        Get video metadata from available sources.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video metadata
        """
        try:
            if self.youtube_api_key:
                return self._get_metadata_via_api(video_id)
            else:
                return self._get_metadata_via_scraping(video_id)
        except Exception as e:
            logger.warning(f"Could not fetch metadata for {video_id}: {e}")
            return {}
    
    def _get_metadata_via_api(self, video_id: str) -> Dict[str, Any]:
        """Get metadata via YouTube Data API."""
        # YouTube API implementation would go here
        # For now, return empty dict
        logger.debug(f"API metadata fetch not implemented for {video_id}")
        return {}
    
    def _get_metadata_via_scraping(self, video_id: str) -> Dict[str, Any]:
        """Get basic metadata via web scraping."""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            # Basic scraping implementation would go here
            # For now, return minimal data
            return {
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.debug(f"Scraping failed for {video_id}: {e}")
            return {}
    
    def enrich_videos_with_metadata(self, videos: VideoDataCollection) -> ProcessingStats:
        """
        Enrich video collection with additional metadata.
        
        Args:
            videos: Video collection to enrich
            
        Returns:
            Processing statistics
        """
        stats = ProcessingStats(start_time=datetime.now())
        
        for video in videos:
            try:
                metadata = self.get_video_metadata(video.video_id)
                # Could merge additional metadata here
                stats.videos_processed += 1
            except Exception as e:
                logger.error(f"Error enriching metadata for {video.video_id}: {e}")
                stats.errors_encountered += 1
        
        stats.end_time = datetime.now()
        return stats 