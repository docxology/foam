#!/bin/bash
# Foam-Fabric LLM Environment Startup Commands
# 
# This script contains all the commands needed to set up and run
# the complete Fabric LLM environment with Foam integration.
#
# Prerequisites:
# - Git, Python 3.6+, Go 1.24+
# - OpenAI API key
#
# Usage: 
#   chmod +x scripts/fabric/startup_commands.sh
#   ./scripts/fabric/startup_commands.sh

set -e  # Exit on any error

echo "🚀 Starting Foam-Fabric LLM Environment Setup"
echo "=============================================="

# 1. Initial Setup - Run the setup script
echo "📦 Step 1: Running fabric_foam_setup.py..."
python3 scripts/fabric/fabric_foam_setup.py

# 2. Environment Variables Setup
echo "🔧 Step 2: Setting up environment variables..."

# Set OpenAI API Key (replace with your actual key)
export OPENAI_API_KEY="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"

# Add to shell profile for persistence
if ! grep -q "OPENAI_API_KEY" ~/.bashrc; then
    echo 'export OPENAI_API_KEY="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"' >> ~/.bashrc
    echo "✅ Added OpenAI API key to ~/.bashrc"
fi

# Set up Go environment (if needed)
if ! grep -q "GOPATH" ~/.bashrc; then
    echo 'export GOROOT=/usr/local/go' >> ~/.bashrc
    echo 'export GOPATH=$HOME/go' >> ~/.bashrc
    echo 'export PATH=$GOPATH/bin:$GOROOT/bin:$HOME/.local/bin:$PATH' >> ~/.bashrc
    echo "✅ Added Go environment variables to ~/.bashrc"
fi

# 3. Fabric Setup and Configuration
echo "🤖 Step 3: Configuring Fabric..."

# Check if Fabric is accessible
FABRIC_PATH="${HOME}/go/bin/fabric"
if [ ! -f "$FABRIC_PATH" ]; then
    echo "❌ Fabric not found at $FABRIC_PATH"
    echo "Please ensure fabric_foam_setup.py completed successfully"
    exit 1
fi

echo "✅ Fabric found at: $FABRIC_PATH"

# Verify Fabric version
echo "📋 Fabric version: $($FABRIC_PATH --version)"

# 4. Virtual Environment Activation
echo "🐍 Step 4: Activating Python virtual environment..."
source venv_fabric_foam/bin/activate
echo "✅ Virtual environment activated"

# 5. Test Fabric with API
echo "🧪 Step 5: Testing Fabric with OpenAI API..."
echo "Testing Fabric integration..." | $FABRIC_PATH --pattern summarize > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Fabric is working correctly with OpenAI API"
else
    echo "❌ Fabric test failed. Check API key and configuration"
    exit 1
fi

# 6. Setup Fabric Aliases (Optional)
echo "🔗 Step 6: Setting up Fabric aliases..."

# Create aliases for common patterns
ALIAS_FILE="$HOME/.fabric_aliases"
cat > "$ALIAS_FILE" << 'EOF'
# Fabric Pattern Aliases
alias fabric-summarize="fabric --pattern summarize"
alias fabric-extract="fabric --pattern extract_wisdom"  
alias fabric-questions="fabric --pattern extract_questions"
alias fabric-improve="fabric --pattern improve_writing"
alias fabric-essay="fabric --pattern write_essay"
alias fabric-research="fabric --pattern extract_recommendations"
alias fabric-analyze="fabric --pattern analyze_prose"

# Foam-Fabric Integration Aliases
alias foam-enhance="python3 scripts/fabric/foam_fabric_llm.py"
alias foam-process="cd $PWD && source venv_fabric_foam/bin/activate && python3 scripts/fabric/foam_fabric_llm.py"

# Utility Functions
fabric-help() {
    echo "Available Fabric commands:"
    echo "  fabric-summarize    - Summarize content"
    echo "  fabric-extract      - Extract wisdom and insights" 
    echo "  fabric-questions    - Generate questions"
    echo "  fabric-improve      - Improve writing"
    echo "  fabric-essay        - Write essays"
    echo "  fabric-research     - Extract recommendations"
    echo "  fabric-analyze      - Analyze prose"
    echo ""
    echo "Foam Integration commands:"
    echo "  foam-enhance        - Run full integration demo"
    echo "  foam-process        - Process workspace with AI"
    echo ""
    echo "For all patterns: fabric --listpatterns"
}

# YouTube transcript processing
yt-summary() {
    if [ -z "$1" ]; then
        echo "Usage: yt-summary <youtube-url>"
        return 1
    fi
    fabric -y "$1" --pattern summarize
}

yt-wisdom() {
    if [ -z "$1" ]; then
        echo "Usage: yt-wisdom <youtube-url>"
        return 1
    fi
    fabric -y "$1" --pattern extract_wisdom
}
EOF

# Source aliases in bashrc if not already done
if ! grep -q "fabric_aliases" ~/.bashrc; then
    echo "source $ALIAS_FILE" >> ~/.bashrc
    echo "✅ Added Fabric aliases to ~/.bashrc"
fi

source "$ALIAS_FILE"
echo "✅ Fabric aliases loaded"

# 7. Directory Structure Setup
echo "📁 Step 7: Setting up directory structure..."

# Create additional directories for organized workflows (will be created with timestamps during runs)
# Each run creates: ai_enhanced_YYYYMMDD_HHMMSS/{summaries,research,creative,knowledge_maps,enhanced_notes}
mkdir -p workflows/{daily,weekly,research,creative}
mkdir -p templates/{note,research,essay}

echo "✅ Directory structure created"

# 8. Create useful templates
echo "📝 Step 8: Creating workflow templates..."

# Research template
cat > templates/research/research_template.md << 'EOF'
# Research: {{TOPIC}}

Date: {{DATE}}
Status: In Progress

## Research Question
{{RESEARCH_QUESTION}}

## Key Areas to Investigate
- [ ] Area 1
- [ ] Area 2  
- [ ] Area 3

## Sources
- [ ] Source 1
- [ ] Source 2

## Notes
{{NOTES}}

## AI-Generated Insights
<!-- Use: cat this_file.md | fabric --pattern extract_wisdom -->

## Questions for Further Research
<!-- Use: cat this_file.md | fabric --pattern extract_questions -->

## Summary
<!-- Use: cat this_file.md | fabric --pattern summarize -->
EOF

# Daily note template with AI integration
cat > templates/note/daily_ai_template.md << 'EOF'
# Daily Note - {{DATE}}

## Today's Focus
{{FOCUS}}

## Notes
{{NOTES}}

## Ideas & Insights
{{IDEAS}}

## Questions
{{QUESTIONS}}

---

## AI Enhancement Commands
```bash
# Summarize today's notes
cat {{DATE}}.md | fabric-summarize

# Extract key insights
cat {{DATE}}.md | fabric-extract

# Generate follow-up questions  
cat {{DATE}}.md | fabric-questions

# Improve writing
cat {{DATE}}.md | fabric-improve
```
EOF

echo "✅ Templates created"

# 9. Configuration Summary
echo "📊 Step 9: Configuration Summary"
echo "================================="
echo "✅ Foam root: $(pwd)"
echo "✅ Fabric binary: $FABRIC_PATH"
echo "✅ Virtual environment: $(pwd)/venv_fabric_foam"
echo "✅ AI enhanced directories: $(pwd)/ai_enhanced_YYYYMMDD_HHMMSS (timestamped per run)"
echo "✅ Configuration file: $(pwd)/foam_fabric_config.yaml"
echo "✅ Templates directory: $(pwd)/templates"
echo "✅ Logs directory: $(pwd)/logs"

# 10. Usage Instructions
echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "🚀 Quick Start Commands:"
echo "  foam-enhance              # Run full integration demonstration"
echo "  fabric-help               # Show available commands"
echo "  fabric --listpatterns     # List all available AI patterns"
echo ""
echo "📖 Key Files to Explore:"
echo "  ai_enhanced_YYYYMMDD_HHMMSS/  # AI-generated content (timestamped)"
echo "  foam_fabric_config.yaml   # Integration configuration"
echo "  templates/                # Useful templates"
echo ""
echo "🔗 Integration Examples:"
echo "  echo 'Your text' | fabric-summarize"
echo "  cat your_note.md | fabric-extract"
echo "  yt-summary 'https://youtube.com/watch?v=VIDEO_ID'"
echo ""
echo "⚙️  To customize patterns, edit: foam_fabric_config.yaml"
echo "📋 For detailed logs, check: logs/"
echo ""
echo "💡 Pro Tip: Use 'fabric --listpatterns' to discover 200+ AI patterns!"
echo ""
echo "Happy AI-enhanced knowledge work! 🧠✨" 