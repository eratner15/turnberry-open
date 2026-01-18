# Quick Start Guide

Get the Municipal Intent Miner running in 5 minutes.

## Step 1: Download Test PDFs

Visit these Texas city council websites and download 10-15 recent meeting documents:

**Austin** (best signal density):
- Go to: https://www.austintexas.gov/department/city-council
- Look for "Meeting Agendas & Minutes"
- Download recent City Council and Public Safety Committee PDFs

**Dallas**:
- Go to: https://dallascityhall.com/government/citycouncil
- Download recent council meeting packets

**Houston**:
- Go to: https://www.houstontx.gov/council/
- Download recent agendas/minutes

**San Antonio**:
- Go to: https://www.sanantonio.gov/Clerk/Council
- Download recent meeting documents

**Fort Worth**:
- Go to: https://www.fortworthtexas.gov/departments/city-secretary
- Download recent agendas

### What to Download

Look for PDFs with names like:
- `Council_Agenda_2024-01-15.pdf`
- `Public_Safety_Committee_Minutes.pdf`
- `Budget_Committee_Packet.pdf`

**Target**: Get 10-15 PDFs from the last 60 days. Save them all to the `test_pdfs` folder.

## Step 2: Set Up Your API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

Don't have an OpenAI key? Get one at: https://platform.openai.com/api-keys

**Cost estimate**: Processing 10-15 PDFs will cost about $0.10-$0.75 with `gpt-4o-mini`.

## Step 3: Initialize the Database

```bash
municipal-miner init --db-path ./miner.db
```

You should see:
```
✓ Database initialized successfully
  - Documents: 0
  - Signals: 0
```

## Step 4: Process Your PDFs

```bash
municipal-miner process \
  --pdf-dir ./test_pdfs \
  --vertical police-tech \
  --db-path ./miner.db
```

This will:
1. Extract text from each PDF
2. Parse metadata (city name, date, meeting type)
3. Send to LLM for classification
4. Store any signals found in the database

**Expected time**: 30-60 seconds per PDF

You'll see output like:
```
Found 12 PDF files
Vertical: police-tech
Model: gpt-4o-mini

Processing PDFs...
  ✓ Austin_Council_2024-01-09.pdf: 1 signal(s) found (confidence: 0.91)
  ○ Dallas_Planning_2024-01-10.pdf: No signals detected
  ✓ Houston_Budget_2024-01-12.pdf: 2 signal(s) found (confidence: 0.78)

Processing complete!
  - Processed: 12
  - Skipped (duplicates): 0
  - Signals found: 4
```

## Step 5: Generate Your First Report

```bash
municipal-miner report \
  --db-path ./miner.db \
  --vertical police-tech \
  --format markdown \
  --output ./first_report.md
```

Open `first_report.md` in your text editor. You should see:
- High-confidence signals with detailed analysis
- Direct quotes from meeting minutes
- Contact information (if available)
- Estimated values and timelines
- Next action items

## Step 6: Export to CSV (Optional)

For CRM integration:

```bash
municipal-miner report \
  --db-path ./miner.db \
  --vertical police-tech \
  --format csv \
  --output ./signals.csv
```

Open `signals.csv` in Excel/Google Sheets.

## Troubleshooting

### "No PDF files found"
Make sure your PDFs are directly in the `test_pdfs` folder, not in subfolders.

### "Invalid JSON response from LLM"
This occasionally happens. The tool will skip that document and continue. Check the logs with `--verbose`.

### "Module not found" errors
Make sure you installed the package:
```bash
pip install -e .
```

### Low signal detection
Try these PDFs for higher signal density:
- Public Safety Committee meetings (not regular council)
- Budget committee meetings
- Technology/IT committee meetings
- Look for meetings from Jan-March (budget season)

## What's Next?

**If you found 2-3 good signals**: You've proven the value prop!

Next steps:
1. Add more verticals (`fleet`, `water-infrastructure`)
2. Build the automated scraper
3. Set up weekly processing
4. Create email digest reports

**If you found 0-1 signals**: Try more PDFs from different sources:
- Focus on Public Safety Committee meetings
- Download budget meeting packets (larger files = more detail)
- Try different cities (Austin and Fort Worth tend to have good signal density)

## Success Criteria

You should be able to:
- [ ] Process 10+ PDFs without errors
- [ ] Find at least 2 high-confidence signals
- [ ] Generate a markdown report you'd send to a prospect
- [ ] See specific quotes, contacts, and dollar amounts

If you hit all four, **you've got a working intelligence engine**. Everything else is automation and scale.

## Questions?

Check the main README.md or open an issue on GitHub.
