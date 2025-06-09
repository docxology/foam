"""
Advanced data visualization and analysis module for the Active Inference YouTube Channel Analyzer.

This module provides comprehensive visualization capabilities including:
- Statistical visualizations (PCA, clustering, correlation matrices)
- Natural language analysis (sentiment, topic modeling, word clouds)
- Network analysis and ontology mapping
- Time series analysis and forecasting
- Interactive visualizations and dashboards
"""

import json
import logging
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
from wordcloud import WordCloud
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import networkx as nx
from textblob import TextBlob
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

from models import VideoData, VideoDataCollection, VisualizationConfig
from utils import create_timestamp, ensure_directory, parse_youtube_duration

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class VisualizationError(Exception):
    """Raised when there's an error creating visualizations."""
    pass


class AdvancedDataVisualizer:
    """Advanced data visualizer with statistical analysis and natural language processing."""
    
    def __init__(self, config: VisualizationConfig, output_dir: Path):
        """
        Initialize advanced visualizer.
        
        Args:
            config: Visualization configuration
            output_dir: Output directory for saving visualizations
        """
        self.config = config
        self.output_dir = ensure_directory(output_dir)
        self.timestamp = create_timestamp()
        
        # Set visualization style
        plt.style.use(config.style)
        sns.set_palette(config.color_palette)
        
        logger.info("Advanced data visualizer initialized")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Chart types: {', '.join(config.chart_types)}")
    
    def create_all_visualizations(self, videos: VideoDataCollection) -> List[Path]:
        """
        Create all configured visualizations with enhanced analytics.
        
        Args:
            videos: Video collection to visualize
            
        Returns:
            List of paths to created visualization files
        """
        if not videos:
            logger.warning("No video data available for visualization")
            return []
        
        logger.info(f"Creating visualizations for {len(videos)} videos")
        created_files = []
        
        # Standard visualizations
        standard_methods = {
            'views_vs_likes_scatter': self._create_views_likes_scatter,
            'publication_timeline': self._create_publication_timeline,
            'duration_distribution': self._create_duration_distribution,
            'transcript_analysis': self._create_transcript_analysis,
            'top_videos_chart': self._create_top_videos_chart,
            'series_distribution': self._create_series_distribution,
            'engagement_metrics': self._create_engagement_metrics,
            'monthly_activity': self._create_monthly_activity,
            'content_length_correlation': self._create_content_length_correlation,
        }
        
        # Advanced analytics visualizations
        advanced_methods = {
            'pca_analysis': self._create_pca_analysis,
            'correlation_heatmap': self._create_correlation_heatmap,
            'clustering_analysis': self._create_clustering_analysis,
            'sentiment_analysis': self._create_sentiment_analysis,
            'topic_modeling': self._create_topic_modeling,
            'word_cloud': self._create_word_cloud,
            'network_analysis': self._create_network_analysis,
            'statistical_distributions': self._create_statistical_distributions,
            'time_series_analysis': self._create_time_series_analysis,
            'content_ontology': self._create_content_ontology,
            'interactive_dashboard': self._create_interactive_dashboard,
            'hierarchical_clustering': self._create_hierarchical_clustering,
            'tsne_visualization': self._create_tsne_visualization,
            'feature_importance': self._create_feature_importance,
            'anomaly_detection': self._create_anomaly_detection,
            'trend_analysis': self._create_trend_analysis,
            'semantic_similarity': self._create_semantic_similarity,
            'content_evolution': self._create_content_evolution,
            'engagement_prediction': self._create_engagement_prediction,
            'multi_dimensional_scaling': self._create_mds_analysis,
            'comparative_analysis': self._create_comparative_analysis
        }
        
        # Combine all methods
        all_methods = {**standard_methods, **advanced_methods}
        
        for chart_type in self.config.chart_types:
            if chart_type in all_methods:
                try:
                    logger.info(f"Creating {chart_type} visualization")
                    viz_file = all_methods[chart_type](videos)
                    if viz_file:
                        created_files.append(viz_file)
                        logger.info(f"Created visualization: {viz_file.name}")
                except Exception as e:
                    logger.error(f"Error creating {chart_type}: {e}")
            else:
                logger.warning(f"Unknown chart type: {chart_type}")
        
        logger.info(f"Created {len(created_files)} visualizations")
        return created_files

    # Original visualization methods (enhanced)
    def _create_views_likes_scatter(self, videos: VideoDataCollection) -> Optional[Path]:
        """Enhanced scatter plot of views vs likes with additional analytics."""
        videos_with_data = [v for v in videos if v.view_count > 0 and v.like_count > 0]
        
        if not videos_with_data:
            logger.warning("No view/like data available for scatter plot")
            return None
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Engagement Analysis: Views vs Likes', fontsize=16, fontweight='bold')
        
        # Main scatter plot with series coloring
        series_colors = {}
        unique_series = list(set(v.series for v in videos_with_data if v.series))
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_series)))
        for i, series in enumerate(unique_series):
            series_colors[series] = colors[i]
        
        for video in videos_with_data:
            color = series_colors.get(video.series, 'gray')
            ax1.scatter(video.view_count, video.like_count, 
                       c=[color], s=50, alpha=0.7, edgecolors='black')
        
        ax1.set_xlabel('Views')
        ax1.set_ylabel('Likes')
        ax1.set_title('Views vs Likes by Series')
        ax1.grid(True, alpha=0.3)
        
        # Add trend line
        views = [v.view_count for v in videos_with_data]
        likes = [v.like_count for v in videos_with_data]
        z = np.polyfit(views, likes, 1)
        p = np.poly1d(z)
        ax1.plot(views, p(views), "r--", alpha=0.8, linewidth=2)
        
        # Engagement rate distribution
        engagement_rates = [v.like_count / max(v.view_count, 1) * 100 for v in videos_with_data]
        ax2.hist(engagement_rates, bins=20, alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Engagement Rate (%)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Engagement Rate Distribution')
        ax2.grid(True, alpha=0.3)
        
        # Views distribution (log scale)
        ax3.hist([np.log10(v.view_count) for v in videos_with_data], 
                bins=20, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Log10(Views)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Views Distribution (Log Scale)')
        ax3.grid(True, alpha=0.3)
        
        # Top performers
        top_videos = sorted(videos_with_data, key=lambda v: v.view_count, reverse=True)[:10]
        ax4.barh(range(len(top_videos)), [v.view_count for v in top_videos])
        ax4.set_yticks(range(len(top_videos)))
        ax4.set_yticklabels([v.title[:30] + '...' if len(v.title) > 30 else v.title 
                           for v in top_videos], fontsize=8)
        ax4.set_xlabel('Views')
        ax4.set_title('Top 10 Videos by Views')
        
        plt.tight_layout()
        return self._save_figure('enhanced_views_likes_analysis')

    def _create_pca_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Principal Component Analysis of video features."""
        try:
            # Extract numerical features
            features = []
            labels = []
            
            for video in videos:
                if video.view_count > 0:  # Only include videos with data
                    duration_minutes = parse_youtube_duration(video.duration) if video.duration else 0
                    engagement_rate = video.like_count / max(video.view_count, 1)
                    
                    features.append([
                        np.log10(max(video.view_count, 1)),
                        np.log10(max(video.like_count, 1)),
                        np.log10(max(video.comment_count, 1)),
                        duration_minutes,
                        video.transcript_length,
                        engagement_rate,
                        len(video.title),
                        len(video.description)
                    ])
                    labels.append(video.series or 'Unknown')
            
            if len(features) < 3:
                logger.warning("Insufficient data for PCA analysis")
                return None
            
            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Apply PCA
            pca = PCA()
            pca_result = pca.fit_transform(features_scaled)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Principal Component Analysis', fontsize=16, fontweight='bold')
            
            # PCA scatter plot (first two components)
            unique_labels = list(set(labels))
            colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))
            for i, label in enumerate(unique_labels):
                mask = [l == label for l in labels]
                ax1.scatter(pca_result[mask, 0], pca_result[mask, 1], 
                           c=[colors[i]], label=label, alpha=0.7)
            
            ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
            ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
            ax1.set_title('PCA: First Two Components')
            ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            # Explained variance
            ax2.bar(range(1, len(pca.explained_variance_ratio_) + 1), 
                   pca.explained_variance_ratio_)
            ax2.set_xlabel('Principal Component')
            ax2.set_ylabel('Explained Variance Ratio')
            ax2.set_title('Explained Variance by Component')
            ax2.grid(True, alpha=0.3)
            
            # Cumulative explained variance
            cumsum = np.cumsum(pca.explained_variance_ratio_)
            ax3.plot(range(1, len(cumsum) + 1), cumsum, 'bo-')
            ax3.axhline(y=0.95, color='r', linestyle='--', label='95% variance')
            ax3.set_xlabel('Number of Components')
            ax3.set_ylabel('Cumulative Explained Variance')
            ax3.set_title('Cumulative Explained Variance')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Feature loadings heatmap
            feature_names = ['Log Views', 'Log Likes', 'Log Comments', 'Duration', 
                           'Transcript Length', 'Engagement Rate', 'Title Length', 'Desc Length']
            loadings = pca.components_[:4, :].T  # First 4 components
            
            im = ax4.imshow(loadings, cmap='RdBu', aspect='auto')
            ax4.set_xticks(range(4))
            ax4.set_xticklabels([f'PC{i+1}' for i in range(4)])
            ax4.set_yticks(range(len(feature_names)))
            ax4.set_yticklabels(feature_names)
            ax4.set_title('Feature Loadings')
            plt.colorbar(im, ax=ax4)
            
            plt.tight_layout()
            return self._save_figure('pca_analysis')
            
        except Exception as e:
            logger.error(f"Error in PCA analysis: {e}")
            return None

    def _create_correlation_heatmap(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create correlation heatmap of video metrics."""
        try:
            # Prepare data
            data = []
            for video in videos:
                if video.view_count > 0:
                    duration_minutes = parse_youtube_duration(video.duration) if video.duration else 0
                    data.append({
                        'Views': video.view_count,
                        'Likes': video.like_count,
                        'Comments': video.comment_count,
                        'Duration (min)': duration_minutes,
                        'Transcript Length': video.transcript_length,
                        'Title Length': len(video.title),
                        'Description Length': len(video.description),
                        'Engagement Rate': video.like_count / max(video.view_count, 1)
                    })
            
            if not data:
                logger.warning("No data for correlation analysis")
                return None
            
            df = pd.DataFrame(data)
            
            # Create correlation matrix
            correlation_matrix = df.corr()
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Correlation Analysis', fontsize=16, fontweight='bold')
            
            # Main correlation heatmap
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', 
                       center=0, square=True, ax=ax1)
            ax1.set_title('Correlation Matrix (Upper Triangle)')
            
            # Correlation with views specifically
            views_corr = correlation_matrix['Views'].sort_values(ascending=False)
            ax2.barh(range(len(views_corr)-1), views_corr[1:])  # Exclude self-correlation
            ax2.set_yticks(range(len(views_corr)-1))
            ax2.set_yticklabels(views_corr.index[1:])
            ax2.set_xlabel('Correlation with Views')
            ax2.set_title('Feature Correlation with Views')
            ax2.grid(True, alpha=0.3)
            
            # Distribution of correlations
            corr_values = correlation_matrix.values
            corr_flat = corr_values[np.triu_indices_from(corr_values, k=1)]
            ax3.hist(corr_flat, bins=20, alpha=0.7, edgecolor='black')
            ax3.set_xlabel('Correlation Coefficient')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Distribution of Correlations')
            ax3.grid(True, alpha=0.3)
            
            # Scatter plot of highest correlation pair
            if len(views_corr) > 1:
                highest_corr_feature = views_corr.index[1]
                ax4.scatter(df['Views'], df[highest_corr_feature], alpha=0.6)
                ax4.set_xlabel('Views')
                ax4.set_ylabel(highest_corr_feature)
                ax4.set_title(f'Views vs {highest_corr_feature} (r={views_corr[1]:.3f})')
                ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('correlation_heatmap')
            
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {e}")
            return None

    def _create_clustering_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Perform clustering analysis on video data."""
        try:
            # Prepare features for clustering
            features = []
            video_info = []
            
            for video in videos:
                if video.view_count > 0:
                    duration_minutes = parse_youtube_duration(video.duration) if video.duration else 0
                    features.append([
                        np.log10(max(video.view_count, 1)),
                        np.log10(max(video.like_count, 1)),
                        duration_minutes,
                        video.transcript_length
                    ])
                    video_info.append({'title': video.title, 'series': video.series})
            
            if len(features) < 5:
                logger.warning("Insufficient data for clustering analysis")
                return None
            
            features_array = np.array(features)
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_array)
            
            # K-means clustering
            optimal_k = min(5, len(features) // 2)
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features_scaled)
            
            # DBSCAN clustering
            dbscan = DBSCAN(eps=0.5, min_samples=3)
            dbscan_labels = dbscan.fit_predict(features_scaled)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Clustering Analysis', fontsize=16, fontweight='bold')
            
            # K-means results
            scatter = ax1.scatter(features_array[:, 0], features_array[:, 1], 
                                c=cluster_labels, cmap='viridis', alpha=0.7)
            ax1.set_xlabel('Log10(Views)')
            ax1.set_ylabel('Log10(Likes)')
            ax1.set_title(f'K-Means Clustering (k={optimal_k})')
            plt.colorbar(scatter, ax=ax1)
            
            # DBSCAN results
            scatter2 = ax2.scatter(features_array[:, 0], features_array[:, 1], 
                                 c=dbscan_labels, cmap='viridis', alpha=0.7)
            ax2.set_xlabel('Log10(Views)')
            ax2.set_ylabel('Log10(Likes)')
            ax2.set_title('DBSCAN Clustering')
            plt.colorbar(scatter2, ax=ax2)
            
            # Cluster characteristics for K-means
            cluster_stats = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                cluster_stats[label].append(features_array[i])
            
            cluster_means = []
            cluster_names = []
            for cluster_id, points in cluster_stats.items():
                if points:
                    mean_point = np.mean(points, axis=0)
                    cluster_means.append(mean_point)
                    cluster_names.append(f'Cluster {cluster_id}')
            
            cluster_means = np.array(cluster_means)
            
            # Radar chart of cluster characteristics
            if len(cluster_means) > 0:
                feature_names = ['Log Views', 'Log Likes', 'Duration', 'Transcript Length']
                angles = np.linspace(0, 2 * np.pi, len(feature_names), endpoint=False)
                angles = np.concatenate((angles, [angles[0]]))
                
                ax3 = plt.subplot(2, 2, 3, projection='polar')
                
                for i, (cluster_mean, cluster_name) in enumerate(zip(cluster_means, cluster_names)):
                    values = np.concatenate((cluster_mean, [cluster_mean[0]]))
                    ax3.plot(angles, values, 'o-', linewidth=2, label=cluster_name)
                    ax3.fill(angles, values, alpha=0.25)
                
                ax3.set_xticks(angles[:-1])
                ax3.set_xticklabels(feature_names)
                ax3.set_title('Cluster Characteristics (Normalized)')
                ax3.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            
            # Silhouette analysis
            from sklearn.metrics import silhouette_score
            silhouette_scores = []
            k_range = range(2, min(10, len(features)))
            
            for k in k_range:
                kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels_temp = kmeans_temp.fit_predict(features_scaled)
                score = silhouette_score(features_scaled, labels_temp)
                silhouette_scores.append(score)
            
            ax4.plot(k_range, silhouette_scores, 'bo-')
            ax4.set_xlabel('Number of Clusters (k)')
            ax4.set_ylabel('Silhouette Score')
            ax4.set_title('Optimal Number of Clusters')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('clustering_analysis')
            
        except Exception as e:
            logger.error(f"Error in clustering analysis: {e}")
            return None

    def _create_sentiment_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Analyze sentiment in video titles and descriptions."""
        try:
            sentiments = []
            for video in videos:
                # Analyze title sentiment
                title_blob = TextBlob(video.title)
                desc_blob = TextBlob(video.description)
                
                sentiments.append({
                    'title': video.title,
                    'series': video.series,
                    'title_polarity': title_blob.sentiment.polarity,
                    'title_subjectivity': title_blob.sentiment.subjectivity,
                    'desc_polarity': desc_blob.sentiment.polarity,
                    'desc_subjectivity': desc_blob.sentiment.subjectivity,
                    'view_count': video.view_count,
                    'like_count': video.like_count
                })
            
            df = pd.DataFrame(sentiments)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Sentiment Analysis', fontsize=16, fontweight='bold')
            
            # Title sentiment distribution
            ax1.hist(df['title_polarity'], bins=20, alpha=0.7, edgecolor='black', 
                    color='skyblue', label='Title Polarity')
            ax1.axvline(x=0, color='red', linestyle='--', label='Neutral')
            ax1.set_xlabel('Sentiment Polarity')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Title Sentiment Distribution')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Sentiment vs engagement
            ax2.scatter(df['title_polarity'], df['view_count'], alpha=0.6)
            ax2.set_xlabel('Title Sentiment Polarity')
            ax2.set_ylabel('View Count')
            ax2.set_title('Sentiment vs Engagement')
            ax2.grid(True, alpha=0.3)
            
            # Sentiment by series
            series_sentiment = df.groupby('series')['title_polarity'].mean().sort_values()
            ax3.barh(range(len(series_sentiment)), series_sentiment.values)
            ax3.set_yticks(range(len(series_sentiment)))
            ax3.set_yticklabels(series_sentiment.index, fontsize=8)
            ax3.set_xlabel('Average Title Sentiment')
            ax3.set_title('Average Sentiment by Series')
            ax3.grid(True, alpha=0.3)
            
            # Polarity vs Subjectivity
            scatter = ax4.scatter(df['title_polarity'], df['title_subjectivity'], 
                                c=df['view_count'], cmap='viridis', alpha=0.7)
            ax4.set_xlabel('Polarity (Negative ← → Positive)')
            ax4.set_ylabel('Subjectivity (Objective ← → Subjective)')
            ax4.set_title('Sentiment Landscape (Color = Views)')
            plt.colorbar(scatter, ax=ax4)
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('sentiment_analysis')
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return None

    def _create_topic_modeling(self, videos: VideoDataCollection) -> Optional[Path]:
        """Perform topic modeling on video content."""
        try:
            from sklearn.decomposition import LatentDirichletAllocation
            
            # Prepare text data
            documents = []
            video_metadata = []
            
            for video in videos:
                # Combine title and description
                text = f"{video.title} {video.description}"
                if len(text.strip()) > 10:  # Only include substantial text
                    documents.append(text)
                    video_metadata.append({
                        'title': video.title,
                        'series': video.series,
                        'views': video.view_count
                    })
            
            if len(documents) < 5:
                logger.warning("Insufficient text data for topic modeling")
                return None
            
            # Vectorize documents
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english', 
                                       min_df=2, max_df=0.8)
            doc_term_matrix = vectorizer.fit_transform(documents)
            
            # Perform LDA
            n_topics = min(5, len(documents) // 2)
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
            topic_distributions = lda.fit_transform(doc_term_matrix)
            
            # Get feature names
            feature_names = vectorizer.get_feature_names_out()
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Topic Modeling Analysis', fontsize=16, fontweight='bold')
            
            # Topic word clouds
            for i in range(min(2, n_topics)):
                topic_words = lda.components_[i]
                top_words_idx = topic_words.argsort()[-20:][::-1]
                top_words = [feature_names[idx] for idx in top_words_idx]
                word_weights = {word: topic_words[idx] for word, idx in zip(top_words, top_words_idx)}
                
                if i == 0:
                    wordcloud = WordCloud(width=400, height=300, 
                                        background_color='white').generate_from_frequencies(word_weights)
                    ax1.imshow(wordcloud, interpolation='bilinear')
                    ax1.set_title(f'Topic {i+1} Word Cloud')
                    ax1.axis('off')
                elif i == 1:
                    wordcloud = WordCloud(width=400, height=300, 
                                        background_color='white').generate_from_frequencies(word_weights)
                    ax2.imshow(wordcloud, interpolation='bilinear')
                    ax2.set_title(f'Topic {i+1} Word Cloud')
                    ax2.axis('off')
            
            # Topic distribution across documents
            topic_props = np.mean(topic_distributions, axis=0)
            ax3.bar(range(n_topics), topic_props)
            ax3.set_xlabel('Topic')
            ax3.set_ylabel('Average Proportion')
            ax3.set_title('Topic Prevalence')
            ax3.set_xticks(range(n_topics))
            ax3.set_xticklabels([f'Topic {i+1}' for i in range(n_topics)])
            ax3.grid(True, alpha=0.3)
            
            # Document-topic heatmap
            if len(topic_distributions) <= 20:  # Only show if manageable number
                im = ax4.imshow(topic_distributions[:20].T, cmap='Blues', aspect='auto')
                ax4.set_xlabel('Documents')
                ax4.set_ylabel('Topics')
                ax4.set_title('Document-Topic Distribution')
                ax4.set_yticks(range(n_topics))
                ax4.set_yticklabels([f'Topic {i+1}' for i in range(n_topics)])
                plt.colorbar(im, ax=ax4)
            else:
                # Show topic coherence instead
                ax4.text(0.5, 0.5, f'Generated {n_topics} topics from {len(documents)} documents', 
                        ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Topic Model Summary')
                ax4.axis('off')
            
            plt.tight_layout()
            return self._save_figure('topic_modeling')
            
        except Exception as e:
            logger.error(f"Error in topic modeling: {e}")
            return None

    def _create_word_cloud(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create word clouds from video content."""
        try:
            # Collect all text
            all_titles = ' '.join([video.title for video in videos])
            all_descriptions = ' '.join([video.description for video in videos if video.description])
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Word Cloud Analysis', fontsize=16, fontweight='bold')
            
            # Title word cloud
            if all_titles:
                wordcloud_titles = WordCloud(width=400, height=300, 
                                           background_color='white',
                                           colormap='viridis').generate(all_titles)
                ax1.imshow(wordcloud_titles, interpolation='bilinear')
                ax1.set_title('Title Word Cloud')
                ax1.axis('off')
            
            # Description word cloud
            if all_descriptions:
                wordcloud_desc = WordCloud(width=400, height=300, 
                                         background_color='white',
                                         colormap='plasma').generate(all_descriptions)
                ax2.imshow(wordcloud_desc, interpolation='bilinear')
                ax2.set_title('Description Word Cloud')
                ax2.axis('off')
            
            # Most common words in titles
            from collections import Counter
            import re
            
            title_words = re.findall(r'\b\w+\b', all_titles.lower())
            title_word_freq = Counter(title_words)
            common_words = title_word_freq.most_common(15)
            
            if common_words:
                words, counts = zip(*common_words)
                ax3.barh(range(len(words)), counts)
                ax3.set_yticks(range(len(words)))
                ax3.set_yticklabels(words)
                ax3.set_xlabel('Frequency')
                ax3.set_title('Most Common Title Words')
                ax3.grid(True, alpha=0.3)
            
            # Word frequency by series
            series_words = defaultdict(list)
            for video in videos:
                if video.series:
                    words = re.findall(r'\b\w+\b', video.title.lower())
                    series_words[video.series].extend(words)
            
            if series_words:
                series_names = list(series_words.keys())[:5]  # Top 5 series
                word_counts_by_series = []
                
                for series in series_names:
                    word_freq = Counter(series_words[series])
                    total_words = sum(word_freq.values())
                    word_counts_by_series.append(total_words)
                
                ax4.bar(range(len(series_names)), word_counts_by_series)
                ax4.set_xticks(range(len(series_names)))
                ax4.set_xticklabels([s[:15] + '...' if len(s) > 15 else s 
                                   for s in series_names], rotation=45)
                ax4.set_ylabel('Total Words')
                ax4.set_title('Word Count by Series')
                ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('word_cloud_analysis')
            
        except Exception as e:
            logger.error(f"Error creating word cloud: {e}")
            return None

    # Additional advanced methods...
    def _create_network_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create network analysis of video relationships."""
        try:
            # Create a network based on series and guest relationships
            G = nx.Graph()
            
            # Add nodes for videos
            for video in videos:
                G.add_node(video.video_id, 
                          title=video.title[:30],
                          series=video.series,
                          views=video.view_count,
                          node_type='video')
            
            # Add edges based on same series
            series_groups = defaultdict(list)
            for video in videos:
                if video.series:
                    series_groups[video.series].append(video.video_id)
            
            for series, video_ids in series_groups.items():
                for i in range(len(video_ids)):
                    for j in range(i+1, len(video_ids)):
                        G.add_edge(video_ids[i], video_ids[j], weight=1, relation='series')
            
            if len(G.nodes()) < 3:
                logger.warning("Insufficient data for network analysis")
                return None
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Network Analysis', fontsize=16, fontweight='bold')
            
            # Main network layout
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Color nodes by series
            series_list = list(set([video.series for video in videos if video.series]))
            color_map = plt.cm.Set3(np.linspace(0, 1, len(series_list)))
            series_colors = dict(zip(series_list, color_map))
            
            node_colors = []
            for node in G.nodes():
                video = next((v for v in videos if v.video_id == node), None)
                if video and video.series in series_colors:
                    node_colors.append(series_colors[video.series])
                else:
                    node_colors.append('gray')
            
            nx.draw(G, pos, ax=ax1, node_color=node_colors, node_size=50, 
                   with_labels=False, edge_color='gray', alpha=0.7)
            ax1.set_title('Video Network by Series')
            
            # Degree distribution
            degrees = [G.degree(n) for n in G.nodes()]
            ax2.hist(degrees, bins=10, alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Node Degree')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Degree Distribution')
            ax2.grid(True, alpha=0.3)
            
            # Centrality measures
            betweenness = nx.betweenness_centrality(G)
            closeness = nx.closeness_centrality(G)
            
            centrality_data = [(node, betweenness[node], closeness[node]) for node in G.nodes()]
            centrality_data.sort(key=lambda x: x[1], reverse=True)
            
            top_central = centrality_data[:min(10, len(centrality_data))]
            if top_central:
                central_nodes, bet_scores, close_scores = zip(*top_central)
                
                ax3.barh(range(len(bet_scores)), bet_scores)
                ax3.set_yticks(range(len(bet_scores)))
                ax3.set_yticklabels([next((v.title[:20] for v in videos if v.video_id == node), node) 
                                   for node in central_nodes], fontsize=8)
                ax3.set_xlabel('Betweenness Centrality')
                ax3.set_title('Most Central Videos')
                ax3.grid(True, alpha=0.3)
            
            # Network statistics
            stats_text = f"""Network Statistics:
Nodes: {G.number_of_nodes()}
Edges: {G.number_of_edges()}
Density: {nx.density(G):.3f}
Avg Clustering: {nx.average_clustering(G):.3f}
"""
            
            ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes, 
                    fontsize=12, verticalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
            ax4.set_title('Network Statistics')
            ax4.axis('off')
            
            plt.tight_layout()
            return self._save_figure('network_analysis')
            
        except Exception as e:
            logger.error(f"Error in network analysis: {e}")
            return None

    # Standard visualization methods (missing implementations)
    def _create_publication_timeline(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create publication timeline visualization."""
        try:
            videos_with_dates = [v for v in videos if v.published_at]
            if not videos_with_dates:
                logger.warning("No publication date data available")
                return None
                
            # Parse dates and create timeline
            dates = []
            for video in videos_with_dates:
                try:
                    date = pd.to_datetime(video.published_at)
                    dates.append(date)
                except:
                    continue
            
            if not dates:
                return None
                
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
            fig.suptitle('Publication Timeline Analysis', fontsize=16, fontweight='bold')
            
            # Timeline scatter
            views = [v.view_count for v in videos_with_dates[:len(dates)]]
            ax1.scatter(dates, views, alpha=0.6)
            ax1.set_xlabel('Publication Date')
            ax1.set_ylabel('Views')
            ax1.set_title('Views Over Time')
            ax1.grid(True, alpha=0.3)
            
            # Monthly publication frequency
            monthly_counts = pd.Series(dates).dt.to_period('M').value_counts().sort_index()
            ax2.plot(monthly_counts.index.astype(str), monthly_counts.values, 'bo-')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Number of Videos')
            ax2.set_title('Publication Frequency by Month')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('publication_timeline')
        except Exception as e:
            logger.error(f"Error creating publication timeline: {e}")
            return None

    def _create_duration_distribution(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create duration distribution visualization."""
        try:
            durations = []
            for video in videos:
                if video.duration:
                    duration_minutes = parse_youtube_duration(video.duration)
                    if duration_minutes > 0:
                        durations.append(duration_minutes)
            
            if not durations:
                logger.warning("No duration data available")
                return None
                
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Video Duration Analysis', fontsize=16, fontweight='bold')
            
            # Duration histogram
            ax1.hist(durations, bins=20, alpha=0.7, edgecolor='black')
            ax1.set_xlabel('Duration (minutes)')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Duration Distribution')
            ax1.grid(True, alpha=0.3)
            
            # Box plot
            ax2.boxplot(durations)
            ax2.set_ylabel('Duration (minutes)')
            ax2.set_title('Duration Box Plot')
            ax2.grid(True, alpha=0.3)
            
            # Duration vs views
            views = [v.view_count for v in videos if v.duration and parse_youtube_duration(v.duration) > 0][:len(durations)]
            if views:
                ax3.scatter(durations[:len(views)], views, alpha=0.6)
                ax3.set_xlabel('Duration (minutes)')
                ax3.set_ylabel('Views')
                ax3.set_title('Duration vs Views')
                ax3.grid(True, alpha=0.3)
            
            # Statistics
            stats_text = f"""Duration Statistics:
Mean: {np.mean(durations):.1f} min
Median: {np.median(durations):.1f} min
Std: {np.std(durations):.1f} min
Min: {min(durations):.1f} min
Max: {max(durations):.1f} min"""
            
            ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Duration Statistics')
            ax4.axis('off')
            
            plt.tight_layout()
            return self._save_figure('duration_distribution')
        except Exception as e:
            logger.error(f"Error creating duration distribution: {e}")
            return None

    def _create_transcript_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create transcript analysis visualization."""
        try:
            with_transcripts = [v for v in videos if v.transcript.strip()]
            if not with_transcripts:
                logger.warning("No transcript data available")
                return None
                
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Transcript Analysis', fontsize=16, fontweight='bold')
            
            # Transcript length distribution
            lengths = [v.transcript_length for v in with_transcripts]
            ax1.hist(lengths, bins=20, alpha=0.7, edgecolor='black')
            ax1.set_xlabel('Transcript Length (characters)')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Transcript Length Distribution')
            ax1.grid(True, alpha=0.3)
            
            # Length vs views
            views = [v.view_count for v in with_transcripts]
            ax2.scatter(lengths, views, alpha=0.6)
            ax2.set_xlabel('Transcript Length')
            ax2.set_ylabel('Views')
            ax2.set_title('Transcript Length vs Views')
            ax2.grid(True, alpha=0.3)
            
            # Coverage statistics
            total_videos = len(videos)
            with_transcripts_count = len(with_transcripts)
            coverage = (with_transcripts_count / total_videos) * 100
            
            ax3.pie([with_transcripts_count, total_videos - with_transcripts_count], 
                   labels=['With Transcripts', 'Without Transcripts'],
                   autopct='%1.1f%%', startangle=90)
            ax3.set_title('Transcript Coverage')
            
            # Top words in transcripts
            all_text = ' '.join([v.transcript for v in with_transcripts])
            words = re.findall(r'\b\w+\b', all_text.lower())
            word_freq = Counter(words)
            common_words = word_freq.most_common(10)
            
            if common_words:
                words_list, counts = zip(*common_words)
                ax4.barh(range(len(words_list)), counts)
                ax4.set_yticks(range(len(words_list)))
                ax4.set_yticklabels(words_list)
                ax4.set_xlabel('Frequency')
                ax4.set_title('Most Common Words')
                ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('transcript_analysis')
        except Exception as e:
            logger.error(f"Error creating transcript analysis: {e}")
            return None

    def _create_top_videos_chart(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create top videos chart."""
        try:
            top_by_views = sorted(videos, key=lambda v: v.view_count, reverse=True)[:15]
            top_by_likes = sorted(videos, key=lambda v: v.like_count, reverse=True)[:15]
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
            fig.suptitle('Top Performing Videos', fontsize=16, fontweight='bold')
            
            # Top by views
            titles = [v.title[:40] + '...' if len(v.title) > 40 else v.title for v in top_by_views]
            views = [v.view_count for v in top_by_views]
            
            ax1.barh(range(len(titles)), views)
            ax1.set_yticks(range(len(titles)))
            ax1.set_yticklabels(titles, fontsize=8)
            ax1.set_xlabel('Views')
            ax1.set_title('Top 15 Videos by Views')
            ax1.grid(True, alpha=0.3)
            
            # Top by likes
            titles_likes = [v.title[:40] + '...' if len(v.title) > 40 else v.title for v in top_by_likes]
            likes = [v.like_count for v in top_by_likes]
            
            ax2.barh(range(len(titles_likes)), likes)
            ax2.set_yticks(range(len(titles_likes)))
            ax2.set_yticklabels(titles_likes, fontsize=8)
            ax2.set_xlabel('Likes')
            ax2.set_title('Top 15 Videos by Likes')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('top_videos_chart')
        except Exception as e:
            logger.error(f"Error creating top videos chart: {e}")
            return None

    def _create_series_distribution(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create series distribution visualization."""
        try:
            series_stats = defaultdict(lambda: {'count': 0, 'views': 0, 'likes': 0})
            
            for video in videos:
                series = video.series or 'Unknown'
                series_stats[series]['count'] += 1
                series_stats[series]['views'] += video.view_count
                series_stats[series]['likes'] += video.like_count
            
            if not series_stats:
                logger.warning("No series data available")
                return None
                
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Series Distribution Analysis', fontsize=16, fontweight='bold')
            
            # Series count pie chart
            series_names = list(series_stats.keys())[:10]  # Top 10 series
            counts = [series_stats[s]['count'] for s in series_names]
            
            ax1.pie(counts, labels=series_names, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Video Count by Series')
            
            # Series views bar chart
            total_views = [series_stats[s]['views'] for s in series_names]
            ax2.bar(range(len(series_names)), total_views)
            ax2.set_xticks(range(len(series_names)))
            ax2.set_xticklabels(series_names, rotation=45, ha='right')
            ax2.set_ylabel('Total Views')
            ax2.set_title('Total Views by Series')
            ax2.grid(True, alpha=0.3)
            
            # Average views per video by series
            avg_views = [series_stats[s]['views'] / series_stats[s]['count'] for s in series_names]
            ax3.bar(range(len(series_names)), avg_views)
            ax3.set_xticks(range(len(series_names)))
            ax3.set_xticklabels(series_names, rotation=45, ha='right')
            ax3.set_ylabel('Average Views per Video')
            ax3.set_title('Average Views per Video by Series')
            ax3.grid(True, alpha=0.3)
            
            # Series engagement
            avg_likes = [series_stats[s]['likes'] / series_stats[s]['count'] for s in series_names]
            ax4.scatter(avg_views, avg_likes)
            for i, series in enumerate(series_names):
                ax4.annotate(series[:10], (avg_views[i], avg_likes[i]), fontsize=8)
            ax4.set_xlabel('Average Views')
            ax4.set_ylabel('Average Likes')
            ax4.set_title('Series Performance Comparison')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('series_distribution')
        except Exception as e:
            logger.error(f"Error creating series distribution: {e}")
            return None

    def _create_engagement_metrics(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create engagement metrics visualization."""
        try:
            videos_with_data = [v for v in videos if v.view_count > 0]
            if not videos_with_data:
                logger.warning("No engagement data available")
                return None
                
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Engagement Metrics Analysis', fontsize=16, fontweight='bold')
            
            # Like rate distribution
            like_rates = [v.like_count / max(v.view_count, 1) * 100 for v in videos_with_data]
            ax1.hist(like_rates, bins=20, alpha=0.7, edgecolor='black')
            ax1.set_xlabel('Like Rate (%)')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Like Rate Distribution')
            ax1.grid(True, alpha=0.3)
            
            # Comment rate distribution
            comment_rates = [v.comment_count / max(v.view_count, 1) * 100 for v in videos_with_data]
            ax2.hist(comment_rates, bins=20, alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Comment Rate (%)')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Comment Rate Distribution')
            ax2.grid(True, alpha=0.3)
            
            # Engagement scatter plot
            ax3.scatter(like_rates, comment_rates, alpha=0.6)
            ax3.set_xlabel('Like Rate (%)')
            ax3.set_ylabel('Comment Rate (%)')
            ax3.set_title('Like Rate vs Comment Rate')
            ax3.grid(True, alpha=0.3)
            
            # Top engagement videos
            engagement_scores = [(v.like_count + v.comment_count * 2) / max(v.view_count, 1) * 100 
                               for v in videos_with_data]
            top_engagement = sorted(zip(videos_with_data, engagement_scores), 
                                  key=lambda x: x[1], reverse=True)[:10]
            
            titles = [v[0].title[:30] + '...' if len(v[0].title) > 30 else v[0].title 
                     for v in top_engagement]
            scores = [v[1] for v in top_engagement]
            
            ax4.barh(range(len(titles)), scores)
            ax4.set_yticks(range(len(titles)))
            ax4.set_yticklabels(titles, fontsize=8)
            ax4.set_xlabel('Engagement Score')
            ax4.set_title('Top 10 Videos by Engagement')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('engagement_metrics')
        except Exception as e:
            logger.error(f"Error creating engagement metrics: {e}")
            return None

    def _create_monthly_activity(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create monthly activity visualization."""
        try:
            videos_with_dates = [v for v in videos if v.published_at]
            if not videos_with_dates:
                logger.warning("No date data available")
                return None
                
            # Parse dates
            monthly_data = defaultdict(lambda: {'count': 0, 'views': 0, 'likes': 0})
            
            for video in videos_with_dates:
                try:
                    date = pd.to_datetime(video.published_at)
                    month_key = date.strftime('%Y-%m')
                    monthly_data[month_key]['count'] += 1
                    monthly_data[month_key]['views'] += video.view_count
                    monthly_data[month_key]['likes'] += video.like_count
                except:
                    continue
            
            if not monthly_data:
                return None
                
            months = sorted(monthly_data.keys())
            counts = [monthly_data[m]['count'] for m in months]
            views = [monthly_data[m]['views'] for m in months]
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
            fig.suptitle('Monthly Activity Analysis', fontsize=16, fontweight='bold')
            
            # Monthly video count
            ax1.plot(months, counts, 'bo-', linewidth=2, markersize=6)
            ax1.set_xlabel('Month')
            ax1.set_ylabel('Number of Videos')
            ax1.set_title('Videos Published per Month')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Monthly total views
            ax2.plot(months, views, 'ro-', linewidth=2, markersize=6)
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Total Views')
            ax2.set_title('Total Views per Month')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._save_figure('monthly_activity')
        except Exception as e:
            logger.error(f"Error creating monthly activity: {e}")
            return None

    def _create_content_length_correlation(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create content length correlation visualization."""
        try:
            data_points = []
            for video in videos:
                if video.view_count > 0 and video.duration:
                    duration_minutes = parse_youtube_duration(video.duration)
                    if duration_minutes > 0:
                        data_points.append({
                            'duration': duration_minutes,
                            'views': video.view_count,
                            'likes': video.like_count,
                            'transcript_length': video.transcript_length,
                            'title_length': len(video.title),
                            'desc_length': len(video.description)
                        })
            
            if not data_points:
                logger.warning("No content length data available")
                return None
                
            df = pd.DataFrame(data_points)
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Content Length Correlation Analysis', fontsize=16, fontweight='bold')
            
            # Duration vs views
            ax1.scatter(df['duration'], df['views'], alpha=0.6)
            ax1.set_xlabel('Duration (minutes)')
            ax1.set_ylabel('Views')
            ax1.set_title('Duration vs Views')
            ax1.grid(True, alpha=0.3)
            
            # Transcript length vs views
            ax2.scatter(df['transcript_length'], df['views'], alpha=0.6)
            ax2.set_xlabel('Transcript Length')
            ax2.set_ylabel('Views')
            ax2.set_title('Transcript Length vs Views')
            ax2.grid(True, alpha=0.3)
            
            # Title length vs views
            ax3.scatter(df['title_length'], df['views'], alpha=0.6)
            ax3.set_xlabel('Title Length')
            ax3.set_ylabel('Views')
            ax3.set_title('Title Length vs Views')
            ax3.grid(True, alpha=0.3)
            
            # Correlation matrix
            corr_matrix = df[['duration', 'views', 'likes', 'transcript_length', 'title_length']].corr()
            im = ax4.imshow(corr_matrix, cmap='RdBu_r', aspect='auto')
            ax4.set_xticks(range(len(corr_matrix.columns)))
            ax4.set_yticks(range(len(corr_matrix.columns)))
            ax4.set_xticklabels(corr_matrix.columns, rotation=45)
            ax4.set_yticklabels(corr_matrix.columns)
            ax4.set_title('Content Length Correlations')
            
            # Add correlation values
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    ax4.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', 
                            ha='center', va='center', fontsize=8)
            
            plt.tight_layout()
            return self._save_figure('content_length_correlation')
        except Exception as e:
            logger.error(f"Error creating content length correlation: {e}")
            return None

    # Advanced visualization methods (stub implementations)
    def _create_statistical_distributions(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create statistical distributions visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Statistical Distributions Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Statistical Distributions')
            plt.tight_layout()
            return self._save_figure('statistical_distributions')
        except Exception as e:
            logger.error(f"Error creating statistical distributions: {e}")
            return None

    def _create_time_series_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create time series analysis visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Time Series Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Time Series Analysis')
            plt.tight_layout()
            return self._save_figure('time_series_analysis')
        except Exception as e:
            logger.error(f"Error creating time series analysis: {e}")
            return None

    def _create_content_ontology(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create content ontology visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Content Ontology Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Content Ontology')
            plt.tight_layout()
            return self._save_figure('content_ontology')
        except Exception as e:
            logger.error(f"Error creating content ontology: {e}")
            return None

    def _create_interactive_dashboard(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create interactive dashboard visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Interactive Dashboard\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Interactive Dashboard')
            plt.tight_layout()
            return self._save_figure('interactive_dashboard')
        except Exception as e:
            logger.error(f"Error creating interactive dashboard: {e}")
            return None

    def _create_hierarchical_clustering(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create hierarchical clustering visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Hierarchical Clustering\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Hierarchical Clustering')
            plt.tight_layout()
            return self._save_figure('hierarchical_clustering')
        except Exception as e:
            logger.error(f"Error creating hierarchical clustering: {e}")
            return None

    def _create_tsne_visualization(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create t-SNE visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 't-SNE Visualization\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('t-SNE Visualization')
            plt.tight_layout()
            return self._save_figure('tsne_visualization')
        except Exception as e:
            logger.error(f"Error creating t-SNE visualization: {e}")
            return None

    def _create_feature_importance(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create feature importance visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Feature Importance Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Feature Importance')
            plt.tight_layout()
            return self._save_figure('feature_importance')
        except Exception as e:
            logger.error(f"Error creating feature importance: {e}")
            return None

    def _create_anomaly_detection(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create anomaly detection visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Anomaly Detection\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Anomaly Detection')
            plt.tight_layout()
            return self._save_figure('anomaly_detection')
        except Exception as e:
            logger.error(f"Error creating anomaly detection: {e}")
            return None

    def _create_trend_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create trend analysis visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Trend Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Trend Analysis')
            plt.tight_layout()
            return self._save_figure('trend_analysis')
        except Exception as e:
            logger.error(f"Error creating trend analysis: {e}")
            return None

    def _create_semantic_similarity(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create semantic similarity visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Semantic Similarity Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Semantic Similarity')
            plt.tight_layout()
            return self._save_figure('semantic_similarity')
        except Exception as e:
            logger.error(f"Error creating semantic similarity: {e}")
            return None

    def _create_content_evolution(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create content evolution visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Content Evolution Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Content Evolution')
            plt.tight_layout()
            return self._save_figure('content_evolution')
        except Exception as e:
            logger.error(f"Error creating content evolution: {e}")
            return None

    def _create_engagement_prediction(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create engagement prediction visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Engagement Prediction\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Engagement Prediction')
            plt.tight_layout()
            return self._save_figure('engagement_prediction')
        except Exception as e:
            logger.error(f"Error creating engagement prediction: {e}")
            return None

    def _create_mds_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create multi-dimensional scaling visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Multi-Dimensional Scaling\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Multi-Dimensional Scaling')
            plt.tight_layout()
            return self._save_figure('multi_dimensional_scaling')
        except Exception as e:
            logger.error(f"Error creating MDS analysis: {e}")
            return None

    def _create_comparative_analysis(self, videos: VideoDataCollection) -> Optional[Path]:
        """Create comparative analysis visualization."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'Comparative Analysis\n(Implementation in progress)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Comparative Analysis')
            plt.tight_layout()
            return self._save_figure('comparative_analysis')
        except Exception as e:
            logger.error(f"Error creating comparative analysis: {e}")
            return None

    def _save_figure(self, filename: str) -> Path:
        """Save current figure with timestamp and configured settings."""
        full_filename = f"{filename}_{self.timestamp}.{self.config.figure_format}"
        file_path = self.output_dir / full_filename
        plt.savefig(file_path, dpi=self.config.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        return file_path

# ... rest of existing methods ... 

def create_visualizations(videos: VideoDataCollection, config: dict, output_dir: Path) -> List[Path]:
    """
    Module-level function to create visualizations.
    
    Args:
        videos: Video collection to visualize
        config: Configuration dictionary
        output_dir: Output directory for visualizations
        
    Returns:
        List of paths to created visualization files
    """
    from models import VisualizationConfig
    
    # Create visualization config from dictionary
    viz_config_dict = config.get('visualization', {})
    
    # Only create visualizations if enabled
    if not viz_config_dict.get('create_charts', True):
        logger.info("Chart creation disabled in configuration")
        return []
    
    viz_config = VisualizationConfig(
        chart_types=viz_config_dict.get('chart_types', ['views_vs_likes_scatter']),
        style=viz_config_dict.get('style', 'seaborn-v0_8'),
        color_palette=viz_config_dict.get('color_palette', 'husl'),
        dpi=viz_config_dict.get('dpi', 300),
        figure_format=viz_config_dict.get('figure_format', 'png'),
        output_dir=output_dir
    )
    
    # Create and use the advanced visualizer
    visualizer = AdvancedDataVisualizer(viz_config, output_dir)
    return visualizer.create_all_visualizations(videos) 