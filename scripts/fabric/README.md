# Fabric and Foam Setup Script

This script automates the setup process for integrating Fabric with your Foam project.

## What it does

1. **Clones the Fabric repository** from `https://github.com/danielmiessler/fabric`
2. **Sets up a Python virtual environment** for managing dependencies
3. **Installs Fabric** (Go-based AI augmentation framework)
4. **Installs Foam dependencies** (common Python packages)
5. **Verifies the installation** and generates a comprehensive status report

## Prerequisites

- **Python 3.6+** (for virtual environment and logging)
- **Go 1.24+** (required for Fabric installation)
- **Git** (for cloning repositories)

## Usage

```bash
# Run the setup script
python3 scripts/fabric/fabric_foam_setup.py

# Or make it executable and run directly
chmod +x scripts/fabric/fabric_foam_setup.py
./scripts/fabric/fabric_foam_setup.py
```

## What gets created

- `venv_fabric_foam/` - Python virtual environment
- `fabric/` - Cloned Fabric repository
- `logs/` - Detailed execution logs
- `fabric_foam_setup_status.json` - Installation status report

## After installation

1. **Activate the virtual environment:**

   ```bash
   source venv_fabric_foam/bin/activate
   ```

2. **Use Fabric:**

   ```bash
   ~/go/bin/fabric --help
   # Or add to PATH for global access
   ```

3. **Configure Fabric:**
   ```bash
   ~/go/bin/fabric --setup
   ```

## Features

- **Comprehensive logging** with both file and console output
- **Error handling** with fallback installation methods
- **Status verification** to confirm successful installation
- **Professional code structure** following Python best practices
- **Cross-platform compatibility** (Linux, macOS, Windows)

## Troubleshooting

Check the log files in the `logs/` directory for detailed information about any issues encountered during setup.

## Architecture

The script is designed as a modular class-based system:

- `FabricFoamSetup` - Main setup orchestrator
- Separate methods for each setup phase
- Comprehensive error handling and logging
- Status reporting and verification

This ensures maintainability, extensibility, and professional-grade reliability.

## Active Inference Channel Analyzer

The `fabric_active_inference.py` script provides comprehensive analysis of the Active Inference YouTube channel (http://youtube.com/@activeinference).

### Features

- **Channel Analysis**: Fetches all public videos with metadata
- **Transcript Processing**: Downloads video transcripts using Fabric
- **AI Content Analysis**: Applies Fabric patterns for insight extraction
- **Data Visualization**: Creates comprehensive charts and graphs
- **Statistical Reporting**: Generates detailed analytics reports
- **Professional Output**: Saves data in JSON, CSV, and Markdown formats

### Usage

```bash
# Basic analysis (50 videos, no transcripts)
python3 scripts/fabric/fabric_active_inference.py --max-videos 50 --no-transcripts

# Full analysis with AI patterns
python3 scripts/fabric/fabric_active_inference.py --max-videos 20 --patterns summarize extract_wisdom extract_ideas

# Generate only visualizations from existing data
python3 scripts/fabric/fabric_active_inference.py --visualizations-only

# Custom output directory
python3 scripts/fabric/fabric_active_inference.py --output-dir ./my_analysis
```

### Prerequisites

Install additional dependencies:

```bash
pip install -r scripts/fabric/requirements_active_inference.txt
```

Optional: Set YouTube API key for enhanced metadata:

```bash
export YOUTUBE_API_KEY="your_api_key_here"
```

### Output Structure

```
active_inference_analysis/
├── data/                          # Raw data files
│   ├── active_inference_videos_*.json
│   └── active_inference_summary_*.csv
├── visualizations/                # Generated charts
│   ├── views_vs_likes.png
│   ├── publication_timeline.png
│   ├── duration_distribution.png
│   └── top_videos.png
└── reports/                       # Analysis reports
    └── active_inference_analysis_report_*.md
```

### Analysis Capabilities

1. **Video Discovery**: Automatically finds all channel videos
2. **Metadata Collection**: Views, likes, comments, duration, publication date
3. **Transcript Analysis**: Full text extraction and length analysis
4. **AI Pattern Application**:
   - Content summarization
   - Wisdom extraction
   - Insight generation
   - Question extraction
5. **Statistical Analysis**: Performance metrics and trends
6. **Visualization**: Multiple chart types for data exploration
