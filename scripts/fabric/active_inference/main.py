#!/usr/bin/env python3
"""
Active Inference YouTube Channel Analyzer v2.1.0

A comprehensive, state-of-the-art tool for analyzing YouTube channels focused on Active Inference content.
This version provides advanced analytics, machine learning, and interactive visualizations.

Enhanced Features:
- Advanced statistical analysis (PCA, clustering, time series)
- Natural language processing (sentiment analysis, topic modeling)
- Network analysis and relationship mapping
- Interactive dashboards and visualizations
- Hierarchical output structure with individual video folders
- Intelligent caching and parallel processing
- 20+ Fabric AI patterns for comprehensive content analysis
- Professional reporting and data export in multiple formats

Usage Modes:
- Full pipeline: python main.py
- Transcripts only: python main.py --mode transcripts
- Analysis only: python main.py --mode analysis  
- Visualizations only: python main.py --mode visualization
- Reports only: python main.py --mode reports
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add the current directory to the path for imports
sys.path.append(str(Path(__file__).parent))

from config import load_config
from csv_parser import VideoCSVParser
from downloader import HierarchicalTranscriptDownloader, MetadataFetcher
from fabric_analyzer import HierarchicalFabricAnalyzer
from visualizer import create_visualizations
from reporter import AnalysisReporter
from models import FabricConfig, ProcessingConfig


def setup_logging(config: dict) -> None:
    """Setup logging configuration."""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO').upper())
    format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logs directory
    output_config = config.get('output', {})
    base_dir = Path(output_config.get('base_dir', 'output'))
    logs_dir = base_dir / output_config.get('structure', {}).get('logs_dir', 'logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup file logging
    log_filename = logs_dir / f"{log_config.get('file_prefix', 'analysis')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Active Inference YouTube Channel Analyzer v2.1.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Run full analysis pipeline
  python main.py --mode transcripts           # Download transcripts only
  python main.py --mode analysis              # Run Fabric analysis only
  python main.py --mode visualization         # Generate visualizations only
  python main.py --mode reports               # Generate reports only
  python main.py --config custom_config.yaml # Use custom configuration
  python main.py --max-videos 50              # Limit to 50 videos for testing
  python main.py --verbose                    # Enable debug logging
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'transcripts', 'analysis', 'visualization', 'reports'],
        default='full',
        help='Analysis mode to run (default: full pipeline)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--max-videos',
        type=int,
        help='Maximum number of videos to process (overrides config)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (overrides config)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose (debug) logging'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-processing of existing files'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )
    
    return parser.parse_args()


def main():
    """Main analysis pipeline with enhanced command line support."""
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Load configuration
        config_file = Path(args.config) if args.config else None
        config = load_config(config_file)
        
        # Apply command line overrides
        if args.max_videos:
            config['processing']['max_videos'] = args.max_videos
        if args.output_dir:
            config['output']['base_dir'] = args.output_dir
        if args.force:
            config['processing']['skip_existing_transcripts'] = False
            config['processing']['skip_existing_analyses'] = False
        if args.verbose:
            config['logging']['level'] = 'DEBUG'
        
        setup_logging(config)
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No files will be modified")
            
        # Apply dry run mode
        if args.dry_run:
            config['processing']['dry_run'] = True
        
        logger = logging.getLogger(__name__)
        logger.info("=== ACTIVE INFERENCE YOUTUBE ANALYZER v2.1.0 ===")
        logger.info(f"Execution mode: {args.mode}")
        config_path = config_file or (Path(__file__).parent / "config.yaml")
        logger.info("Configuration loaded from: %s", config_path)
        
        # Setup output directories
        output_config = config.get('output', {})
        base_dir = Path(output_config.get('base_dir', 'output'))
        structure = output_config.get('structure', {})
        
        videos_dir = base_dir / structure.get('videos_dir', 'videos')
        reports_dir = base_dir / structure.get('reports_dir', 'reports')
        visualizations_dir = base_dir / structure.get('visualizations_dir', 'visualizations')
        logs_dir = base_dir / structure.get('logs_dir', 'logs')
        
        # Create all directories
        for directory in [videos_dir, reports_dir, visualizations_dir, logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Output structure:")
        logger.info(f"  Videos: {videos_dir}")
        logger.info(f"  Reports: {reports_dir}")
        logger.info(f"  Visualizations: {visualizations_dir}")
        logger.info(f"  Logs: {logs_dir}")
        
        # Step 1: Load video data from CSV
        data_config = config.get('data', {})
        csv_file = Path(__file__).parent / data_config.get('csv_file', 'video_information_active_inference_06-08-2025.csv')
        
        logger.info("Step 1: Loading video data from CSV")
        logger.info(f"Loading videos from: {csv_file}")
        
        csv_parser = VideoCSVParser(csv_file)
        videos = csv_parser.load_videos()
        
        logger.info(f"Loaded {len(videos)} videos from CSV")
        
        # Apply processing limits
        processing_config = config.get('processing', {})
        max_videos = processing_config.get('max_videos')
        if max_videos and len(videos) > max_videos:
            logger.info(f"Limiting analysis to {max_videos} videos")
            videos.videos = videos.videos[:max_videos]
        
        # Step 2: Setup hierarchical transcript downloader
        logger.info("Step 2: Setting up transcript downloader")
        
        fabric_config = config.get('fabric', {})
        downloader = HierarchicalTranscriptDownloader(
            fabric_binary_path=fabric_config.get('binary_path'),
            videos_dir=str(videos_dir),
            skip_existing=processing_config.get('skip_existing_transcripts', True),
            rate_limit_delay=processing_config.get('rate_limit_delay', 1)
        )
        
        # Step 3: Download missing transcripts
        logger.info("Step 3: Downloading transcripts")
        
        # Convert video collection to list of dicts for the new downloader
        videos_list = []
        for video in videos.videos:
            videos_list.append({
                'url': f"https://www.youtube.com/watch?v={video.video_id}",
                'title': video.title,
                'video_id': video.video_id
            })
        
        transcript_stats = downloader.download_batch_transcripts(
            videos_list, 
            batch_size=processing_config.get('transcript_batch_size', 5)
        )
        
        logger.info(f"Transcript download complete:")
        logger.info(f"  Downloaded: {transcript_stats.get('fabric_success', 0) + transcript_stats.get('api_success', 0) + transcript_stats.get('ytdlp_success', 0)}")
        logger.info(f"  Cached: {transcript_stats.get('cached', 0)}")
        logger.info(f"  Errors: {transcript_stats.get('failed', 0)}")
        
        # Step 4: Setup hierarchical Fabric analyzer
        logger.info("Step 4: Setting up Fabric analyzer")
        
        fabric_cfg = FabricConfig(
            binary_path=fabric_config.get('binary_path'),
            patterns=fabric_config.get('patterns', []),
            timeout=fabric_config.get('timeout', 300),
            retry_attempts=fabric_config.get('retry_attempts', 3)
        )
        
        analyzer = HierarchicalFabricAnalyzer(
            config=fabric_cfg,
            base_output_dir=base_dir,
            skip_existing=processing_config.get('skip_existing_analyses', True)
        )
        
        # Step 5: Analyze transcripts with Fabric
        logger.info("Step 5: Analyzing transcripts with Fabric")
        
        fabric_stats = analyzer.analyze_videos(videos)
        
        logger.info(f"Fabric analysis complete:")
        logger.info(f"  Analyses completed: {fabric_stats.completed}")
        logger.info(f"  Errors: {fabric_stats.errors}")
        
        # Step 6: Generate analytics and reports
        logger.info("Step 6: Generating analytics and reports")
        
        reporter = AnalysisReporter(reports_dir)
        analytics = reporter.generate_analytics(videos)
        
        # Step 7: Create visualizations
        logger.info("Step 7: Creating visualizations")
        
        viz_config = config.get('visualization', {})
        if viz_config.get('create_charts', True):
            created_files = create_visualizations(videos, config, visualizations_dir)
            logger.info(f"Created {len(created_files)} visualizations")
        
        # Step 8: Generate reports
        logger.info("Step 8: Generating reports")
        
        # Generate main markdown report  
        transcript_status = downloader.get_transcript_status(videos)
        report_file = reporter.generate_markdown_report(
            videos, 
            analytics,
            transcript_status,
            csv_file.name
        )
        
        # Generate JSON data export
        json_file = reporter.generate_json_report(videos, analytics)
        
        # Generate CSV summary
        csv_file = reporter.generate_csv_summary(videos)
        
        # Final summary  
        end_time = datetime.now()
        start_time = transcript_stats.start_time if transcript_stats.start_time else end_time
        total_duration = (end_time - start_time).total_seconds()
        
        logger.info("=== ANALYSIS COMPLETE ===")
        logger.info(f"Duration: {total_duration:.1f} seconds")
        logger.info(f"Videos processed: {len(videos)}")
        logger.info(f"Transcripts downloaded: {transcript_stats.get('fabric_success', 0) + transcript_stats.get('api_success', 0) + transcript_stats.get('ytdlp_success', 0)}")
        logger.info(f"Transcripts cached: {transcript_stats.get('cached', 0)}")
        logger.info(f"Fabric analyses completed: {fabric_stats.completed}")
        logger.info(f"Errors encountered: {transcript_stats.get('failed', 0) + fabric_stats.errors}")
        
        # Calculate coverage
        videos_with_transcripts = len([v for v in videos if v.transcript.strip()])
        transcript_coverage = (videos_with_transcripts / len(videos)) * 100 if len(videos) > 0 else 0
        
        logger.info(f"Transcript coverage: {transcript_coverage:.1f}%")
        logger.info(f"Output directory: {base_dir}")
        logger.info(f"Main report: {report_file}")
        logger.info("Data files:")
        logger.info(f"  JSON: {json_file}")
        logger.info(f"  CSV: {csv_file}")
        
        # List video directories created
        video_dirs = list(videos_dir.glob("*"))
        logger.info(f"Video directories created: {len(video_dirs)}")
        for video_dir in sorted(video_dirs):
            files = list(video_dir.glob("*"))
            logger.info(f"  {video_dir.name}: {len(files)} files")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 