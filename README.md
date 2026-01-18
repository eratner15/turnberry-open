# Municipal Intent Miner

**Extract pre-RFP procurement intelligence from municipal meeting documents.**

Turn boring city council meeting minutes into actionable sales intelligence. This tool processes PDFs of municipal meetings and uses LLM classification to identify early-stage buying signals before official RFPs are published.

## The Value Proposition

Somewhere in Texas right now, a police chief is saying "we need to replace our body cameras" in a budget meeting. That statement gets transcribed, published as a PDF on the city website, and nobody reads it—except the vendors using this tool.

**This finds deals 3-6 months before RFPs are published.**

## Quick Start

### Installation

```bash
# Clone and install
git clone <repo-url>
cd turnberry-open
pip install -e .

# Set up your LLM API key
export OPENAI_API_KEY="your-key-here"

# Or use .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

### Zero-Setup Usage (Recommended)

The scraper downloads PDFs automatically - no manual hunting required:

```bash
# 1. Initialize the database
municipal-miner init --db-path ./miner.db

# 2. Scrape PDFs from Texas cities (automatic!)
municipal-miner scrape \
  --city all \
  --max-pdfs 5 \
  --pdf-dir ./test_pdfs

# 3. Process scraped PDFs (with anti-hallucination validation)
municipal-miner process \
  --pdf-dir ./test_pdfs \
  --vertical police-tech \
  --db-path ./miner.db

# 4. Generate an intelligence report
municipal-miner report \
  --db-path ./miner.db \
  --vertical police-tech \
  --format markdown \
  --output ./intelligence_report.md

# 5. Check statistics
municipal-miner stats --db-path ./miner.db
```

### Manual PDF Upload (Alternative)

If you prefer to download PDFs manually, skip the scrape command and add PDFs to `./test_pdfs/`.

## What It Does

### 1. Automated Scraping (NEW!)
- Automatically downloads PDFs from 5 major Texas cities
- Austin, Dallas, Houston, San Antonio, Fort Worth
- Finds council meeting agendas, minutes, and packets
- Respects rate limits (2-second delay between requests)
- No manual PDF hunting required

### 2. PDF Processing
- Extracts text from municipal meeting documents
- **Tracks page numbers for every piece of text**
- Parses metadata (municipality name, meeting date, type)
- Handles common PDF formats (including scanned documents)
- Deduplicates based on file hash

### 3. LLM Classification with Anti-Hallucination
- Uses GPT-4o-mini by default (cost-efficient)
- **Specialized prompts emphasizing VERBATIM quotes only**
- Extracts structured signals with confidence scores
- Identifies:
  - Budget approvals
  - Vendor dissatisfaction
  - Pilot programs
  - Needs discussions

### 4. Multi-Layer Validation (NEW!)
- **Quote Verification**: Every quote verified against source (≥85% similarity)
- **Page Attribution**: Track which page each quote comes from
- **Fact Checking**: Verify contact names and dollar amounts appear in source
- **Audit Trail**: Log all validation warnings
- **Only verified intelligence makes it to reports**

See [ANTI_HALLUCINATION.md](ANTI_HALLUCINATION.md) for full details on how we prevent fabrication.

### 5. Intelligence Reports
- Markdown reports with **page-attributed, verified quotes**
- CSV exports for CRM integration
- Confidence-based categorization (high/medium/low)
- Timeline of decision points
- **Verification badges** showing quote authenticity

## Supported Verticals

### Police Technology (`police-tech`)
Detects buying signals for:
- Body cameras / dash cameras
- License plate readers (ALPR/LPR)
- Evidence management software
- Records management systems (RMS)
- Radio/communication equipment
- In-car camera systems
- Digital evidence storage

**Coming soon**: `fleet`, `water-infrastructure`, `public-works`

## CLI Commands

### `scrape` (NEW!)
Automatically download PDFs from Texas municipal websites.

```bash
# Scrape all cities (5 PDFs each)
municipal-miner scrape --city all --max-pdfs 5

# Scrape specific city
municipal-miner scrape --city austin --max-pdfs 10

# Custom download directory
municipal-miner scrape \
  --city all \
  --max-pdfs 5 \
  --pdf-dir ./my_pdfs
```

**Options:**
- `--city`: City to scrape: `austin`, `dallas`, `houston`, `san-antonio`, `fort-worth`, `all` (default: `all`)
- `--max-pdfs`: Max PDFs per city (default: `5`)
- `--pdf-dir`: Download directory (default: `./test_pdfs`)

**Supported Cities:**
- Austin City Council
- Dallas City Council
- Houston City Council
- San Antonio City Clerk
- Fort Worth City Secretary

### `init`
Initialize the SQLite database.

```bash
municipal-miner init --db-path ./miner.db
```

### `process`
Process PDFs and extract signals.

```bash
municipal-miner process \
  --pdf-dir ./test_pdfs \           # Directory with PDFs
  --vertical police-tech \           # Vertical to analyze
  --db-path ./miner.db \            # Database path
  --model gpt-4o-mini               # Optional: LLM model
```

**Options:**
- `--pdf-dir`: Directory containing PDF files (required)
- `--vertical`: Analysis vertical: `police-tech`, etc. (required)
- `--db-path`: SQLite database path (default: `./miner.db`)
- `--model`: LLM model to use (default: `gpt-4o-mini`)

### `report`
Generate intelligence reports.

```bash
# Markdown report
municipal-miner report \
  --db-path ./miner.db \
  --vertical police-tech \
  --format markdown \
  --output ./report.md \
  --min-confidence 0.7

# CSV export
municipal-miner report \
  --db-path ./miner.db \
  --vertical police-tech \
  --format csv \
  --output ./signals.csv
```

**Options:**
- `--db-path`: Database path (default: `./miner.db`)
- `--vertical`: Vertical to report on (required)
- `--format`: Output format: `markdown` or `csv` (default: `markdown`)
- `--output`: Output file path (required)
- `--min-confidence`: Minimum confidence score 0.0-1.0 (default: `0.0`)

### `stats`
Show database statistics.

```bash
municipal-miner stats --db-path ./miner.db
```

## Example Output

**Terminal output during processing:**
```
Found 12 PDF files
Vertical: police-tech
Model: gpt-4o-mini

Processing PDFs...
  ✓ Austin_Council_2024-01-09.pdf: 1 signal(s) found (confidence: 0.91)
  ○ Dallas_Planning_2024-01-10.pdf: No signals detected
  ✓ FortWorth_Budget_2024-01-15.pdf: 1 signal(s) found (confidence: 0.87)

Processing complete!
  - Processed: 12
  - Skipped (duplicates): 0
  - Signals found: 4
```

**Intelligence report snippet:**
```markdown
# Texas Law Enforcement Technology Intelligence Report
**Report Generated**: January 18, 2026
**Documents Processed**: 12
**Signals Found**: 4 (2 high-confidence)

## 🔥 High-Confidence Signals (≥0.85)

### 1. Austin Police Department
**Meeting Date**: January 9, 2026
**Signal Type**: Vendor Dissatisfaction
**Confidence**: 91%

**The Opportunity**:
Chief Joseph Chacon raised concerns about current body-worn camera
cloud storage costs, which have increased 40% over the initial
contract price. Contract renewal approaching in June.

**Direct Quote**:
> "Our current body camera vendor has been reliable, but cloud
> storage fees have become unsustainable. We're paying $180K
> annually just for storage—40% more than the original contract."

**Next Steps**: Contract renewal decision scheduled for May 2026

**Contact**: Chief Joseph Chacon

**Estimated Value**: $180K/year current, potential $500K multi-year
```

## Project Structure

```
municipal-miner/
├── municipal_miner/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── database.py         # SQLite operations
│   ├── pdf_processor.py    # PDF text extraction
│   ├── classifier.py       # LLM classification
│   ├── prompts.py          # Vertical-specific prompts
│   ├── reporter.py         # Report generation
│   └── models.py           # Pydantic models
├── requirements.txt
├── setup.py
└── README.md
```

## Database Schema

### `documents` table
Stores processed PDF documents with metadata and extracted text.

### `signals` table
Stores identified procurement signals with:
- Signal type (budget_approval, vendor_dissatisfaction, etc.)
- Confidence score (0.0-1.0)
- Extracted quotes and context
- Contact information
- Estimated value
- Urgency level
- Next action items

## Development

### Adding a New Vertical

1. Create a system prompt in `municipal_miner/prompts.py`:

```python
FLEET_SYSTEM_PROMPT = """You are a fleet procurement analyst..."""

VERTICAL_PROMPTS = {
    "police-tech": POLICE_TECH_SYSTEM_PROMPT,
    "fleet": FLEET_SYSTEM_PROMPT,  # Add here
}
```

2. Use it:

```bash
municipal-miner process \
  --pdf-dir ./pdfs \
  --vertical fleet \
  --db-path ./miner.db
```

### Verbose Logging

```bash
municipal-miner --verbose process ...
```

## Cost Estimation

Using `gpt-4o-mini` (default):
- ~$0.01-0.05 per document (depending on length)
- Processing 100 PDFs: ~$2-5
- Monthly for 500 municipalities: ~$100-200

Using `gpt-4o` (higher quality):
- ~$0.10-0.50 per document
- Processing 100 PDFs: ~$20-50

## Data Sources

**Texas municipalities** (great starting points):
- [Austin City Council](https://www.austintexas.gov/department/city-council)
- [Dallas City Council](https://dallascityhall.com/government/citycouncil)
- [Houston City Council](https://www.houstontx.gov/council/)
- [San Antonio City Clerk](https://www.sanantonio.gov/Clerk/Council)
- [Fort Worth City Secretary](https://www.fortworthtexas.gov/departments/city-secretary)

Look for:
- City Council meeting minutes/packets
- Budget committee meetings
- Public Safety committee meetings
- Technology/IT committee meetings

## Roadmap

- [x] Core PDF processing
- [x] LLM classification
- [x] Police-tech vertical
- [x] Markdown/CSV reports
- [ ] Automated scraping
- [ ] Fleet vertical
- [ ] Water infrastructure vertical
- [ ] Email digest generation
- [ ] Web dashboard
- [ ] Multi-state support

## License

MIT

## Support

For issues, questions, or feature requests, open an issue on GitHub.

---

**Built with**: Python, Click, sqlite-utils, PyMuPDF, LLM (Simon Willison), Pydantic, Rich
