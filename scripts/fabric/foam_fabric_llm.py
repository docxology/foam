#!/usr/bin/env python3
"""
Foam and Fabric LLM Integration Script

This script demonstrates and implements creative integration between Foam (knowledge management)
and Fabric (AI augmentation framework), providing automated workflows for enhanced productivity.

Prerequisites:
- Run fabric_foam_setup.py first to set up the environment
- OpenAI API key configured in environment

Features:
- Automated note processing with AI patterns
- Knowledge extraction and enhancement
- Creative content generation workflows
- Integration with existing Foam recipes and workflows

Author: AI Assistant
Version: 1.0.0
"""

import os
import sys
import subprocess
import logging
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml


class FoamFabricIntegrator:
    """
    A comprehensive integration system between Foam knowledge management and Fabric AI.
    
    This class provides various workflows and automation capabilities:
    - Note enhancement and summarization
    - Knowledge extraction from content
    - Creative content generation
    - Automated tagging and organization
    - Research assistance workflows
    """
    
    def __init__(self, foam_root: Optional[Path] = None):
        """
        Initialize the Foam-Fabric integrator.
        
        Args:
            foam_root: Path to Foam workspace root. Detected automatically if not provided.
        """
        self.foam_root = self._find_foam_root(foam_root)
        self.fabric_binary = self._find_fabric_binary()
        self.setup_logging()
        
        # Configuration
        self.config = self._load_configuration()
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = self.foam_root / f"ai_enhanced_{timestamp}"
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Initialized Foam-Fabric Integrator")
        self.logger.info(f"Foam root: {self.foam_root}")
        self.logger.info(f"Fabric binary: {self.fabric_binary}")
    
    def _find_foam_root(self, foam_root: Optional[Path] = None) -> Path:
        """Find the Foam project root directory."""
        if foam_root:
            return Path(foam_root)
            
        current = Path.cwd()
        while current != current.parent:
            if (current / "package.json").exists() and (current / "packages" / "foam-vscode").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _find_fabric_binary(self) -> str:
        """Find the Fabric binary location."""
        locations = [
            shutil.which("fabric"),
            Path.home() / "go" / "bin" / "fabric",
            "./venv_fabric_foam/bin/fabric"
        ]
        
        for location in locations:
            if location and Path(location).exists():
                return str(location)
        
        raise RuntimeError("Fabric binary not found. Please run fabric_foam_setup.py first.")
    
    def setup_logging(self) -> None:
        """Setup comprehensive logging."""
        log_dir = self.foam_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"foam_fabric_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized. Log file: {log_file}")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration for integration workflows."""
        config_file = self.foam_root / "foam_fabric_config.yaml"
        
        default_config = {
            "patterns": {
                "summarize": "summarize",
                "extract_wisdom": "extract_wisdom",
                "extract_questions": "extract_questions",
                "improve_writing": "improve_writing",
                "create_tags": "extract_main_activities",
                "analyze_content": "analyze_prose"
            },
            "workflows": {
                "note_enhancement": True,
                "knowledge_extraction": True,
                "research_assistance": True,
                "creative_writing": True
            },
            "output_formats": {
                "enhanced_notes": "markdown",
                "summaries": "markdown", 
                "extractions": "json"
            }
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
                self.logger.info(f"Created default configuration: {config_file}")
        
        return default_config
    
    def _run_fabric_pattern(self, pattern: str, input_text: str, 
                           additional_args: List[str] = None) -> str:
        """
        Execute a Fabric pattern with input text.
        
        Args:
            pattern: Name of the Fabric pattern to use
            input_text: Text to process
            additional_args: Additional command line arguments
            
        Returns:
            Processed output from Fabric
        """
        args = [self.fabric_binary, "--pattern", pattern]
        if additional_args:
            args.extend(additional_args)
        
        self.logger.debug(f"Running Fabric pattern: {pattern}")
        
        try:
            result = subprocess.run(
                args,
                input=input_text,
                text=True,
                capture_output=True,
                check=True
            )
            
            self.logger.info(f"Successfully processed with pattern: {pattern}")
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Fabric pattern failed: {pattern}")
            self.logger.error(f"Error: {e.stderr}")
            raise
    
    def enhance_foam_note(self, note_path: Path, patterns: List[str] = None) -> Dict[str, Any]:
        """
        Enhance a Foam note using multiple Fabric patterns.
        
        Args:
            note_path: Path to the note file
            patterns: List of patterns to apply. Uses defaults if not provided.
            
        Returns:
            Dictionary containing enhanced content and metadata
        """
        if not note_path.exists():
            raise FileNotFoundError(f"Note not found: {note_path}")
        
        if patterns is None:
            patterns = ["summarize", "extract_wisdom", "extract_questions"]
        
        self.logger.info(f"Enhancing note: {note_path}")
        
        # Read original note
        with open(note_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        enhancements = {
            "original_file": str(note_path),
            "timestamp": datetime.now().isoformat(),
            "enhancements": {}
        }
        
        # Apply each pattern
        for pattern in patterns:
            try:
                fabric_pattern = self.config["patterns"].get(pattern, pattern)
                enhanced_content = self._run_fabric_pattern(fabric_pattern, original_content)
                enhancements["enhancements"][pattern] = enhanced_content
                self.logger.info(f"Applied pattern '{pattern}' to {note_path.name}")
            except Exception as e:
                self.logger.error(f"Failed to apply pattern '{pattern}': {e}")
                enhancements["enhancements"][pattern] = f"Error: {str(e)}"
        
        # Save enhanced note
        enhanced_note_path = self.output_dir / f"enhanced_{note_path.name}"
        self._save_enhanced_note(enhancements, enhanced_note_path)
        
        return enhancements
    
    def _save_enhanced_note(self, enhancements: Dict[str, Any], output_path: Path) -> None:
        """Save enhanced note with AI-generated content."""
        content = f"""# Enhanced Note: {Path(enhancements['original_file']).name}

Generated: {enhancements['timestamp']}
Original: {enhancements['original_file']}

---

"""
        
        for pattern, result in enhancements["enhancements"].items():
            content += f"## {pattern.replace('_', ' ').title()}\n\n{result}\n\n---\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Saved enhanced note: {output_path}")
    
    def process_foam_workspace(self, file_pattern: str = "*.md") -> Dict[str, Any]:
        """
        Process all notes in the Foam workspace with AI enhancement.
        
        Args:
            file_pattern: Glob pattern for files to process
            
        Returns:
            Summary of processing results
        """
        self.logger.info(f"Processing Foam workspace with pattern: {file_pattern}")
        
        # Find all matching files
        note_files = list(self.foam_root.glob(file_pattern))
        note_files.extend(list(self.foam_root.glob(f"**/{file_pattern}")))
        
        # Filter out generated files and directories
        excluded_dirs = {".git", "node_modules", "venv_fabric_foam", "fabric", "logs"}
        # Also exclude any ai_enhanced directories
        excluded_patterns = ["ai_enhanced"]
        note_files = [f for f in note_files if not any(part in excluded_dirs for part in f.parts) 
                     and not any(pattern in str(f) for pattern in excluded_patterns)]
        
        self.logger.info(f"Found {len(note_files)} notes to process")
        
        results = {
            "processed_files": [],
            "failed_files": [],
            "summary": {}
        }
        
        for note_file in note_files[:10]:  # Limit to 10 files for demo
            try:
                enhancement_result = self.enhance_foam_note(note_file)
                results["processed_files"].append({
                    "file": str(note_file),
                    "enhancements": list(enhancement_result["enhancements"].keys())
                })
            except Exception as e:
                self.logger.error(f"Failed to process {note_file}: {e}")
                results["failed_files"].append({"file": str(note_file), "error": str(e)})
        
        results["summary"] = {
            "total_found": len(note_files),
            "processed": len(results["processed_files"]),
            "failed": len(results["failed_files"]),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save processing summary
        summary_file = self.output_dir / "processing_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Workspace processing complete. Summary saved to: {summary_file}")
        return results
    
    def create_knowledge_map(self, topic: str) -> str:
        """
        Create a knowledge map for a given topic using AI analysis.
        
        Args:
            topic: Topic to create knowledge map for
            
        Returns:
            Generated knowledge map content
        """
        self.logger.info(f"Creating knowledge map for topic: {topic}")
        
        # Search for related notes
        related_notes = self._find_related_notes(topic)
        
        # Combine content from related notes
        combined_content = f"Topic: {topic}\n\nRelated content:\n\n"
        for note_path in related_notes:
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                combined_content += f"## {note_path.name}\n{content}\n\n"
            except Exception as e:
                self.logger.warning(f"Could not read {note_path}: {e}")
        
        # Generate knowledge map using extract_wisdom pattern
        knowledge_map = self._run_fabric_pattern("extract_wisdom", combined_content)
        
        # Save knowledge map
        map_file = self.output_dir / f"knowledge_map_{topic.lower().replace(' ', '_')}.md"
        with open(map_file, 'w', encoding='utf-8') as f:
            f.write(f"# Knowledge Map: {topic}\n\nGenerated: {datetime.now().isoformat()}\n\n{knowledge_map}")
        
        self.logger.info(f"Knowledge map saved: {map_file}")
        return knowledge_map
    
    def _find_related_notes(self, topic: str) -> List[Path]:
        """Find notes related to a given topic."""
        related_notes = []
        search_terms = topic.lower().split()
        
        for note_file in self.foam_root.glob("**/*.md"):
            if (any(part in {".git", "node_modules", "venv_fabric_foam", "fabric", "logs"} 
                   for part in note_file.parts) or
                "ai_enhanced" in str(note_file)):
                continue
                
            try:
                with open(note_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # Simple relevance scoring
                relevance_score = sum(content.count(term) for term in search_terms)
                if relevance_score > 0:
                    related_notes.append(note_file)
                    
            except Exception:
                continue
        
        return related_notes[:5]  # Return top 5 related notes
    
    def generate_research_assistant(self, research_query: str) -> Dict[str, Any]:
        """
        Create a research assistant workflow for a given query.
        
        Args:
            research_query: Research question or topic
            
        Returns:
            Research assistance results
        """
        self.logger.info(f"Generating research assistance for: {research_query}")
        
        research_results = {
            "query": research_query,
            "timestamp": datetime.now().isoformat(),
            "research_plan": "",
            "questions": "",
            "related_knowledge": "",
            "next_steps": ""
        }
        
        # Generate research plan
        research_plan_prompt = f"""
        Research Query: {research_query}
        
        Based on this research query, provide a structured research plan including:
        1. Key areas to investigate
        2. Research methodology
        3. Information sources to consider
        4. Expected outcomes
        """
        
        research_results["research_plan"] = self._run_fabric_pattern(
            "extract_wisdom", research_plan_prompt
        )
        
        # Generate research questions
        research_results["questions"] = self._run_fabric_pattern(
            "extract_questions", f"Research topic: {research_query}"
        )
        
        # Find related knowledge in Foam workspace
        related_notes = self._find_related_notes(research_query)
        if related_notes:
            related_content = "\n\n".join([
                f"Note: {note.name}\n{open(note).read()[:500]}..."
                for note in related_notes[:3]
            ])
            research_results["related_knowledge"] = self._run_fabric_pattern(
                "summarize", related_content
            )
        
        # Save research assistant results
        research_file = self.output_dir / f"research_assistant_{research_query.lower().replace(' ', '_')}.md"
        self._save_research_results(research_results, research_file)
        
        return research_results
    
    def _save_research_results(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save research assistant results."""
        content = f"""# Research Assistant: {results['query']}

Generated: {results['timestamp']}

## Research Plan
{results['research_plan']}

## Key Questions
{results['questions']}

## Related Knowledge in Workspace
{results['related_knowledge']}

## Next Steps
{results.get('next_steps', 'Continue research based on the plan above.')}

---

*Generated by Foam-Fabric Integration System*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Research results saved: {output_path}")
    
    def create_creative_writing_workflow(self, prompt: str, writing_type: str = "essay") -> str:
        """
        Create a creative writing workflow using AI assistance.
        
        Args:
            prompt: Writing prompt or topic
            writing_type: Type of writing (essay, story, article, etc.)
            
        Returns:
            Generated creative content
        """
        self.logger.info(f"Creating {writing_type} for prompt: {prompt}")
        
        # Choose appropriate pattern based on writing type
        pattern_map = {
            "essay": "write_essay",
            "micro_essay": "write_micro_essay", 
            "article": "improve_writing",
            "story": "write_essay",  # Can be adapted
            "summary": "summarize"
        }
        
        pattern = pattern_map.get(writing_type, "write_essay")
        
        # Generate content
        generated_content = self._run_fabric_pattern(pattern, prompt)
        
        # Save creative work
        output_file = self.output_dir / f"{writing_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {writing_type.title()}: Generated Content\n\n")
            f.write(f"**Prompt:** {prompt}\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(generated_content)
        
        self.logger.info(f"Creative content saved: {output_file}")
        return generated_content
    
    def demonstrate_integration_capabilities(self) -> None:
        """Demonstrate various integration capabilities between Foam and Fabric."""
        self.logger.info("=== Demonstrating Foam-Fabric Integration Capabilities ===")
        
        # 1. Create sample content for demonstration
        demo_note = self.foam_root / "demo_integration_note.md"
        demo_content = """# AI and Knowledge Management Integration

This is a demonstration note showing how Foam (knowledge management) can be enhanced with Fabric (AI augmentation).

## Key Concepts

- **Foam**: A personal knowledge management system built on VS Code
- **Fabric**: An AI framework for augmenting human capabilities
- **Integration**: Combining structured knowledge with AI processing

## Benefits

1. Automated content summarization
2. Knowledge extraction and organization
3. Research assistance workflows
4. Creative content generation
5. Enhanced note-taking and linking

## Research Questions

- How can AI improve knowledge management workflows?
- What are the best practices for AI-human collaboration?
- How do we maintain knowledge quality while scaling with AI?

## Next Steps

Explore specific use cases and develop automated workflows.
"""
        
        with open(demo_note, 'w', encoding='utf-8') as f:
            f.write(demo_content)
        
        self.logger.info("Created demonstration note")
        
        # 2. Enhance the demo note
        self.logger.info("--- Enhancing Demo Note ---")
        enhancement_result = self.enhance_foam_note(demo_note)
        
        # 3. Create knowledge map
        self.logger.info("--- Creating Knowledge Map ---")
        knowledge_map = self.create_knowledge_map("AI and Knowledge Management")
        
        # 4. Generate research assistance
        self.logger.info("--- Generating Research Assistance ---")
        research_result = self.generate_research_assistant(
            "How can AI improve personal knowledge management systems?"
        )
        
        # 5. Create creative content
        self.logger.info("--- Creating Creative Content ---")
        creative_content = self.create_creative_writing_workflow(
            "The future of AI-enhanced knowledge work", "essay"
        )
        
        # 6. Generate summary report
        self.logger.info("--- Generating Summary Report ---")
        self._generate_demonstration_report()
        
        self.logger.info("=== Integration Demonstration Complete ===")
    
    def _generate_demonstration_report(self) -> None:
        """Generate a comprehensive demonstration report."""
        report_content = f"""# Foam-Fabric Integration Demonstration Report

Generated: {datetime.now().isoformat()}

## Overview

This report demonstrates the integration capabilities between Foam (knowledge management) 
and Fabric (AI augmentation framework).

## Capabilities Demonstrated

### 1. Note Enhancement
- Automated summarization of existing notes
- Wisdom extraction from content
- Question generation for deeper exploration
- Writing improvement suggestions

### 2. Knowledge Mapping
- Topic-based knowledge organization
- Automated relationship discovery
- Content synthesis across multiple notes

### 3. Research Assistance
- Research plan generation
- Question formulation
- Related knowledge discovery
- Next steps recommendations

### 4. Creative Writing Workflows
- AI-assisted content creation
- Multiple writing formats supported
- Prompt-based generation

## Files Generated

Check the timestamped `ai_enhanced_YYYYMMDD_HHMMSS/` directory for:
- Enhanced notes with AI analysis
- Knowledge maps for specific topics
- Research assistant outputs
- Creative writing samples
- Processing summaries

## Integration Benefits

1. **Productivity Enhancement**: Automated processing of knowledge assets
2. **Quality Improvement**: AI-powered analysis and enhancement
3. **Discovery**: Finding connections and patterns in existing knowledge
4. **Creativity**: AI-assisted content generation and ideation
5. **Research**: Structured approach to information gathering

## Configuration

Integration behavior can be customized via `foam_fabric_config.yaml`:
- Pattern mappings for different AI operations
- Workflow enablement/disablement
- Output format preferences

## Next Steps

1. Customize patterns for specific use cases
2. Develop domain-specific workflows
3. Integrate with existing Foam recipes
4. Explore advanced AI patterns from Fabric library
5. Create automated content pipelines

---

*This integration system bridges the gap between structured knowledge management 
and AI-powered content processing, creating new possibilities for enhanced 
productivity and creativity in knowledge work.*
"""
        
        report_file = self.output_dir / "integration_demonstration_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Demonstration report saved: {report_file}")


def main():
    """Main entry point for the Foam-Fabric integration system."""
    try:
        # Initialize the integrator
        integrator = FoamFabricIntegrator()
        
        # Run comprehensive demonstration
        integrator.demonstrate_integration_capabilities()
        
        print("\n" + "="*60)
        print("🎉 FOAM-FABRIC INTEGRATION DEMONSTRATION COMPLETE!")
        print("="*60)
        print(f"📁 Enhanced content saved to: {integrator.output_dir}")
        print(f"📋 Check logs directory for detailed execution logs")
        print(f"⚙️  Configuration file: {integrator.foam_root}/foam_fabric_config.yaml")
        print("\n🚀 Integration capabilities ready for your workflows!")
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        logging.exception("Integration system error")
        sys.exit(1)


if __name__ == "__main__":
    main()