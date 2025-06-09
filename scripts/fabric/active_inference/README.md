# Active Inference YouTube Channel Analyzer v2.1.0

A comprehensive, state-of-the-art toolkit for analyzing the Active Inference YouTube channel using advanced AI, machine learning, and data visualization techniques.

## 🌟 Enhanced Features

### Core Functionality

- **CSV-Driven Analysis**: Uses curated CSV data as the gold standard for video information
- **Intelligent Transcript Management**: Multi-method transcript extraction with smart caching
- **Advanced Fabric AI Integration**: 20+ AI patterns for comprehensive content analysis
- **Hierarchical Output Structure**: Organized file system with individual video folders

### 🔬 Advanced Analytics & Visualizations

#### Statistical Analysis

- **Principal Component Analysis (PCA)**: Dimensionality reduction and feature importance
- **Clustering Analysis**: K-means, DBSCAN, and hierarchical clustering
- **Correlation Analysis**: Feature correlation matrices and heatmaps
- **Statistical Distributions**: Normality testing, outlier detection, Q-Q plots
- **Time Series Analysis**: Temporal patterns, seasonality, and forecasting
- **Multi-Dimensional Scaling (MDS)**: Alternative dimensionality reduction

#### Natural Language Processing

- **Sentiment Analysis**: Polarity and subjectivity analysis of titles/descriptions
- **Topic Modeling**: Latent Dirichlet Allocation (LDA) for content themes
- **Word Cloud Generation**: Visual representation of content frequency
- **Content Ontology**: Domain-specific concept mapping for Active Inference
- **Semantic Similarity**: Content relationship networks and similarity matrices
- **Text Evolution Analysis**: How content themes change over time

#### Network & Relationship Analysis

- **Video Relationship Networks**: Series connections and guest relationships
- **Centrality Analysis**: Identifying key videos and content hubs
- **Community Detection**: Finding content clusters and sub-communities
- **Content Evolution Tracking**: How video content develops over time

#### Predictive & Advanced Analytics

- **Engagement Prediction**: ML models for predicting video performance
- **Anomaly Detection**: Identifying unusual patterns in video metrics
- **Trend Analysis**: Content and engagement trend forecasting
- **Feature Importance**: Understanding which factors drive engagement
- **Comparative Analysis**: Cross-series and temporal comparisons

#### Interactive Visualizations

- **Interactive Dashboards**: Plotly-based dynamic visualizations
- **Multi-dimensional Exploration**: Interactive scatter plots and filters
- **Time-based Navigation**: Temporal sliders and animation
- **Drill-down Capabilities**: Hierarchical data exploration

## 📋 Prerequisites

- Python 3.8+
- [Fabric](https://github.com/danielmiessler/fabric) installed and configured
- Active Inference video information CSV file
- 8GB+ RAM recommended for large datasets

## 🚀 Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv_active_inference
source venv_active_inference/bin/activate  # Linux/Mac
# venv_active_inference\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements_active_inference.txt

# Download required NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

# Optional: Install spaCy language model
python -m spacy download en_core_web_sm
```

### 2. Configuration

Edit `config.yaml` to customize your analysis:

```yaml
# Data source
data:
  csv_file: 'video_information_active_inference_06-08-2025.csv'

# Processing settings
processing:
  max_videos: null # Process all videos
  skip_existing_transcripts: true
  skip_existing_analyses: true

# Fabric AI patterns
fabric:
  patterns:
    - 'summarize'
    - 'extract_wisdom'
    - 'extract_insights'
    - 'analyze_prose'
    - 'topic_modeling'

# Visualization types
visualization:
  chart_types:
    # Standard analytics
    - 'views_vs_likes_scatter'
    - 'publication_timeline'
    - 'series_distribution'

    # Advanced analytics
    - 'pca_analysis'
    - 'clustering_analysis'
    - 'sentiment_analysis'
    - 'topic_modeling'
    - 'network_analysis'
    - 'interactive_dashboard'
```

### 3. Run Analysis

```bash
# Complete analysis pipeline
python main.py

# Or run specific components
python main.py --mode transcripts    # Download missing transcripts only
python main.py --mode analysis       # Run Fabric analysis only
python main.py --mode visualization  # Generate visualizations only
```

## 🏗️ Enhanced Architecture

```
scripts/fabric/active_inference/
├── __init__.py              # Package initialization
├── main.py                  # Main orchestration with new modes
├── config.py               # Enhanced configuration management
├── config.yaml             # Comprehensive configuration
├── models.py               # Extended data models
├── utils.py                # Enhanced utility functions
├── csv_parser.py           # Robust CSV data loading
├── downloader.py           # Multi-method transcript extraction
├── fabric_analyzer.py      # Advanced Fabric AI integration
├── visualizer.py           # Comprehensive visualization suite
├── reporter.py             # Enhanced report generation
├── analytics_engine.py     # NEW: Advanced analytics engine
├── nlp_processor.py        # NEW: Natural language processing
├── network_analyzer.py     # NEW: Network analysis tools
├── requirements_active_inference.txt  # Complete dependencies
└── README.md               # This comprehensive documentation
```

## 📊 Comprehensive Output Structure

The analyzer creates a sophisticated hierarchical output structure:

```
output/
├── videos/                 # Individual video analysis
│   ├── VIDEO_ID/
│   │   ├── transcript.txt
│   │   ├── metadata.json
│   │   ├── summarize.md
│   │   ├── extract_wisdom.md
│   │   ├── sentiment_analysis.json
│   │   └── ...
│   └── ...
├── reports/               # Comprehensive analysis reports
│   ├── active_inference_analysis_report_TIMESTAMP.md
│   ├── active_inference_videos_TIMESTAMP.json
│   ├── active_inference_summary_TIMESTAMP.csv
│   ├── statistical_analysis_TIMESTAMP.pdf
│   └── content_ontology_TIMESTAMP.json
├── visualizations/        # All generated visualizations
│   ├── standard/          # Basic charts
│   ├── statistical/       # PCA, clustering, correlations
│   ├── nlp/              # Sentiment, topics, word clouds
│   ├── network/          # Relationship networks
│   ├── temporal/         # Time series analysis
│   ├── interactive/      # HTML dashboards
│   └── comparative/      # Cross-analysis comparisons
└── logs/                 # Detailed execution logs
    ├── main_analysis_TIMESTAMP.log
    ├── fabric_analysis_TIMESTAMP.log
    └── visualization_TIMESTAMP.log
```

## 🎯 Advanced Use Cases

### Academic Research

- **Longitudinal Content Analysis**: Track evolution of Active Inference concepts
- **Citation Network Analysis**: Identify key papers and researchers
- **Pedagogical Pattern Recognition**: Understand teaching and learning patterns
- **Cross-disciplinary Mapping**: Connect Active Inference to other fields

### Content Strategy & Optimization

- **Engagement Prediction Models**: Forecast video performance
- **Optimal Content Length Analysis**: Data-driven duration recommendations
- **Series Performance Analytics**: Identify successful content formats
- **Audience Engagement Patterns**: Understand viewer behavior

### Educational Applications

- **Concept Difficulty Assessment**: Identify complex vs. accessible content
- **Learning Path Optimization**: Sequence content for optimal understanding
- **Knowledge Gap Analysis**: Find missing or under-explained concepts
- **Prerequisite Mapping**: Build dependency graphs for concepts

### Research Collaboration

- **Guest Impact Analysis**: Measure contribution of different speakers
- **Interdisciplinary Connections**: Map connections to other research areas
- **Publication Alignment**: Connect videos to academic publications
- **Community Growth Tracking**: Monitor field development over time

## ⚙️ Comprehensive Configuration Options

### Data Sources & Processing

```yaml
data:
  csv_file: 'path/to/video_data.csv'
  youtube_api_key: 'YOUR_API_KEY' # Optional for enhanced metadata
  additional_sources: # Future: multiple data sources
    - 'academic_papers.csv'
    - 'researcher_profiles.json'

processing:
  max_videos: null # null = process all
  parallel_workers: 4 # Parallel processing
  memory_limit: '8GB' # Memory management
  cache_strategy: 'aggressive' # Caching behavior
  error_handling: 'continue' # How to handle errors
```

### Advanced Fabric Analysis

```yaml
fabric:
  binary_path: '/path/to/fabric'
  analysis_modes:
    - 'comprehensive' # All patterns
    - 'academic' # Academic-focused patterns
    - 'creative' # Creative analysis patterns

  custom_patterns:
    - name: 'active_inference_concepts'
      description: 'Extract AI-specific concepts'
      template: 'custom_templates/ai_concepts.md'

  batch_processing:
    enabled: true
    batch_size: 10
    parallel_analysis: true
```

### Comprehensive Visualization

```yaml
visualization:
  # Output settings
  dpi: 300 # Publication quality
  formats: ['png', 'pdf', 'svg'] # Multiple formats

  # Style customization
  theme: 'academic' # Professional styling
  color_schemes:
    primary: 'Set3'
    categorical: 'tab10'
    sequential: 'viridis'

  # Advanced analytics
  statistical_tests:
    - 'normality'
    - 'correlation_significance'
    - 'trend_significance'

  machine_learning:
    clustering_algorithms: ['kmeans', 'dbscan', 'hierarchical']
    dimensionality_reduction: ['pca', 'tsne', 'umap']

  interactive:
    enable_plotly: true
    dashboard_features: ['filtering', 'drilling', 'exporting']
```

## 🔧 Advanced Usage Examples

### Programmatic Analysis

```python
from scripts.fabric.active_inference import (
    get_config, load_videos_from_csv,
    AdvancedDataVisualizer, AnalyticsEngine,
    NLPProcessor, NetworkAnalyzer
)

# Load configuration and data
config = get_config("custom_config.yaml")
videos = load_videos_from_csv(config.csv_file_path)

# Advanced analytics engine
analytics = AnalyticsEngine(config)
results = analytics.run_comprehensive_analysis(videos)

# Natural language processing
nlp = NLPProcessor(config)
concepts = nlp.extract_domain_concepts(videos)
sentiment_trends = nlp.analyze_sentiment_evolution(videos)

# Network analysis
network = NetworkAnalyzer(config)
collaboration_graph = network.build_collaboration_network(videos)
influence_metrics = network.calculate_influence_metrics(videos)

# Advanced visualizations
visualizer = AdvancedDataVisualizer(config, output_dir)
dashboards = visualizer.create_interactive_dashboards(videos, results)
```

### Custom Analysis Pipeline

```python
# Custom analysis for specific research questions
def analyze_concept_evolution(videos, concept='free energy'):
    """Track how a specific concept evolves over time."""

    # Extract concept mentions
    concept_timeline = nlp.track_concept_over_time(videos, concept)

    # Analyze co-occurring concepts
    co_concepts = nlp.find_related_concepts(videos, concept)

    # Create specialized visualizations
    viz_files = [
        visualizer.create_concept_timeline(concept_timeline),
        visualizer.create_concept_network(co_concepts),
        visualizer.create_concept_evolution_heatmap(videos, concept)
    ]

    return {
        'timeline': concept_timeline,
        'related_concepts': co_concepts,
        'visualizations': viz_files
    }

# Engagement prediction model
def build_engagement_model(videos):
    """Build ML model to predict video engagement."""

    features = analytics.extract_features(videos)
    model = analytics.train_engagement_model(features)
    predictions = model.predict(features)

    return {
        'model': model,
        'predictions': predictions,
        'feature_importance': model.feature_importance_,
        'accuracy_metrics': analytics.evaluate_model(model, features)
    }
```

### Batch Processing for Large Datasets

```python
from scripts.fabric.active_inference.batch_processor import BatchProcessor

# Process large datasets efficiently
processor = BatchProcessor(config)
processor.set_batch_size(50)
processor.enable_parallel_processing(workers=8)

# Process in chunks with progress tracking
for batch_result in processor.process_videos_in_batches(videos):
    logger.info(f"Processed batch: {batch_result.summary}")

    # Save intermediate results
    processor.save_batch_results(batch_result)
```

## 📈 Performance Optimization

### For Large Datasets (1000+ videos)

```yaml
# config.yaml optimizations
processing:
  batch_size: 20
  parallel_workers: 8
  memory_management: 'streaming'
  checkpoint_frequency: 100

visualization:
  sampling_strategy: 'stratified'
  max_points_per_plot: 1000
  generate_thumbnails: true
```

### Memory-Efficient Processing

```python
# Stream processing for memory efficiency
def process_large_dataset(csv_file):
    processor = StreamingProcessor(config)

    for video_batch in processor.stream_from_csv(csv_file, chunk_size=100):
        # Process each batch
        results = processor.analyze_batch(video_batch)

        # Save results incrementally
        processor.save_batch_results(results)

        # Clear memory
        processor.cleanup_batch()
```

## 🐛 Troubleshooting & FAQ

### Common Issues

**Q: Visualization generation is slow**
A: Enable sampling for large datasets:

```yaml
visualization:
  sampling_strategy: 'random'
  max_samples: 1000
```

**Q: Out of memory errors**
A: Reduce batch size and enable streaming:

```yaml
processing:
  batch_size: 10
  streaming_mode: true
  memory_limit: '4GB'
```

**Q: Fabric patterns failing**
A: Check pattern availability:

```bash
fabric --listpatterns | grep extract_wisdom
```

**Q: Interactive dashboards not working**
A: Install plotly and dash:

```bash
pip install plotly dash
```

### Performance Monitoring

```python
# Enable detailed performance monitoring
config.monitoring.enabled = True
config.monitoring.profile_memory = True
config.monitoring.profile_cpu = True

# View performance reports
analyzer.generate_performance_report()
```

## 🔬 Research Applications

### Published Research Integration

- Connect video content to published papers
- Track concept development from papers to videos
- Identify research gaps and opportunities
- Map researcher collaboration networks

### Meta-Analysis Capabilities

- Compare Active Inference with other frameworks
- Track field evolution and paradigm shifts
- Identify emerging research directions
- Quantify concept adoption rates

### Educational Impact Assessment

- Measure learning effectiveness
- Identify optimal teaching sequences
- Track concept difficulty progression
- Assess pedagogical innovation

## 🤝 Advanced Contributing

### Adding New Visualizations

```python
# Custom visualization example
class CustomVisualizer(AdvancedDataVisualizer):
    def _create_custom_analysis(self, videos):
        """Your custom visualization logic"""
        # Implementation here
        return self._save_figure('custom_analysis')

# Register new visualization type
config.visualization.chart_types.append('custom_analysis')
```

### Extending Analytics Engine

```python
# Custom analytics module
class DomainSpecificAnalytics(AnalyticsEngine):
    def analyze_active_inference_concepts(self, videos):
        """Domain-specific analysis methods"""
        # Your analysis logic
        pass
```

### Contributing Guidelines

1. **New Features**: Add comprehensive tests and documentation
2. **Visualizations**: Include example outputs and configuration
3. **Analytics**: Provide mathematical foundation and validation
4. **Performance**: Include benchmarks and optimization notes

## 📚 Educational Resources

### Learning Active Inference Through Data

- Use the analyzer to explore concept relationships
- Track your own learning journey through the content
- Identify prerequisite knowledge gaps
- Create personalized learning paths

### Teaching Applications

- Generate quizzes from video content
- Create concept maps for students
- Track class engagement with different topics
- Identify difficult concepts for additional explanation

## 🔮 Future Developments

### Planned Features (v2.2.0)

- **Real-time Analysis**: Live video processing
- **Multi-channel Comparison**: Compare with related channels
- **Advanced NLP Models**: Transformer-based analysis
- **Interactive 3D Visualizations**: WebGL-based exploration
- **Automated Report Generation**: LaTeX/PDF reports

### Research Integrations

- **ArXiv Integration**: Connect to academic papers
- **Google Scholar**: Track citation networks
- **ORCID Integration**: Researcher identification
- **Zotero/Mendeley**: Bibliography management

## 📄 License & Citation

This project is part of the Foam knowledge management ecosystem. When using this analyzer for research, please cite:

```bibtex
@software{active_inference_analyzer,
  title={Active Inference YouTube Channel Analyzer},
  author={Foam Community},
  version={2.1.0},
  year={2025},
  url={https://github.com/foambubble/foam}
}
```

## 🙏 Acknowledgments

- [Active Inference Institute](https://www.activeinference.org/) for educational content
- [Fabric](https://github.com/danielmiessler/fabric) for AI-powered analysis
- The Foam community for knowledge management framework
- Open source contributors to visualization and ML libraries

---

**For advanced usage, custom analysis, or research collaboration, please refer to the detailed API documentation and contribute to the project's continued development.**
