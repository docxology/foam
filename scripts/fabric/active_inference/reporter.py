"""
Report generator module for the Active Inference YouTube Channel Analyzer.

This module handles creating comprehensive analysis reports in various formats.
"""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import VideoData, VideoDataCollection, AnalyticsResult, TranscriptStatus
from utils import (
    create_timestamp, ensure_directory, format_number, format_duration,
    calculate_percentage, truncate_text, parse_youtube_duration
)

logger = logging.getLogger(__name__)


class ReportGenerationError(Exception):
    """Raised when there's an error generating reports."""
    pass


class ReportGenerator:
    """Generates comprehensive analysis reports in multiple formats."""
    
    def __init__(self, output_dir: Path, config: Dict[str, Any] = None):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
            config: Reporting configuration (optional)
        """
        self.output_dir = ensure_directory(output_dir)
        self.config = config or {}
        
        logger.info(f"Report generator initialized")
        logger.info(f"Output directory: {self.output_dir}")
    
    def generate_analytics(self, videos: VideoDataCollection) -> AnalyticsResult:
        """
        Generate comprehensive analytics from video collection.
        
        Args:
            videos: Collection of video data
            
        Returns:
            Analytics results
        """
        if not videos:
            logger.warning("No video data available for analytics")
            return AnalyticsResult()
        
        logger.info(f"Generating analytics for {len(videos)} videos")
        
        # Basic statistics
        total_videos = len(videos)
        total_views = sum(video.view_count for video in videos)
        total_likes = sum(video.like_count for video in videos)
        total_comments = sum(video.comment_count for video in videos)
        total_transcript_length = sum(video.transcript_length for video in videos)
        
        # Duration analysis
        durations = []
        for video in videos:
            if video.duration:
                duration_minutes = parse_youtube_duration(video.duration)
                if duration_minutes > 0:
                    durations.append(duration_minutes)
        
        total_duration_minutes = sum(durations)
        
        # Average statistics
        avg_views = total_views / total_videos if total_videos > 0 else 0
        avg_likes = total_likes / total_videos if total_videos > 0 else 0
        avg_comments = total_comments / total_videos if total_videos > 0 else 0
        avg_transcript_length = total_transcript_length / total_videos if total_videos > 0 else 0
        avg_duration_minutes = total_duration_minutes / len(durations) if durations else 0
        
        # Publication timeline analysis
        dates = []
        for video in videos:
            if video.published_at:
                try:
                    date = datetime.fromisoformat(video.published_at.replace('Z', '+00:00'))
                    dates.append(date)
                except:
                    continue
        
        timeline_analysis = {}
        if dates:
            dates.sort()
            timeline_analysis = {
                'first_video': dates[0].isoformat(),
                'latest_video': dates[-1].isoformat(),
                'channel_age_days': (dates[-1] - dates[0]).days,
                'average_videos_per_month': len(dates) / max(1, (dates[-1] - dates[0]).days / 30)
            }
        
        # Series analysis
        series_stats = videos.get_series_stats()
        
        # Top performing videos
        top_videos_by_views = videos.get_top_by_views(self.config.get('top_videos_count', 10))
        top_videos_by_likes = videos.get_top_by_likes(self.config.get('top_videos_count', 10))
        
        # Create analytics result
        analytics = AnalyticsResult(
            summary={
                'total_videos': total_videos,
                'total_views': total_views,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_transcript_length': total_transcript_length,
                'total_duration_minutes': total_duration_minutes
            },
            averages={
                'avg_views_per_video': round(avg_views, 2),
                'avg_likes_per_video': round(avg_likes, 2),
                'avg_comments_per_video': round(avg_comments, 2),
                'avg_transcript_length': round(avg_transcript_length, 2),
                'avg_duration_minutes': round(avg_duration_minutes, 2)
            },
            timeline=timeline_analysis,
            series_analysis=series_stats,
            top_performers={
                'by_views': [
                    {'title': v.title, 'views': v.view_count, 'series': v.series} 
                    for v in top_videos_by_views
                ],
                'by_likes': [
                    {'title': v.title, 'likes': v.like_count, 'series': v.series} 
                    for v in top_videos_by_likes
                ]
            }
        )
        
        return analytics
    
    def generate_markdown_report(self, videos: VideoDataCollection, 
                                analytics: AnalyticsResult,
                                transcript_status: Optional[TranscriptStatus] = None,
                                csv_file_name: str = "CSV") -> Path:
        """
        Generate comprehensive markdown report.
        
        Args:
            videos: Collection of video data
            analytics: Analytics results
            transcript_status: Transcript status information
            csv_file_name: Name of source CSV file
            
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_content = f"""# Active Inference YouTube Channel Analysis Report

**Generated:** {timestamp}  
**Channel:** http://youtube.com/@activeinference  
**Data Source:** {csv_file_name}  
**Total Videos Analyzed:** {len(videos)}

## Executive Summary

This comprehensive analysis examines the Active Inference YouTube channel using CSV data as the gold standard, providing insights into content patterns, audience engagement, and channel growth metrics.

## Channel Statistics

### Overall Metrics
- **Total Videos:** {format_number(analytics.summary.get('total_videos', 0))}
- **Total Views:** {format_number(analytics.summary.get('total_views', 0))}
- **Total Likes:** {format_number(analytics.summary.get('total_likes', 0))}
- **Total Comments:** {format_number(analytics.summary.get('total_comments', 0))}
- **Total Content Duration:** {analytics.summary.get('total_duration_minutes', 0):.0f} minutes ({analytics.summary.get('total_duration_minutes', 0)/60:.1f} hours)

### Average Performance
- **Average Views per Video:** {format_number(int(analytics.averages.get('avg_views_per_video', 0)))}
- **Average Likes per Video:** {analytics.averages.get('avg_likes_per_video', 0):.0f}
- **Average Comments per Video:** {analytics.averages.get('avg_comments_per_video', 0):.0f}
- **Average Video Duration:** {analytics.averages.get('avg_duration_minutes', 0):.1f} minutes

## Content Analysis

### Transcript Statistics
- **Total Transcript Content:** {format_number(analytics.summary.get('total_transcript_length', 0))} characters
- **Average Transcript Length:** {format_number(int(analytics.averages.get('avg_transcript_length', 0)))} characters per video
"""

        # Publication timeline
        if analytics.timeline:
            timeline = analytics.timeline
            report_content += f"""
### Publication Timeline
- **Channel Active Since:** {timeline.get('first_video', 'N/A')[:10]}
- **Latest Video:** {timeline.get('latest_video', 'N/A')[:10]}
- **Channel Age:** {timeline.get('channel_age_days', 0)} days
- **Average Videos per Month:** {timeline.get('average_videos_per_month', 0):.1f}
"""

        # Series analysis
        if analytics.series_analysis:
            report_content += f"\n### Content Series Analysis\n\n"
            top_series = sorted(
                analytics.series_analysis.items(), 
                key=lambda x: x[1]['count'], 
                reverse=True
            )[:self.config.get('top_series_count', 10)]
            
            for series, stats in top_series:
                report_content += f"- **{series}:** {stats['count']} videos, {format_number(stats['total_views'])} total views\n"

        # Top performing videos
        if analytics.top_performers.get('by_views'):
            report_content += "\n## Top Performing Videos (by Views)\n\n"
            for i, video in enumerate(analytics.top_performers['by_views'][:5], 1):
                report_content += f"{i}. **{video['title']}** ({video['series']}) - {format_number(video['views'])} views\n"

        # Fabric analysis insights
        if self.config.get('include_sample_analysis', True):
            videos_with_analysis = [v for v in videos if v.fabric_analysis]
            if videos_with_analysis:
                report_content += f"\n## AI Content Analysis\n\n"
                report_content += f"**Videos Analyzed with Fabric Patterns:** {len(videos_with_analysis)}\n\n"
                
                # Sample insights from the first analyzed video
                sample_video = videos_with_analysis[0]
                report_content += f"### Sample Analysis: {sample_video.title}\n\n"
                
                max_length = self.config.get('max_sample_length', 300)
                for pattern, result in sample_video.fabric_analysis.items():
                    if result and not result.startswith('Error:'):
                        truncated_result = truncate_text(result, max_length)
                        pattern_title = pattern.replace('_', ' ').title()
                        report_content += f"**{pattern_title}:**\n{truncated_result}\n\n"

        # Transcript status
        if transcript_status:
            report_content += f"""
## Transcript Status

- **Total Videos in CSV:** {transcript_status.total_videos}
- **Videos with Transcripts:** {transcript_status.with_transcripts}
- **Videos without Transcripts:** {transcript_status.without_transcripts}
- **Transcript Coverage:** {transcript_status.coverage_percentage:.1f}%
"""

        report_content += f"""
## Data Files

Raw data has been saved in multiple formats:
- JSON format with complete data including transcripts and analysis
- CSV format with summary statistics for easy import into other tools

## Methodology

This analysis was conducted using:
- **CSV Gold Standard Data** from Active Inference community curation
- **Fabric AI Framework** for transcript extraction and content analysis
- **Intelligent Caching** to avoid re-downloading existing transcripts
- **Statistical Analysis** using Python pandas and matplotlib
- **Content Analysis** using various Fabric patterns including summarization, wisdom extraction, and insight analysis

---

*This report was generated automatically using the Fabric Active Inference Analyzer v2.0.*
*For questions or additional analysis, please refer to the detailed data files and visualizations.*
"""
        
        # Save the report
        timestamp_str = create_timestamp()
        report_file = self.output_dir / f"active_inference_analysis_report_{timestamp_str}.md"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Markdown report saved: {report_file}")
            return report_file
        except Exception as e:
            raise ReportGenerationError(f"Failed to save markdown report: {e}")
    
    def save_data_files(self, videos: VideoDataCollection, analytics: AnalyticsResult) -> Dict[str, Path]:
        """
        Save data in multiple formats.
        
        Args:
            videos: Collection of video data
            analytics: Analytics results
            
        Returns:
            Dictionary mapping format names to file paths
        """
        timestamp = create_timestamp()
        saved_files = {}
        
        # JSON format (complete data)
        if self.config.get('generate_json_summary', True):
            json_file = self.output_dir / f"active_inference_videos_{timestamp}.json"
            try:
                data_to_save = {
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'total_videos': len(videos),
                        'analyzer_version': '2.0.0'
                    },
                    'analytics': analytics.to_dict(),
                    'videos': videos.to_dict_list()
                }
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
                saved_files['json'] = json_file
                logger.info(f"JSON data saved: {json_file}")
                
            except Exception as e:
                logger.error(f"Failed to save JSON data: {e}")
        
        # CSV format (summary data)
        csv_file = self.output_dir / f"active_inference_summary_{timestamp}.csv"
        try:
            csv_data = []
            
            for video in videos:
                csv_data.append({
                    'video_id': video.video_id,
                    'title': video.title,
                    'published_at': video.published_at,
                    'duration': video.duration,
                    'view_count': video.view_count,
                    'like_count': video.like_count,
                    'comment_count': video.comment_count,
                    'transcript_length': video.transcript_length,
                    'unique_event_name': video.unique_event_name,
                    'series': video.series,
                    'number': video.number,
                    'guests': video.guests,
                    'other_participants': video.other_participants,
                    'youtube_url': video.youtube_url
                })
            
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_file, index=False)
            
            saved_files['csv'] = csv_file
            logger.info(f"CSV summary saved: {csv_file}")
            
        except Exception as e:
            logger.error(f"Failed to save CSV data: {e}")
        
        return saved_files
    
    def create_executive_summary(self, analytics: AnalyticsResult) -> Dict[str, Any]:
        """
        Create executive summary of key metrics.
        
        Args:
            analytics: Analytics results
            
        Returns:
            Executive summary dictionary
        """
        summary = analytics.summary
        averages = analytics.averages
        
        # Calculate engagement rate
        total_views = summary.get('total_views', 0)
        total_likes = summary.get('total_likes', 0)
        engagement_rate = calculate_percentage(total_likes, total_views) if total_views > 0 else 0
        
        # Calculate content metrics
        total_duration_hours = summary.get('total_duration_minutes', 0) / 60
        content_per_week = 0
        if analytics.timeline and analytics.timeline.get('channel_age_days', 0) > 0:
            weeks = analytics.timeline['channel_age_days'] / 7
            content_per_week = summary.get('total_videos', 0) / weeks
        
        executive_summary = {
            'key_metrics': {
                'total_videos': summary.get('total_videos', 0),
                'total_views': summary.get('total_views', 0),
                'total_hours_content': round(total_duration_hours, 1),
                'engagement_rate_percent': round(engagement_rate, 2),
                'average_views_per_video': int(averages.get('avg_views_per_video', 0)),
                'content_per_week': round(content_per_week, 2)
            },
            'top_series': [],
            'growth_metrics': {},
            'content_insights': {}
        }
        
        # Add top series
        if analytics.series_analysis:
            sorted_series = sorted(
                analytics.series_analysis.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:3]
            
            executive_summary['top_series'] = [
                {
                    'name': series,
                    'video_count': stats['count'],
                    'total_views': stats['total_views']
                }
                for series, stats in sorted_series
            ]
        
        return executive_summary

    def generate_json_report(self, videos: VideoDataCollection, analytics: AnalyticsResult) -> Path:
        """
        Generate JSON report file.
        
        Args:
            videos: Video collection
            analytics: Analytics results
            
        Returns:
            Path to JSON file
        """
        saved_files = self.save_data_files(videos, analytics)
        return saved_files.get('json', Path())

    def generate_csv_summary(self, videos: VideoDataCollection) -> Path:
        """
        Generate CSV summary file.
        
        Args:
            videos: Video collection
            
        Returns:
            Path to CSV file
        """
        # Create dummy analytics for save_data_files
        analytics = AnalyticsResult()
        saved_files = self.save_data_files(videos, analytics)
        return saved_files.get('csv', Path())


# Alias for backwards compatibility
AnalysisReporter = ReportGenerator 