# ARRS - AI Readability & Recommendation Score

**Commercial Intent Optimization (CIO) Core Tool**

ARRS is a system that evaluates how well websites are understood by LLMs, trusted by AI systems, and eligible for AI-led recommendations and agentic commerce.

Unlike traditional SEO tools that optimize for search engine rankings, ARRS optimizes for **AI citation, recommendation, and transaction confidence**.

## Key Differentiators

- **AI Simulation Layer**: Tests whether Claude actually cites your brand in recommendations
- **CIO-Native Scoring**: 5 engines designed specifically for AI readability (ADE, ARCE, TRE, ERE, SVE)
- **Actionable Gap Analysis**: Identifies why AI doesn't recommend you and how to fix it
- **Agentic Commerce Ready**: Assesses if AI agents can autonomously transact

## Quick Start

### 1. Installation

```bash
# Clone the repository
cd arrs_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for JS-heavy sites)
playwright install
```

### 2. Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Initialize Database

```bash
python cli.py init
```

### 4. Run Your First Analysis

```bash
# Basic analysis (without AI simulation)
python cli.py analyze https://example.com

# Full analysis with AI simulation
python cli.py analyze https://example.com \
  --brand "Nike" \
  --category "running shoes" \
  --use-case "marathon training"

# Save report to JSON
python cli.py analyze https://example.com \
  --brand "Nike" \
  --category "running shoes" \
  --use-case "marathon training" \
  --output report.json
```

## Architecture

```
URL Input → Crawler → Parser → [ADE, ARCE, TRE Engines] → Composite Score
                                         ↓
                              AI Simulation (Claude) → Gap Analysis → Report
```

### Core Components

1. **Content Extraction Layer**
   - BeautifulSoup crawler for static sites
   - Playwright crawler for JS-heavy sites (optional)
   - Schema.org extraction (JSON-LD, microdata)

2. **Scoring Engine Layer (Prototype includes 3/5 engines)**
   - **ADE (Attribute Density Engine)** - 30% weight
     - Product attribute completeness
     - Schema.org validation
     - Description richness

   - **ARCE (AI Readability Engine)** - 20% weight
     - Semantic HTML structure
     - Content clarity (Flesch score)
     - Heading hierarchy

   - **TRE (Transaction Readiness Engine)** - 20% weight
     - Buy button detection
     - Trust signals (SSL, reviews)
     - Contact information

3. **AI Simulation Layer** (Key Differentiator)
   - Queries Claude API with recommendation prompts
   - Analyzes if your brand is cited
   - Identifies missing attributes AI values

4. **Storage Layer**
   - SQLite for structured data
   - JSON files for large content blobs

5. **Reporting Layer**
   - Composite score (0-100)
   - Engine-specific scores
   - Prioritized gap recommendations
   - AI citation analysis

## Scoring Breakdown

### Composite Score = Weighted Sum of Engines

| Engine | Weight | Focus |
|--------|--------|-------|
| ADE (Attribute Density) | 30% | Product attributes, schema completeness |
| ARCE (AI Readability) | 20% | Content clarity, semantic HTML |
| TRE (Transaction Readiness) | 20% | Buy buttons, trust signals |
| ERE (Entity Resolution)* | 20% | Brand authority (future) |
| SVE (Sentiment Velocity)* | 10% | Review momentum (future) |

*Not yet implemented in prototype

### Score Interpretation

- **90-100 (A)**: Excellent - Highly optimized for AI recommendations
- **80-89 (B)**: Very Good - Well-positioned for AI citations
- **70-79 (C)**: Good - Decent AI readability
- **60-69 (D)**: Fair - Needs optimization
- **0-59 (F)**: Critical - Major barriers

## CLI Commands

### Initialize Database
```bash
python cli.py init
```

### Analyze a URL
```bash
# Basic analysis
python cli.py analyze <url>

# With AI simulation
python cli.py analyze <url> --brand "Brand Name" --category "product type" --use-case "use case"

# Save to JSON
python cli.py analyze <url> -o output.json
```

### Generate Report
```bash
# Display report in terminal
python cli.py report <analysis_id>

# Export to JSON
python cli.py report <analysis_id> -o report.json
```

## Example Output

```
Composite ARRS Score
━━━━━━━━━━━━━━━━━━━━
     75.3/100

Engine Scores
┏━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Engine┃ Score ┃ Weight ┃ Grade ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ ADE   │ 82.0  │ 30%    │   B   │
│ ARCE  │ 71.0  │ 20%    │   C   │
│ TRE   │ 69.5  │ 20%    │   D   │
└───────┴───────┴────────┴───────┘

⚠ Found 8 improvement opportunities

Top Priority Issues:
  ● Product schema missing 'offers' field
  ● Brand is NOT cited by AI in recommendations
  ● No review or rating information found
```

## Sample Report Structure

```json
{
  "analysis_id": "uuid",
  "url": "https://example.com",
  "composite_score": 75.3,
  "grade": "C",
  "engine_scores": {
    "ADE": {
      "score": 82.0,
      "weight": 0.30,
      "details": {
        "schema_completeness_score": 32.0,
        "attribute_richness_score": 28.5,
        "image_quality_score": 15.0,
        "technical_specs_score": 6.5
      }
    }
  },
  "gaps": [
    {
      "type": "missing_offer_schema",
      "severity": "high",
      "description": "Offer schema missing from Product markup",
      "recommendation": "Add Offer schema with price, currency, and availability"
    }
  ],
  "simulation_results": {
    "brand_cited": false,
    "citation_count": 0,
    "missing_signals": ["warranty information", "size guide"]
  }
}
```

## Project Structure

```
arrs_system/
├── arrs/
│   ├── core/              # Orchestrator & exceptions
│   ├── engines/           # Scoring engines (ADE, ARCE, TRE)
│   ├── simulation/        # Claude API integration
│   ├── crawlers/          # Web crawlers
│   ├── parsers/           # HTML & schema parsers
│   ├── storage/           # Database & JSON storage
│   ├── models/            # Data models
│   ├── reporting/         # Report generation
│   └── utils/             # Logging & utilities
├── data/                  # SQLite DB & JSON files
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── cli.py                 # CLI interface
├── config.py              # Configuration
└── requirements.txt       # Dependencies
```

## Technical Details

### Database Schema

- `analyses`: Analysis sessions
- `crawled_pages`: Crawled content
- `engine_scores`: Individual engine results
- `simulation_results`: AI simulation outcomes
- `gaps`: Improvement recommendations

### Key Technologies

- **Python 3.9+**
- **FastAPI**: API framework (future)
- **Anthropic Claude API**: AI simulation
- **BeautifulSoup4**: HTML parsing
- **Playwright**: JS rendering (optional)
- **Extruct**: Schema extraction
- **SQLite**: Data storage
- **Typer**: CLI framework
- **Rich**: Terminal formatting

## Configuration Options

Edit `.env` to customize:

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...

# Crawler Settings
CRAWLER_TIMEOUT=30
PLAYWRIGHT_HEADLESS=true

# Scoring Weights (must sum to 1.0 for implemented engines)
WEIGHT_ADE=0.30
WEIGHT_ARCE=0.20
WEIGHT_TRE=0.20

# Rate Limiting
CLAUDE_RPM_LIMIT=50
```

## Development Roadmap

### Phase 1: Prototype ✓
- [x] Core infrastructure
- [x] 3 scoring engines (ADE, ARCE, TRE)
- [x] AI simulation layer
- [x] CLI interface
- [x] Report generation

### Phase 2: Full MVP (Future)
- [ ] Entity Resolution Engine (ERE)
- [ ] Sentiment Velocity Engine (SVE)
- [ ] FastAPI REST API
- [ ] Web dashboard
- [ ] Competitor comparison
- [ ] Batch processing

### Phase 3: Advanced Features (Future)
- [ ] Historical tracking
- [ ] A/B testing simulation
- [ ] Multi-LLM support (GPT-4, etc.)
- [ ] Custom scoring rules
- [ ] Integration APIs

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=arrs

# Specific test
pytest tests/test_engines/test_ade_scoring.py
```

## Troubleshooting

### "No module named 'arrs'"
Make sure you're in the project root directory and virtual environment is activated.

### "Anthropic API key not found"
Check that your `.env` file exists and contains a valid `ANTHROPIC_API_KEY`.

### Database errors
Re-initialize the database:
```bash
rm data/database.db
python cli.py init
```

### Crawler timeouts
Increase timeout in `.env`:
```bash
CRAWLER_TIMEOUT=60
```

## FAQ

**Q: How is this different from SEO tools?**
A: SEO tools optimize for search engine rankings. ARRS optimizes for AI citation and recommendation behavior.

**Q: Do I need an Anthropic API key?**
A: Yes, for the AI simulation feature. Without it, you can still run the scoring engines.

**Q: How much does it cost to run an analysis?**
A: Each analysis makes 1-2 Claude API calls, costing approximately $0.01-0.02 per analysis.

**Q: Can I use this for non-ecommerce sites?**
A: Yes, though some engines (ADE, TRE) are optimized for product pages.

## License

Proprietary - Commercial Intent Optimization (CIO) System

## Support

For issues, questions, or feature requests, please contact the development team.

---

**Built with Claude Sonnet 4.5**
