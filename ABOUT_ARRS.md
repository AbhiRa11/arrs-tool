# ARRS - AI Readability & Recommendation Score

**Developed by DevX Labs**

---

## What is ARRS?

ARRS is a tool that analyzes how well AI models (like ChatGPT, Claude, etc.) can understand and recommend your products or brand. Unlike traditional SEO that optimizes for Google search rankings, ARRS focuses on **Commercial Intent Optimization (CIO)** - making your content AI-friendly so it gets recommended by AI assistants.

**The Problem:** When users ask ChatGPT "What are the best running shoes for marathons?", will your brand be mentioned?

**The Solution:** ARRS analyzes your website and tells you exactly what to fix to increase AI citations.

---

## How It Works

1. **Enter your product/brand URL**
2. **ARRS crawls and analyzes** your website using 3 scoring engines:
   - **ADE (Attribute Density Engine)** - Checks product attributes, schema.org data, specs
   - **ARCE (AI Readability Engine)** - Analyzes content structure, readability, metadata
   - **TRE (Transaction Readiness Engine)** - Detects buy buttons, trust signals, reviews
3. **AI Simulation** - Tests if GPT-4 actually recommends your brand
4. **Get actionable recommendations** - Specific fixes to improve your AI visibility

---

## Key Features

✅ **AI Recommendation Testing**
- Simulates real AI queries to see if your brand gets cited
- Uses OpenAI GPT-4 to test actual recommendations

✅ **Multi-Engine Scoring System**
- Composite score (0-100) based on 3 specialized engines
- Detailed breakdown of each metric with explanations

✅ **Gap Analysis**
- Identifies missing attributes, poor structure, weak trust signals
- Provides code examples and specific fixes

✅ **Visual Reports**
- Interactive charts and progress bars
- Hover tooltips explaining each metric
- Downloadable JSON reports

✅ **Anti-Bot Protection Bypass**
- Uses Playwright browser automation for JavaScript-heavy sites
- Works on sites that block regular crawlers

---

## Example Websites to Test

### E-Commerce Products

**Nike Running Shoes:**
```
https://www.nike.com/t/air-zoom-pegasus-40-mens-road-running-shoes-wide-extra-wide-Fd6QMg
```
*Expected: High ARRS score due to rich product data and structured schema*

**Amazon Product Page:**
```
https://www.amazon.com/Apple-AirPods-Pro-2nd-Generation/dp/B0CHWRXH8B
```
*Expected: Very high score - excellent attributes, reviews, trust signals*

**Shopify Store Example:**
```
https://www.allbirds.com/products/mens-wool-runners
```
*Expected: Good schema, clean structure, eco-friendly attributes*

### Beauty & Skincare

**Foxtale Sunscreen (Indian Brand):**
```
https://foxtale.in/collections/sunscreens
```
*Expected: Good for testing anti-bot protection, product attributes*

**The Ordinary:**
```
https://theordinary.com/en-us/niacinamide-10-zinc-1-serum-100436.html
```
*Expected: Strong ingredient data, scientific details*

### Electronics

**Apple Product Page:**
```
https://www.apple.com/shop/buy-iphone/iphone-15
```
*Expected: Excellent technical specs, rich media*

**Best Buy Product:**
```
https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p
```
*Expected: Good reviews, pricing data, availability info*

### Fashion & Apparel

**Zara Product:**
```
https://www.zara.com/us/en/textured-knit-sweater-p04087300.html
```
*Expected: Fashion attributes, size guides, materials*

**Patagonia Jacket:**
```
https://www.patagonia.com/product/mens-down-sweater/84674.html
```
*Expected: Sustainability data, detailed specs*

### Food & Beverage

**Starbucks Coffee:**
```
https://www.starbucks.com/menu/product/406/hot
```
*Expected: Nutritional info, ingredients, customization options*

---

## What Results You Get

### 1. Composite ARRS Score (0-100)
- **90-100:** Excellent - AI will confidently recommend your brand
- **70-89:** Good - Well-optimized but room for improvement
- **50-69:** Fair - Needs optimization work
- **Below 50:** Poor - Major issues preventing AI recommendations

### 2. Engine Breakdown
- **ADE Score:** How rich is your product data?
- **ARCE Score:** How readable is your content for AI?
- **TRE Score:** How ready are you for transactions?

### 3. AI Simulation Result
- ✅ **Brand Cited:** Your brand was mentioned by GPT-4
- ❌ **Not Cited:** AI couldn't confidently recommend you

### 4. Gap Analysis
Specific issues found, like:
- "Missing GTIN field in Product schema"
- "No buy button detected"
- "Readability score too low (20/100)"
- "Missing warranty information"

Each gap includes:
- Severity level (Critical/High/Medium)
- Detailed description
- Recommended fix
- Code example

---

## Why This Matters

**The Future of Discovery:**
- 43% of consumers now use AI assistants for product recommendations
- AI doesn't crawl like Google - it needs structured, rich data
- Traditional SEO ≠ AI Optimization

**Business Impact:**
- Get cited by ChatGPT, Claude, Perplexity
- Increase brand visibility in AI-powered shopping
- Stay ahead of Commercial Intent Optimization (CIO) trends

---

## Quick Start

1. Visit: **https://missed-ambient-cleared-duncan.trycloudflare.com**
2. Paste any product/brand URL
3. Optional: Add brand name for AI simulation
4. Click "Analyze Now"
5. Wait 30-60 seconds for complete analysis
6. Review scores, simulation, and gaps
7. Download JSON report for detailed data

---

## Technical Details

**Tech Stack:**
- Python + FastAPI backend
- BeautifulSoup + Playwright for crawling
- OpenAI GPT-4 for AI simulation
- SQLite + JSON for data storage
- Chart.js for visualizations

**Supported Sites:**
- Static HTML pages
- JavaScript-heavy SPAs (React, Vue, Angular)
- Sites with anti-bot protection (using Playwright)
- E-commerce platforms (Shopify, WooCommerce, Magento)

**Analysis Time:**
- Simple pages: 15-30 seconds
- Complex sites: 30-60 seconds
- JavaScript-heavy: 45-90 seconds

---

## Pro Tips for Testing

1. **Test competitor sites** - See how you compare
2. **Use specific product pages** - Not homepage or category pages
3. **Include brand name** - For accurate AI simulation
4. **Add product category** - Helps AI simulation context
5. **Specify use case** - Makes simulation more realistic

### Example Input:
```
URL: https://www.nike.com/t/air-zoom-pegasus-40-mens-road-running-shoes
Brand: Nike
Category: running shoes
Use Case: marathon training
```

This gives the most accurate AI simulation results.

---

## Limitations

- Currently supports English content primarily
- OpenAI API required for AI simulation (uses your key)
- Analysis limited to publicly accessible pages
- Some heavily protected sites may be difficult to crawl

---

## Contact & Support

**Developed by:** DevX Labs
**Tool:** ARRS v1.0
**Public URL:** https://missed-ambient-cleared-duncan.trycloudflare.com

For questions or feedback, analyze any site and see the power of AI-optimized content!

---

**Remember:** In the AI era, it's not about ranking #1 on Google - it's about being the brand AI assistants recommend. ARRS helps you get there.
