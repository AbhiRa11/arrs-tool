"""Prompt templates for AI simulation."""
from typing import Dict


def get_recommendation_prompt(product_category: str, use_case: str) -> str:
    """
    Get recommendation prompt template.

    Args:
        product_category: Product category (e.g., "running shoes")
        use_case: Specific use case (e.g., "marathon training")

    Returns:
        Formatted prompt
    """
    return f"""You are helping a customer find the best {product_category} for {use_case}.

Based on your knowledge, recommend specific brands and products that would be best for this use case.
Explain why you're recommending them and what attributes make them suitable.

Use case: {use_case}
Product category: {product_category}

Please provide 3-5 specific recommendations with detailed reasoning about:
- Why each product is suitable for this use case
- Key features and attributes that matter
- Any important considerations

Be specific with brand names and product models when possible."""


def get_attribute_extraction_prompt(brand: str, product_category: str) -> str:
    """
    Get prompt for extracting what attributes AI values.

    Args:
        brand: Brand name
        product_category: Product category

    Returns:
        Formatted prompt
    """
    return f"""What are the most important attributes and information you would need to know about
{brand}'s {product_category} in order to confidently recommend them to customers?

Please list:
1. Essential product attributes (e.g., specifications, features)
2. Trust signals (e.g., reviews, certifications)
3. Purchase information (e.g., pricing, availability)
4. Any other information that would help you make a recommendation

Be specific and prioritize the attributes by importance."""


def get_competitive_analysis_prompt(product_category: str, use_case: str, target_brand: str) -> str:
    """
    Get prompt for competitive analysis.

    Args:
        product_category: Product category
        use_case: Use case
        target_brand: Target brand to analyze

    Returns:
        Formatted prompt
    """
    return f"""Compare and recommend {product_category} for {use_case}.

Please recommend the top 3-5 options, and specifically consider whether {target_brand}
should be included in your recommendations.

For each recommendation, explain:
- Why you're recommending it
- Key differentiators
- Who it's best for

If {target_brand} is NOT in your top recommendations, explain why and what would need
to improve for it to be recommended."""
