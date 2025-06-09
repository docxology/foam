#!/usr/bin/env python3
"""
Test script for debugging visualization issues.
Creates markers for failed visualizations so they can be skipped in future runs.
"""

import sys
import traceback
from pathlib import Path
from config import load_config
from csv_parser import VideoCSVParser
from visualizer import create_visualizations

def test_visualizations():
    """Test visualization creation with proper error handling."""
    
    print("=== VISUALIZATION TEST ===")
    
    try:
        print("Loading config...")
        config = load_config()
        
        print("Loading videos...")
        csv_file = Path('video_information_active_inference_06-08-2025.csv')
        parser = VideoCSVParser(csv_file)
        videos = parser.load_videos()
        print(f"Loaded {len(videos)} videos")
        
        # Limit to first 10 videos for testing
        if len(videos) > 10:
            print("Limiting to first 10 videos for testing...")
            videos.videos = videos.videos[:10]
        
        print("Creating output directory...")
        output_dir = Path('output/visualizations')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create marker directory for failed visualizations
        marker_dir = output_dir / '.failed_markers'
        marker_dir.mkdir(exist_ok=True)
        
        print("Testing individual chart types...")
        viz_config = config.get('visualization', {})
        chart_types = viz_config.get('chart_types', [])
        
        successful_charts = []
        failed_charts = []
        
        for chart_type in chart_types:
            marker_file = marker_dir / f"{chart_type}.failed"
            
            # Skip if already marked as failed
            if marker_file.exists():
                print(f"⏭️  Skipping {chart_type} (previously failed)")
                continue
            
            print(f"🔄 Testing {chart_type}...")
            
            try:
                # Test with single chart type
                test_config = config.copy()
                test_config['visualization']['chart_types'] = [chart_type]
                
                created_files = create_visualizations(videos, test_config, output_dir)
                
                if created_files:
                    print(f"✅ {chart_type}: Created {len(created_files)} files")
                    successful_charts.append(chart_type)
                    for f in created_files:
                        print(f"   📄 {f.name}")
                else:
                    print(f"⚠️  {chart_type}: No files created")
                    
            except Exception as e:
                print(f"❌ {chart_type}: Failed with error: {e}")
                failed_charts.append((chart_type, str(e)))
                
                # Create failure marker
                with open(marker_file, 'w') as f:
                    f.write(f"Failed at: {traceback.format_exc()}\n")
                    f.write(f"Error: {str(e)}\n")
                
                # Print traceback for debugging
                print(f"   Traceback:")
                traceback.print_exc()
        
        print("\n=== SUMMARY ===")
        print(f"✅ Successful: {len(successful_charts)}")
        for chart in successful_charts:
            print(f"   - {chart}")
            
        print(f"❌ Failed: {len(failed_charts)}")
        for chart, error in failed_charts:
            print(f"   - {chart}: {error}")
            
        if failed_charts:
            print(f"\n📝 Failed charts marked in: {marker_dir}")
            print("   These will be skipped in future runs")
            
        return len(successful_charts), len(failed_charts)
        
    except Exception as e:
        print(f"💥 Critical error: {e}")
        traceback.print_exc()
        return 0, 1

if __name__ == "__main__":
    successful, failed = test_visualizations()
    print(f"\nResult: {successful} successful, {failed} failed")
    sys.exit(0 if failed == 0 else 1) 