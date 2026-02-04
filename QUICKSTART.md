# ARRS Quick Start Guide

## ✅ Setup Complete!

Your ARRS system is **fully installed and ready to use**!

## What Was Done

1. ✅ Virtual environment created
2. ✅ All dependencies installed (40+ packages)
3. ✅ Database initialized with schema
4. ✅ Configuration file created
5. ✅ All tests passed (4/4)

## Current Status

```
✓ All imports successful
✓ Configuration loaded
✓ Database initialized
✓ Crawler working
⚠ Anthropic API key needed for AI simulation
```

## Next Step: Add Your API Key

Edit the `.env` file and add your Anthropic API key:

```bash
# Open .env in your editor
nano .env  # or use your preferred editor

# Replace this line:
ANTHROPIC_API_KEY=sk-ant-your-key-here

# With your actual key:
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Get your API key from: https://console.anthropic.com/

## Running Your First Analysis

### Option 1: Basic Analysis (Works Without API Key)
```bash
source venv/bin/activate
python3 cli.py analyze https://example.com --output report.json
```

This will:
- Crawl the URL
- Run 3 scoring engines (ADE, ARCE, TRE)
- Generate composite score
- Identify gaps
- Save JSON report

**Note:** AI simulation will be skipped without API key.

### Option 2: Full Analysis (Requires API Key)
```bash
source venv/bin/activate
python3 cli.py analyze https://www.nike.com/t/air-max-90-mens-shoes-6n3vKB \
  --brand "Nike" \
  --category "running shoes" \
  --use-case "marathon training" \
  --output nike_report.json
```

This will:
- Everything from Option 1, PLUS:
- Query Claude API to test if brand gets recommended
- Identify missing attributes AI values
- Generate competitive gap analysis

## Example Commands

```bash
# Activate virtual environment (always do this first)
source venv/bin/activate

# Analyze a product page
python3 cli.py analyze https://www.amazon.com/dp/B08N5WRWNW \
  --brand "Amazon" \
  --category "smart speaker" \
  --use-case "home automation"

# View existing report
python3 cli.py report <analysis-id>

# Export report to JSON
python3 cli.py report <analysis-id> -o detailed_report.json

# Re-initialize database (if needed)
python3 cli.py init
```

## Understanding the Output

### Composite Score (0-100)
- **90-100 (A)**: Excellent - AI-ready
- **80-89 (B)**: Very Good
- **70-79 (C)**: Good
- **60-69 (D)**: Needs work
- **0-59 (F)**: Critical issues

### Engine Breakdown
- **ADE (30%)**: Product attributes & schema
- **ARCE (20%)**: Content readability
- **TRE (20%)**: Transaction readiness

### Gap Priorities
- **Critical**: Must fix immediately
- **High**: Important for AI citation
- **Medium**: Recommended improvements
- **Low**: Nice to have

## Project Structure

```
arrs_system/
├── venv/              # Virtual environment (✓ created)
├── data/              # Database & analysis files (✓ created)
├── arrs/              # Core system code
├── cli.py             # Command-line interface
├── .env               # Configuration (⚠ add API key)
└── README.md          # Full documentation
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify with:
which python3
# Should show: /Users/abhishekrawal/Desktop/claude_code/venv/bin/python3
```

### "API key not found" error
```bash
# Check .env file exists and has your key
cat .env | grep ANTHROPIC_API_KEY

# Should show your actual key (not "sk-ant-your-key-here")
```

### Database issues
```bash
# Re-initialize database
rm -rf data/
python3 cli.py init
```

### Crawler timeout
```bash
# Increase timeout in .env
echo "CRAWLER_TIMEOUT=60" >> .env
```

## What's Included

### Scoring Engines (3/5 implemented)
- ✅ **ADE** - Attribute Density (30%)
- ✅ **ARCE** - AI Readability (20%)
- ✅ **TRE** - Transaction Readiness (20%)
- ⏳ **ERE** - Entity Resolution (future)
- ⏳ **SVE** - Sentiment Velocity (future)

### Features
- ✅ Web crawling (BeautifulSoup)
- ✅ Schema.org extraction
- ✅ HTML parsing & analysis
- ✅ Composite scoring
- ✅ Gap identification
- ✅ AI simulation (Claude API)
- ✅ CLI interface
- ✅ JSON report export
- ✅ SQLite + JSON storage
- ⏳ REST API (future)
- ⏳ Web dashboard (future)

## Testing

Run the test suite:
```bash
source venv/bin/activate
python3 scripts/test_setup.py
```

Expected output:
```
✓ All tests passed (4/4)
System is ready to use!
```

## Getting Help

- **Documentation**: See [README.md](README.md)
- **Configuration**: See [.env.example](.env.example)
- **Issues**: Check logs in console output

## Example: Analyzing Your Own Site

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Add your API key to .env (one-time setup)
nano .env

# 3. Run analysis
python3 cli.py analyze https://yoursite.com/product \
  --brand "Your Brand" \
  --category "your product type" \
  --use-case "specific use case" \
  --output yoursite_report.json

# 4. View results
cat yoursite_report.json | python3 -m json.tool | less
```

## Success Criteria

You'll know it's working when you see:

1. **Composite Score**: 0-100 number
2. **Engine Scores**: ADE, ARCE, TRE with individual scores
3. **Gaps List**: Prioritized recommendations
4. **AI Citation**: Whether brand was mentioned by Claude

## What Makes ARRS Special

Unlike SEO tools that optimize for Google:
- 🤖 Tests actual AI behavior (not metrics)
- 📊 Optimizes for recommendations (not rankings)
- 🎯 Focuses on AI comprehension (not keywords)
- 🔍 Identifies missing attributes AI values
- 💡 Actionable gaps (not vague suggestions)

---

**System Status**: ✅ READY
**Next Action**: Add API key to `.env`
**First Command**: `python3 cli.py analyze <url>`

🚀 **You're all set to start optimizing for AI!**
