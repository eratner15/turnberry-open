#!/bin/bash
# Example workflow for Municipal Intent Miner
# This shows the complete pipeline from setup to report generation

set -e  # Exit on error

echo "==================================================================="
echo "Municipal Intent Miner - Example Workflow"
echo "==================================================================="
echo ""

# Step 1: Check for API key
echo "Step 1: Checking for OPENAI_API_KEY..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set"
    echo ""
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='sk-your-key-here'"
    echo ""
    echo "Or create a .env file:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your key"
    exit 1
fi
echo "✓ API key found"
echo ""

# Step 2: Check for PDFs
echo "Step 2: Checking for test PDFs..."
PDF_COUNT=$(ls -1 test_pdfs/*.pdf 2>/dev/null | wc -l)
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "❌ No PDFs found in test_pdfs/"
    echo ""
    echo "Please download 10-15 PDFs from Texas city council websites."
    echo "See QUICKSTART.md for download links."
    exit 1
fi
echo "✓ Found $PDF_COUNT PDF files"
echo ""

# Step 3: Initialize database
echo "Step 3: Initializing database..."
municipal-miner init --db-path ./miner.db
echo ""

# Step 4: Process PDFs
echo "Step 4: Processing PDFs (this may take a few minutes)..."
echo ""
municipal-miner process \
  --pdf-dir ./test_pdfs \
  --vertical police-tech \
  --db-path ./miner.db
echo ""

# Step 5: Show statistics
echo "Step 5: Database statistics..."
municipal-miner stats --db-path ./miner.db
echo ""

# Step 6: Generate markdown report
echo "Step 6: Generating intelligence report..."
municipal-miner report \
  --db-path ./miner.db \
  --vertical police-tech \
  --format markdown \
  --output ./intelligence_report.md \
  --min-confidence 0.0
echo ""

# Step 7: Generate CSV export
echo "Step 7: Generating CSV export..."
municipal-miner report \
  --db-path ./miner.db \
  --vertical police-tech \
  --format csv \
  --output ./signals.csv \
  --min-confidence 0.0
echo ""

echo "==================================================================="
echo "✓ Workflow complete!"
echo "==================================================================="
echo ""
echo "Your reports are ready:"
echo "  📄 intelligence_report.md - Full intelligence report"
echo "  📊 signals.csv - CSV export for CRM"
echo "  💾 miner.db - SQLite database with all data"
echo ""
echo "Next steps:"
echo "  1. Open intelligence_report.md to review signals"
echo "  2. Import signals.csv into your CRM"
echo "  3. Process more PDFs by adding them to test_pdfs/"
echo ""
