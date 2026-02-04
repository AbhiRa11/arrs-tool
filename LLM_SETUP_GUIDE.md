# LLM Setup Guide for ARRS

ARRS now supports **two options** for AI simulation:

## Option 1: Ollama (Local, Free, No API Key Needed) ⭐ RECOMMENDED FOR TESTING

### What is Ollama?
Ollama runs AI models locally on your computer - completely free, private, and no API keys required!

### Installation

#### Mac
```bash
# Install Ollama
brew install ollama

# Or download from: https://ollama.ai
```

#### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

#### Windows
Download from: https://ollama.ai/download

### Setup

1. **Start Ollama** (one-time, runs in background):
```bash
ollama serve
```

2. **Download a model** (choose one):
```bash
# Small & fast (1.5GB) - good for testing
ollama pull phi

# Balanced (4GB) - recommended
ollama pull llama2

# Larger & better (7GB)
ollama pull mistral

# Latest & best (4GB)
ollama pull llama3
```

3. **Configure ARRS** - Your `.env` file should have:
```bash
# Leave API key empty
ANTHROPIC_API_KEY=

# Use Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2  # or phi, mistral, llama3
```

4. **Test it**:
```bash
source venv/bin/activate
python3 cli.py analyze https://example.com \
  --brand "Example" \
  --category "website" \
  --use-case "information"
```

### Pros of Ollama
- ✅ **FREE** - no API costs
- ✅ **Private** - data never leaves your computer
- ✅ **No API keys** - works immediately
- ✅ **Offline** - works without internet
- ✅ **Fast** - runs on your GPU if available

### Cons of Ollama
- ⚠️ Requires ~4-7GB disk space for models
- ⚠️ Slightly less accurate than Claude
- ⚠️ Needs decent hardware (8GB+ RAM recommended)

---

## Option 2: Claude API (Cloud, Best Quality)

### What is Claude API?
Anthropic's Claude API - the highest quality AI, same as used in Claude.ai

### Setup

1. **Get API Key**:
   - Go to: https://console.anthropic.com/
   - Sign up / Log in
   - Create an API key
   - Note: Requires credit card, ~$0.01-0.02 per analysis

2. **Configure ARRS** - Edit `.env`:
```bash
# Add your API key
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

# Use Claude
LLM_PROVIDER=claude
```

3. **Test it**:
```bash
source venv/bin/activate
python3 cli.py analyze https://example.com \
  --brand "Example" \
  --category "website" \
  --use-case "information"
```

### Pros of Claude
- ✅ **Best quality** - most accurate recommendations
- ✅ **No setup** - just add API key
- ✅ **Works anywhere** - cloud-based
- ✅ **No hardware requirements** - runs on any machine

### Cons of Claude
- ⚠️ Costs money (~$0.01-0.02 per analysis)
- ⚠️ Requires API key
- ⚠️ Requires internet
- ⚠️ Data sent to Anthropic servers

---

## Option 3: No LLM (Scores Only)

You can run ARRS **without any LLM** - it will skip AI simulation but still:
- ✅ Crawl the website
- ✅ Run all scoring engines (ADE, ARCE, TRE)
- ✅ Generate composite score
- ✅ Identify gaps from scoring engines

Just leave `.env` with:
```bash
ANTHROPIC_API_KEY=
LLM_PROVIDER=  # or remove this line
```

Run without simulation flags:
```bash
python3 cli.py analyze https://example.com
```

---

## Switching Between Options

You can switch at any time by editing `.env`:

### Switch to Ollama:
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
```

### Switch to Claude:
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

### Or override per-analysis:
```bash
# Use Ollama for this analysis
python3 cli.py analyze https://example.com --llm ollama

# Use Claude for this analysis
python3 cli.py analyze https://example.com --llm claude
```

---

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# Test if it's working
curl http://localhost:11434/api/tags
```

### "Model not found"
```bash
# Download the model
ollama pull llama2

# List available models
ollama list
```

### "Anthropic API key not found"
```bash
# Check your .env file
cat .env | grep ANTHROPIC_API_KEY

# Make sure it starts with sk-ant-
```

---

## Recommended Setup

### For Testing/Development:
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=phi  # Small & fast
```

### For Production/Best Results:
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

### For Quick Scoring (No Simulation):
```bash
# Just run without --brand, --category, --use-case flags
python3 cli.py analyze https://example.com
```

---

## Cost Comparison

| Option | Cost | Setup Time | Quality |
|--------|------|------------|---------|
| **Ollama** | $0 (FREE) | 5 min | Good (85%) |
| **Claude** | ~$0.01-0.02/analysis | 2 min | Excellent (100%) |
| **No LLM** | $0 (FREE) | 0 min | N/A (no simulation) |

---

## Quick Start Commands

### With Ollama (Free):
```bash
# 1. Install Ollama
brew install ollama  # Mac
# OR download from https://ollama.ai

# 2. Start Ollama
ollama serve

# 3. Download model (in new terminal)
ollama pull llama2

# 4. Run ARRS
source venv/bin/activate
python3 cli.py analyze https://example.com \
  --brand "Example" \
  --category "website" \
  --use-case "information" \
  --output report.json
```

### With Claude API:
```bash
# 1. Get API key from console.anthropic.com
# 2. Add to .env:
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env
echo "LLM_PROVIDER=claude" >> .env

# 3. Run ARRS
source venv/bin/activate
python3 cli.py analyze https://example.com \
  --brand "Example" \
  --category "website" \
  --use-case "information" \
  --output report.json
```

### Without LLM (Scoring Only):
```bash
source venv/bin/activate
python3 cli.py analyze https://example.com --output report.json
```

---

**Choose Ollama** if you want free, private, and fast testing.
**Choose Claude** if you need the best quality and don't mind paying.
**Choose No LLM** if you only want scoring without AI simulation.

🚀 **Start with Ollama + phi model** - it's free, fast, and works great for testing!
