"""
Fabric analyzer module for the Active Inference YouTube Channel Analyzer.

This module handles AI pattern analysis of video transcripts using Fabric
with hierarchical output structure (individual pattern files per video).
"""

import time
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import VideoData, VideoDataCollection, FabricConfig, ProcessingStats
from utils import find_fabric_binary, run_fabric_command, ensure_directory

logger = logging.getLogger(__name__)


class FabricAnalysisError(Exception):
    """Raised when there's an error in Fabric analysis."""
    pass


class HierarchicalFabricAnalyzer:
    """Handles AI analysis of video transcripts using Fabric patterns with hierarchical file structure."""
    
    def __init__(self, config: FabricConfig, base_output_dir: Path, skip_existing: bool = True):
        """
        Initialize Fabric analyzer with hierarchical structure.
        
        Args:
            config: Fabric configuration
            base_output_dir: Base output directory containing video folders
            skip_existing: Skip analysis if pattern file already exists
        """
        self.config = config
        self.base_output_dir = ensure_directory(base_output_dir)
        self.videos_dir = ensure_directory(base_output_dir / "videos")
        self.fabric_binary_path = config.binary_path or find_fabric_binary()
        self.skip_existing = skip_existing
        
        # Validate patterns
        if not config.patterns:
            raise FabricAnalysisError("No Fabric patterns specified")
        
        logger.info(f"Hierarchical Fabric analyzer initialized")
        logger.info(f"Binary path: {self.fabric_binary_path}")
        logger.info(f"Patterns: {', '.join(config.patterns)}")
        logger.info(f"Skip existing: {self.skip_existing}")
    
    def get_video_dir(self, video_id: str) -> Path:
        """Get directory path for a specific video."""
        return self.videos_dir / video_id
    
    def get_pattern_file_path(self, video_id: str, pattern: str) -> Path:
        """Get file path for storing a pattern analysis result."""
        return self.get_video_dir(video_id) / f"{pattern}.md"
    
    def has_pattern_analysis(self, video_id: str, pattern: str) -> bool:
        """Check if pattern analysis exists for video."""
        pattern_file = self.get_pattern_file_path(video_id, pattern)
        return pattern_file.exists() and pattern_file.stat().st_size > 0
    
    def load_pattern_analysis(self, video_id: str, pattern: str) -> str:
        """
        Load existing pattern analysis from file.
        
        Args:
            video_id: YouTube video ID
            pattern: Fabric pattern name
            
        Returns:
            Pattern analysis text, empty string if not found
        """
        pattern_file = self.get_pattern_file_path(video_id, pattern)
        
        if not pattern_file.exists():
            return ""
        
        try:
            with open(pattern_file, 'r', encoding='utf-8') as f:
                analysis = f.read().strip()
                if analysis:
                    logger.debug(f"Loaded cached {pattern} analysis for {video_id} ({len(analysis)} chars)")
                    return analysis
        except Exception as e:
            logger.warning(f"Error reading {pattern} analysis file for {video_id}: {e}")
        
        return ""
    
    def save_pattern_analysis(self, video_id: str, pattern: str, analysis: str) -> None:
        """
        Save pattern analysis to file in video's directory.
        
        Args:
            video_id: YouTube video ID
            pattern: Fabric pattern name
            analysis: Analysis result text
        """
        if not analysis.strip():
            logger.debug(f"Not saving empty {pattern} analysis for {video_id}")
            return
        
        # Ensure video directory exists
        video_dir = ensure_directory(self.get_video_dir(video_id))
        pattern_file = self.get_pattern_file_path(video_id, pattern)
        
        try:
            with open(pattern_file, 'w', encoding='utf-8') as f:
                # Add header with metadata
                f.write(f"# {pattern.replace('_', ' ').title()} Analysis\n\n")
                f.write(f"**Video ID:** {video_id}  \n")
                f.write(f"**Pattern:** {pattern}  \n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n")
                f.write("---\n\n")
                f.write(analysis)
            logger.debug(f"Saved {pattern} analysis for {video_id} to {pattern_file}")
        except Exception as e:
            logger.error(f"Error saving {pattern} analysis for {video_id}: {e}")
    
    def load_all_pattern_analyses(self, video_id: str, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Load all existing pattern analyses for a video.
        
        Args:
            video_id: YouTube video ID
            patterns: List of patterns to load (defaults to config patterns)
            
        Returns:
            Dictionary containing analysis results from each pattern
        """
        patterns_to_load = patterns or self.config.patterns
        analysis_results = {}
        
        for pattern in patterns_to_load:
            analysis = self.load_pattern_analysis(video_id, pattern)
            if analysis:
                analysis_results[pattern] = analysis
        
        return analysis_results
    
    def analyze_transcript(self, video_id: str, transcript: str, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze transcript using Fabric patterns with caching.
        
        Args:
            video_id: YouTube video ID
            transcript: Video transcript text
            patterns: List of patterns to use (defaults to config patterns)
            
        Returns:
            Dictionary containing analysis results from each pattern
        """
        if not transcript.strip():
            logger.debug("Empty transcript, skipping analysis")
            return {}
        
        patterns_to_use = patterns or self.config.patterns
        analysis_results = {}
        
        # Load existing analyses first
        if self.skip_existing:
            existing_analyses = self.load_all_pattern_analyses(video_id, patterns_to_use)
            analysis_results.update(existing_analyses)
        
        # Determine which patterns need to be run
        patterns_to_run = []
        for pattern in patterns_to_use:
            if not self.skip_existing or not self.has_pattern_analysis(video_id, pattern):
                patterns_to_run.append(pattern)
            elif pattern not in analysis_results:
                # Load the existing analysis
                analysis_results[pattern] = self.load_pattern_analysis(video_id, pattern)
        
        if patterns_to_run:
            logger.info(f"Running {len(patterns_to_run)} new patterns for {video_id}: {', '.join(patterns_to_run)}")
        else:
            logger.info(f"All patterns already exist for {video_id}, skipping analysis")
        
        # Run missing patterns
        for pattern in patterns_to_run:
            try:
                logger.debug(f"Running Fabric pattern: {pattern}")
                result = self._run_pattern(pattern, transcript)
                analysis_results[pattern] = result
                
                # Save individual pattern result
                self.save_pattern_analysis(video_id, pattern, result)
                
                # Brief pause between patterns
                time.sleep(0.5)
                
            except Exception as e:
                error_msg = f"Pattern {pattern} failed: {str(e)}"
                logger.error(error_msg)
                analysis_results[pattern] = f"Error: {error_msg}"
        
        return analysis_results
    
    def _run_pattern(self, pattern: str, transcript: str) -> str:
        """
        Run a single Fabric pattern on transcript.
        
        Args:
            pattern: Fabric pattern name
            transcript: Input transcript
            
        Returns:
            Pattern analysis result
            
        Raises:
            FabricAnalysisError: If pattern execution fails
        """
        for attempt in range(self.config.retry_attempts):
            try:
                args = ["--pattern", pattern]
                result = run_fabric_command(
                    self.fabric_binary_path, 
                    args, 
                    input_text=transcript,
                    timeout=self.config.timeout
                )
                
                output = result.stdout.strip()
                if output:
                    logger.debug(f"Pattern {pattern} completed successfully ({len(output)} chars)")
                    return output
                else:
                    logger.warning(f"Pattern {pattern} returned empty result")
                    return ""
                
            except subprocess.CalledProcessError as e:
                error_msg = f"Pattern {pattern} failed (attempt {attempt + 1}): {e.stderr}"
                logger.warning(error_msg)
                
                if attempt == self.config.retry_attempts - 1:
                    raise FabricAnalysisError(error_msg)
                else:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except subprocess.TimeoutExpired:
                error_msg = f"Pattern {pattern} timed out after {self.config.timeout} seconds"
                logger.error(error_msg)
                raise FabricAnalysisError(error_msg)
                
            except Exception as e:
                error_msg = f"Unexpected error in pattern {pattern}: {str(e)}"
                logger.error(error_msg)
                raise FabricAnalysisError(error_msg)
    
    def analyze_video(self, video: VideoData, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a single video's transcript.
        
        Args:
            video: Video data object
            patterns: Patterns to use (optional)
            
        Returns:
            Analysis results
        """
        if not video.transcript.strip():
            logger.debug(f"No transcript for video {video.video_id}, skipping analysis")
            return {}
        
        logger.info(f"Analyzing video: {video.title}")
        
        try:
            analysis_results = self.analyze_transcript(video.video_id, video.transcript, patterns)
            video.fabric_analysis = analysis_results
            return analysis_results
            
        except Exception as e:
            error_msg = f"Analysis failed for video {video.video_id}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def analyze_videos(self, videos: VideoDataCollection) -> ProcessingStats:
        """
        Analyze videos with Fabric patterns using hierarchical structure.
        
        Args:
            videos: Collection of video data
            
        Returns:
            Processing statistics
        """
        stats = ProcessingStats()
        
        # Filter videos that have transcripts and need analysis
        videos_to_analyze = []
        for video in videos.videos:
            video_dir = self.videos_dir / video.video_id
            transcript_file = video_dir / "transcript.txt"
            
            # Only analyze if transcript exists
            if transcript_file.exists():
                # Check if any pattern files are missing
                needs_analysis = False
                for pattern in self.config.patterns:
                    pattern_file = video_dir / f"{pattern}.md"
                    if not pattern_file.exists():
                        needs_analysis = True
                        break
                
                if needs_analysis or not self.skip_existing:
                    videos_to_analyze.append(video)
                else:
                    stats.cached += 1
            else:
                # Create directory for videos without transcripts too
                ensure_directory(video_dir)
                logger.warning(f"No transcript found for {video.video_id}, skipping Fabric analysis")
        
        if not videos_to_analyze:
            logger.info("No videos to analyze with Fabric")
            return stats
            
        logger.info(f"Analyzing {len(videos_to_analyze)} videos with Fabric patterns")
        logger.info(f"Total patterns per video: {len(self.config.patterns)}")
        logger.info(f"Total pattern analyses to run: {len(videos_to_analyze) * len(self.config.patterns)}")
        
        # Process videos in batches for progress tracking
        batch_size = 5  # Process 5 videos at a time for Fabric analysis
        total_batches = (len(videos_to_analyze) + batch_size - 1) // batch_size
        
        logger.info(f"Processing {len(videos_to_analyze)} videos in {total_batches} batches of {batch_size}")
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(videos_to_analyze))
            batch_videos = videos_to_analyze[start_idx:end_idx]
            
            logger.info(f"=== FABRIC ANALYSIS BATCH {batch_num + 1}/{total_batches} ===")
            logger.info(f"Analyzing videos {start_idx + 1}-{end_idx} of {len(videos_to_analyze)}")
            
            for i, video in enumerate(batch_videos, start_idx + 1):
                video_dir = self.videos_dir / video.video_id
                transcript_file = video_dir / "transcript.txt"
                status_file = video_dir / "processing_status.json"
                
                logger.info(f"Progress: {i}/{len(videos_to_analyze)} ({(i/len(videos_to_analyze)*100):.1f}%) - {video.title}")
                logger.info(f"Analyzing video: {video.title}")
                
                # Load or create status file
                if status_file.exists():
                    with open(status_file, 'r') as f:
                        status = json.load(f)
                else:
                    status = {
                        "video_id": video.video_id,
                        "title": video.title,
                        "processing_started": datetime.now().isoformat(),
                        "transcript_downloaded": transcript_file.exists(),
                        "transcript_error": None,
                        "fabric_analyses_completed": False,
                        "fabric_errors": []
                    }
                
                # Check if all patterns already exist
                all_patterns_exist = all(
                    (video_dir / f"{pattern}.md").exists() 
                    for pattern in self.config.patterns
                )
                
                if all_patterns_exist and self.skip_existing:
                    logger.info(f"✅ All {len(self.config.patterns)} patterns already exist for {video.video_id}, skipping analysis")
                    status["fabric_analyses_completed"] = True
                    with open(status_file, 'w') as f:
                        json.dump(status, f, indent=2)
                    stats.cached += 1
                    continue
                
                # Analyze with each pattern
                video_errors = []
                patterns_completed = []
                patterns_skipped = []
                
                for pattern_idx, pattern in enumerate(self.config.patterns, 1):
                    pattern_file = video_dir / f"{pattern}.md"
                    
                    if pattern_file.exists() and self.skip_existing:
                        logger.info(f"✅ Pattern {pattern} ({pattern_idx}/{len(self.config.patterns)}) already exists for {video.video_id}, skipping")
                        patterns_completed.append(pattern)
                        patterns_skipped.append(pattern)
                        continue
                    
                    try:
                        logger.info(f"🔄 Running Fabric pattern: {pattern} ({pattern_idx}/{len(self.config.patterns)}) for {video.video_id}")
                        
                        # Run Fabric command with pattern
                        with open(transcript_file, 'r', encoding='utf-8') as f:
                            transcript_text = f.read()
                        
                        result = run_fabric_command(
                            self.fabric_binary_path,
                            ["--pattern", pattern],
                            input_text=transcript_text,
                            timeout=self.config.timeout
                        )
                        
                        if result.returncode == 0 and result.stdout.strip():
                            # Save pattern analysis
                            analysis_content = f"# {pattern.replace('_', ' ').title()} Analysis\n\n"
                            analysis_content += f"**Video ID:** {video.video_id}  \n"
                            analysis_content += f"**Pattern:** {pattern}  \n"
                            analysis_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n"
                            analysis_content += "---\n\n"
                            analysis_content += result.stdout.strip()
                            
                            with open(pattern_file, 'w', encoding='utf-8') as f:
                                f.write(analysis_content)
                            
                            patterns_completed.append(pattern)
                            logger.info(f"✅ Successfully completed {pattern} analysis for {video.video_id} ({len(result.stdout.strip())} chars)")
                            
                        else:
                            error_msg = f"Fabric pattern {pattern} failed for {video.video_id}: {result.stderr}"
                            logger.error(f"❌ {error_msg}")
                            video_errors.append(error_msg)
                            
                    except Exception as e:
                        error_msg = f"Exception during {pattern} analysis for {video.video_id}: {str(e)}"
                        logger.error(f"❌ {error_msg}")
                        video_errors.append(error_msg)
                
                # Update status
                status["fabric_analyses_completed"] = len(patterns_completed) == len(self.config.patterns)
                status["patterns_completed"] = patterns_completed
                status["patterns_skipped"] = patterns_skipped
                status["fabric_errors"] = video_errors
                status["fabric_analysis_finished"] = datetime.now().isoformat()
                
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
                
                if video_errors:
                    stats.errors += 1
                    # Create error log file
                    error_file = video_dir / "fabric_errors.txt"
                    with open(error_file, 'w') as f:
                        f.write(f"Fabric analysis errors for {video.video_id}\n")
                        f.write(f"Patterns completed: {patterns_completed}\n")
                        f.write(f"Patterns skipped: {patterns_skipped}\n")
                        f.write(f"Errors:\n")
                        for error in video_errors:
                            f.write(f"  - {error}\n")
                        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    
                    logger.info(f"⚠️  Completed with errors: {len(patterns_completed)}/{len(self.config.patterns)} patterns successful")
                else:
                    stats.completed += 1
                    logger.info(f"✅ Successfully completed all {len(patterns_completed)} patterns for {video.video_id}")
            
            # Batch summary
            logger.info(f"Fabric batch {batch_num + 1} complete. Completed: {stats.completed}, Errors: {stats.errors}, Cached: {stats.cached}")
            logger.info(f"Remaining fabric batches: {total_batches - batch_num - 1}")
        
        logger.info(f"Fabric analysis complete: {stats.completed} completed, {stats.errors} errors, {stats.cached} cached")
        return stats
    
    def get_analysis_summary(self, videos: VideoDataCollection) -> Dict[str, Any]:
        """
        Get summary of analysis coverage across video collection.
        
        Args:
            videos: Video collection to summarize
            
        Returns:
            Analysis summary
        """
        total_videos = len(videos)
        analyzed_videos = 0
        pattern_coverage = {pattern: 0 for pattern in self.config.patterns}
        
        for video in videos:
            if video.fabric_analysis:
                analyzed_videos += 1
                for pattern in self.config.patterns:
                    if pattern in video.fabric_analysis:
                        pattern_coverage[pattern] += 1
        
        return {
            'total_videos': total_videos,
            'analyzed_videos': analyzed_videos,
            'coverage_percentage': (analyzed_videos / total_videos) * 100 if total_videos > 0 else 0,
            'pattern_coverage': pattern_coverage,
            'patterns_configured': self.config.patterns
        }
    
    def extract_insights_across_videos(self, videos: VideoDataCollection, 
                                     pattern: str = "extract_insights") -> List[str]:
        """
        Extract specific insights across all analyzed videos.
        
        Args:
            videos: Video collection
            pattern: Pattern to extract insights from
            
        Returns:
            List of insights
        """
        insights = []
        
        for video in videos:
            if video.fabric_analysis and pattern in video.fabric_analysis:
                analysis = video.fabric_analysis[pattern]
                if analysis and not analysis.startswith("Error:"):
                    # Simple extraction - could be more sophisticated
                    insights.append(f"From '{video.title}': {analysis[:200]}...")
        
        return insights
    
    def get_pattern_results_for_video(self, video: VideoData, pattern: str) -> Optional[str]:
        """
        Get specific pattern results for a video.
        
        Args:
            video: Video data
            pattern: Pattern name
            
        Returns:
            Pattern result or None if not available
        """
        if video.fabric_analysis and pattern in video.fabric_analysis:
            return video.fabric_analysis[pattern]
        
        # Try loading from file if not in memory
        return self.load_pattern_analysis(video.video_id, pattern)
    
    def validate_patterns(self) -> Dict[str, bool]:
        """
        Validate that all configured patterns are available in Fabric.
        
        Returns:
            Dictionary mapping pattern names to validation status
        """
        validation_results = {}
        
        for pattern in self.config.patterns:
            try:
                # Test pattern with minimal input
                args = ["--pattern", pattern, "--listpatterns"]
                result = run_fabric_command(
                    self.fabric_binary_path, 
                    args, 
                    input_text="test",
                    timeout=10
                )
                validation_results[pattern] = True
                logger.debug(f"Pattern {pattern} validated successfully")
                
            except Exception as e:
                validation_results[pattern] = False
                logger.warning(f"Pattern {pattern} validation failed: {e}")
        
        return validation_results 