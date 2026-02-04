const form = document.getElementById('analyzeForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const error = document.getElementById('error');

let currentAnalysisId = null;
let scoreChart = null;

// Engine descriptions and metric explanations
const ENGINE_INFO = {
    'ADE': {
        name: 'Attribute Density Engine',
        description: 'Measures how well your product attributes are structured for AI comprehension',
        weight: 30,
        metrics: {
            'schema_completeness': 'How complete is your Schema.org Product markup',
            'attribute_richness': 'Number and depth of product attributes',
            'image_quality': 'Image availability and metadata quality',
            'specifications': 'Technical specification depth'
        }
    },
    'ARCE': {
        name: 'AI Readability & Composability Engine',
        description: 'Evaluates how easily AI can understand and extract your content',
        weight: 20,
        metrics: {
            'semantic_html_score': 'Use of semantic HTML5 elements',
            'readability_score': 'Flesch reading ease score',
            'heading_hierarchy_score': 'Proper H1-H6 structure',
            'metadata_score': 'Meta tags and descriptions'
        }
    },
    'TRE': {
        name: 'Transaction Readiness Engine',
        description: 'Checks if AI can identify clear purchase pathways',
        weight: 20,
        metrics: {
            'cta_score': 'Call-to-action button detection',
            'trust_score': 'SSL, reviews, and trust signals',
            'contact_score': 'Contact information availability',
            'payment_score': 'Payment method visibility'
        }
    }
};

// Detailed metric explanations with tooltips
const METRIC_EXPLANATIONS = {
    'semantic_html_score': {
        title: 'Semantic HTML Score',
        description: 'Measures the use of meaningful HTML5 elements like <article>, <section>, <nav>, <header>',
        importance: 'AI uses semantic structure to understand content hierarchy and relationships',
        range: '0-100 points',
        good: '60+ (Good use of semantic tags)',
        bad: '0-30 (Mostly generic divs)'
    },
    'readability_score': {
        title: 'Flesch Reading Ease',
        description: 'Calculates how easy your text is to read based on sentence and word length',
        importance: 'Simpler text helps AI extract key information more accurately',
        range: '0-100 (higher is easier)',
        good: '60-70 (Easily understood)',
        bad: '0-30 (Very difficult to read)'
    },
    'flesch_reading_ease': {
        title: 'Flesch Reading Ease',
        description: 'Calculates how easy your text is to read based on sentence and word length',
        importance: 'Simpler text helps AI extract key information more accurately',
        range: '0-100 (higher is easier)',
        good: '60-70 (Easily understood)',
        bad: '0-30 (Very difficult to read)'
    },
    'heading_hierarchy_score': {
        title: 'Heading Hierarchy',
        description: 'Checks for proper H1-H6 structure (one H1, proper nesting)',
        importance: 'AI uses headings to understand page structure and topic organization',
        range: '0-100 points',
        good: '100 (Perfect hierarchy)',
        bad: '0 (No H1 or broken structure)'
    },
    'has_valid_hierarchy': {
        title: 'Valid Heading Hierarchy',
        description: 'Boolean check if headings follow proper nesting order',
        importance: 'Proper nesting helps AI understand content sections',
        range: 'true/false',
        good: 'true (Proper nesting)',
        bad: 'false (Broken structure)'
    },
    'metadata_score': {
        title: 'Metadata Completeness',
        description: 'Checks for meta description, title tags, and Open Graph tags',
        importance: 'Metadata provides AI with page summaries and context',
        range: '0-100 points',
        good: '80+ (Complete metadata)',
        bad: '0-20 (Missing key tags)'
    },
    'semantic_element_count': {
        title: 'Semantic Element Count',
        description: 'Number of semantic HTML5 elements found on the page',
        importance: 'More semantic elements = better structure for AI',
        range: 'Count (higher is better)',
        good: '10+ elements',
        bad: '0-2 elements'
    },
    'word_count': {
        title: 'Content Word Count',
        description: 'Total number of readable words on the page',
        importance: 'AI needs sufficient content to understand your offering',
        range: 'Count',
        good: '300+ words',
        bad: '<100 words'
    },
    'schema_completeness': {
        title: 'Schema.org Completeness',
        description: 'Percentage of required Product schema fields present',
        importance: 'Complete schemas help AI extract structured product data',
        range: '0-1 (0-100%)',
        good: '0.8+ (80%+ complete)',
        bad: '0-0.3 (Missing key fields)'
    },
    'attribute_richness': {
        title: 'Attribute Richness',
        description: 'Depth and quantity of product attributes and specifications',
        importance: 'Rich attributes help AI match products to user needs',
        range: '0-100 points',
        good: '70+ (Many detailed attributes)',
        bad: '0-20 (Minimal info)'
    },
    'image_quality': {
        title: 'Image Quality Score',
        description: 'Checks for image availability, alt text, and metadata',
        importance: 'AI needs image context to recommend visual products',
        range: '0-100 points',
        good: '80+ (Multiple images with alt text)',
        bad: '0-20 (No images or missing alt)'
    },
    'cta_score': {
        title: 'Call-to-Action Score',
        description: 'Detection of clear buy/purchase buttons',
        importance: 'AI needs to identify how users can purchase',
        range: '0-100 points',
        good: '100 (Clear buy button)',
        bad: '0 (No CTA found)'
    },
    'trust_score': {
        title: 'Trust Signals',
        description: 'SSL, reviews, ratings, and security indicators',
        importance: 'AI considers trustworthiness when recommending',
        range: '0-100 points',
        good: '80+ (SSL + reviews + policies)',
        bad: '0-30 (Minimal trust signals)'
    },
    'contact_score': {
        title: 'Contact Information',
        description: 'Availability of email, phone, or contact forms',
        importance: 'AI looks for ways users can get support',
        range: '0-100 points',
        good: '100 (Multiple contact methods)',
        bad: '0 (No contact info)'
    },
    'buy_button_found': {
        title: 'Buy Button Detection',
        description: 'Boolean check if a purchase button was found',
        importance: 'Critical for AI to recognize transactional capability',
        range: 'true/false',
        good: 'true (CTA present)',
        bad: 'false (No buy button)'
    },
    'has_ssl': {
        title: 'SSL Certificate',
        description: 'Checks if site uses HTTPS',
        importance: 'AI prioritizes secure sites for recommendations',
        range: 'true/false',
        good: 'true (HTTPS)',
        bad: 'false (HTTP only)'
    },
    'has_reviews': {
        title: 'Reviews Present',
        description: 'Checks for customer reviews or ratings',
        importance: 'Reviews provide social proof for AI recommendations',
        range: 'true/false',
        good: 'true (Has reviews)',
        bad: 'false (No reviews)'
    },
    'has_offer': {
        title: 'Offer Schema Present',
        description: 'Checks if product has structured pricing data',
        importance: 'Helps AI understand product pricing and availability',
        range: 'true/false',
        good: 'true (Has offer data)',
        bad: 'false (No pricing schema)'
    },
    'payment_score': {
        title: 'Payment Method Visibility',
        description: 'Detection of payment options and checkout information',
        importance: 'AI needs to identify how users can complete purchases',
        range: '0-100 points',
        good: '80+ (Clear payment options)',
        bad: '0-20 (No payment info visible)'
    }
};

// Gap examples by type
const GAP_EXAMPLES = {
    'no_buy_button': {
        example: '<button class="add-to-cart" data-product-id="123">Add to Cart - $49.99</button>',
        explanation: 'AI looks for clear buttons with "buy", "add to cart", or "purchase" text'
    },
    'missing_h1': {
        example: '<h1>Premium Running Shoes for Marathon Training</h1>',
        explanation: 'H1 should clearly describe the page content for AI to understand context'
    },
    'missing_offer_schema': {
        example: `{
  "@type": "Offer",
  "price": "49.99",
  "priceCurrency": "USD",
  "availability": "https://schema.org/InStock"
}`,
        explanation: 'Offer schema helps AI understand pricing and availability'
    },
    'low_semantic_html': {
        example: '<article><header><h1>...</h1></header><section>...</section></article>',
        explanation: 'Use semantic tags (article, section, nav) instead of generic divs'
    },
    'missing_meta_description': {
        example: '<meta name="description" content="Premium running shoes with advanced cushioning...">',
        explanation: 'Meta descriptions help AI summarize your page content'
    }
};

// Score interpretations
function getScoreInterpretation(score) {
    if (score >= 80) return 'Excellent! Your site is highly optimized for AI recommendations.';
    if (score >= 60) return 'Good! Your site has solid AI readability with room for improvement.';
    if (score >= 40) return 'Fair. Significant improvements needed for AI citations.';
    if (score >= 20) return 'Poor. Your site may struggle to get AI recommendations.';
    return 'Critical. Major changes needed for AI to understand and recommend your content.';
}

function getGradeClass(grade) {
    return `grade-${grade}`;
}

function createTooltip(metricKey, metricLabel) {
    const info = METRIC_EXPLANATIONS[metricKey];
    if (!info) return metricLabel;

    return `
        <span class="metric-tooltip">
            ${metricLabel}
            <span class="tooltip-content">
                <div class="tooltip-title">${info.title}</div>
                <div class="tooltip-section">
                    <div class="tooltip-label">Description:</div>
                    <div class="tooltip-value">${info.description}</div>
                </div>
                <div class="tooltip-section">
                    <div class="tooltip-label">Why it matters:</div>
                    <div class="tooltip-value">${info.importance}</div>
                </div>
                <div class="tooltip-section">
                    <div class="tooltip-label">Range:</div>
                    <div class="tooltip-value">${info.range}</div>
                </div>
                <div class="tooltip-section">
                    <span class="tooltip-good">Good: ${info.good}</span><br>
                    <span class="tooltip-bad">Poor: ${info.bad}</span>
                </div>
            </span>
        </span>
    `;
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = document.getElementById('url').value;
    const brand = document.getElementById('brand').value;
    const category = document.getElementById('category').value;
    const useCase = document.getElementById('useCase').value;

    form.style.display = 'none';
    loading.style.display = 'block';
    results.style.display = 'none';
    error.style.display = 'none';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url,
                brand: brand || null,
                category: category || null,
                use_case: useCase || null
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }

        const data = await response.json();
        currentAnalysisId = data.analysis_id;

        const reportResponse = await fetch(`/api/report/${currentAnalysisId}`);
        const report = await reportResponse.json();

        displayResults(report);

    } catch (err) {
        error.textContent = 'Error: ' + err.message;
        error.style.display = 'block';
        form.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
});

function createScoreChart(score) {
    const canvas = document.getElementById('scoreChart');
    const ctx = canvas.getContext('2d');

    if (scoreChart) {
        scoreChart.destroy();
    }

    scoreChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [
                    score >= 60 ? '#4caf50' : score >= 40 ? '#ffc107' : '#f44336',
                    '#e0e0e0'
                ],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

function displayResults(report) {
    const score = report.composite_score || 0;
    const grade = report.grade || 'F';

    // Main score
    document.getElementById('compositeScore').textContent = score.toFixed(1);
    document.getElementById('gradeBadge').textContent = `Grade ${grade}`;
    document.getElementById('gradeBadge').className = `grade-badge ${getGradeClass(grade)}`;
    document.getElementById('scoreInterpretation').textContent = getScoreInterpretation(score);

    createScoreChart(score);

    // Engine scores
    const engineScoresDiv = document.getElementById('engineScores');
    engineScoresDiv.innerHTML = '';

    for (const [engine, data] of Object.entries(report.engine_scores || {})) {
        const engineInfo = ENGINE_INFO[engine] || {};
        const engineDiv = document.createElement('div');
        engineDiv.className = 'engine-item';

        let metricsHTML = '';
        if (data.details) {
            metricsHTML = '<div class="metric-details">';
            for (const [key, value] of Object.entries(data.details)) {
                const metricLabel = engineInfo.metrics?.[key] || key.replace(/_/g, ' ');
                const displayValue = typeof value === 'number' ? value.toFixed(1) : value.toString();
                const tooltipLabel = createTooltip(key, metricLabel);
                metricsHTML += `
                    <div class="metric-row">
                        <span class="metric-label">${tooltipLabel}:</span>
                        <span class="metric-value">${displayValue}</span>
                    </div>
                `;
            }
            metricsHTML += '</div>';
        }

        engineDiv.innerHTML = `
            <div class="engine-header">
                <div>
                    <div class="engine-name">${engineInfo.name || engine}</div>
                    <div class="engine-description">${engineInfo.description || ''}</div>
                </div>
                <div class="engine-score">${data.score.toFixed(1)}</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${data.score}%"></div>
            </div>
            <div style="font-size: 0.85em; color: #999; margin-top: 5px;">
                Weight: ${(data.weight * 100).toFixed(0)}% | Grade: ${data.grade}
            </div>
            ${metricsHTML}
        `;
        engineScoresDiv.appendChild(engineDiv);
    }

    // Simulation result
    const simDiv = document.getElementById('simulationResult');
    if (report.simulation_results) {
        const cited = report.simulation_results.brand_cited;
        const citationCount = report.simulation_results.citation_count || 0;

        simDiv.innerHTML = `
            <div class="simulation-card ${cited ? 'cited' : 'not-cited'}">
                <div class="simulation-header">AI Simulation Result</div>
                <div class="simulation-result">
                    <strong>${cited ? 'Success' : 'Not Recommended'}</strong> -
                    ${cited ? `Your brand was cited ${citationCount} time(s) by OpenAI GPT-4` : 'Your brand was not mentioned in AI recommendations'}
                </div>
                <div style="margin-top: 15px; font-size: 0.9em;">
                    ${cited
                        ? 'Excellent! Your content is structured well enough for AI to recommend your brand.'
                        : 'AI could not confidently recommend your brand. Check the gaps below for improvements.'
                    }
                </div>
            </div>
        `;
    } else {
        simDiv.innerHTML = '';
    }

    // Gaps
    const gapsList = document.getElementById('gapsList');
    gapsList.innerHTML = '';

    const gaps = report.gaps || [];
    if (gaps.length === 0) {
        gapsList.innerHTML = '<div style="text-align: center; padding: 40px; color: #4caf50; font-size: 1.2em;">No major issues found! Your site is well-optimized.</div>';
    } else {
        gaps.forEach((gap, index) => {
            const gapExample = GAP_EXAMPLES[gap.type] || {};
            const gapCard = document.createElement('div');
            gapCard.className = `gap-card ${gap.severity}`;

            gapCard.innerHTML = `
                <div class="gap-header">
                    <div class="gap-title">${index + 1}. ${gap.type.replace(/_/g, ' ').toUpperCase()}</div>
                    <span class="gap-severity severity-${gap.severity}">${gap.severity}</span>
                </div>
                <div class="gap-description">
                    <strong>Issue:</strong> ${gap.description}
                </div>
                <div class="gap-recommendation">
                    <div style="font-weight: 600; margin-bottom: 8px;">Recommendation:</div>
                    ${gap.recommendation}
                </div>
                ${gapExample.example ? `
                    <div class="gap-example">
                        <div style="font-weight: 600; margin-bottom: 8px;">Code Example:</div>
                        <code>${gapExample.example.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code>
                        ${gapExample.explanation ? `
                            <div style="margin-top: 10px; font-family: sans-serif; font-style: italic; color: #666;">
                                ${gapExample.explanation}
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
                <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                    Source: ${gap.engine_source}
                </div>
            `;
            gapsList.appendChild(gapCard);
        });
    }

    results.style.display = 'block';
    results.scrollIntoView({ behavior: 'smooth' });
}

document.getElementById('downloadBtn').addEventListener('click', async () => {
    if (!currentAnalysisId) return;

    const response = await fetch(`/api/report/${currentAnalysisId}`);
    const report = await response.json();

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `arrs-report-${currentAnalysisId}.json`;
    a.click();
});
