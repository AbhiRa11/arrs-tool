"""Transaction Readiness Engine (TRE) - 20% weight.

Validates whether AI can confidently recommend a purchase.
"""
from typing import Dict, List, Any
import re
from arrs.engines.base.engine import BaseEngine
from arrs.models.score_result import EngineScore, Gap
from arrs.models.crawled_content import CrawledContent
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class TREEngine(BaseEngine):
    """Transaction Readiness Engine."""

    async def analyze(self, content: CrawledContent, parsed_data: Dict[str, Any]) -> EngineScore:
        """
        Analyze transaction readiness.

        Scoring breakdown:
        - Buy button/CTA presence: 30 points
        - Trust signals (SSL, reviews, policy): 30 points
        - Contact information: 20 points
        - Payment/shipping info visibility: 20 points
        Total: 100 points

        Args:
            content: Crawled content
            parsed_data: Parsed data

        Returns:
            Engine score
        """
        logger.info(f"Running TRE analysis", extra={"analysis_id": content.analysis_id})

        html_data = parsed_data.get('html', {})
        schema_data = parsed_data.get('schema', {})

        # 1. CTA presence (30 points)
        cta_score = self._score_cta_presence(html_data, schema_data)

        # 2. Trust signals (30 points)
        trust_score = self._score_trust_signals(html_data, schema_data, content.url)

        # 3. Contact information (20 points)
        contact_score = self._score_contact_info(html_data, schema_data)

        # 4. Payment/shipping info (20 points)
        payment_score = self._score_payment_shipping_info(html_data, schema_data)

        # Calculate total score
        total_score = cta_score + trust_score + contact_score + payment_score

        details = {
            "cta_score": cta_score,
            "trust_score": trust_score,
            "contact_score": contact_score,
            "payment_score": payment_score,
            "buy_button_found": self._detect_buy_button(html_data),
            "has_ssl": content.url.startswith('https://'),
            "has_reviews": schema_data.get('reviews', {}).get('has_reviews', False),
            "has_offer": bool(schema_data.get('offers'))
        }

        logger.info(f"TRE analysis complete", extra={
            "analysis_id": content.analysis_id,
            "score": total_score
        })

        return self.create_score(content.analysis_id, total_score, details)

    def _score_cta_presence(self, html_data: Dict[str, Any], schema_data: Dict[str, Any]) -> float:
        """Score CTA/buy button presence (30 points max)."""
        score = 0.0

        # Check for buy button in text
        if self._detect_buy_button(html_data):
            score += 15.0

        # Check for Offer in schema
        offers = schema_data.get('offers', [])
        if offers:
            score += 15.0
            # Bonus for complete offer
            offer = offers[0] if isinstance(offers, list) else offers
            if offer.get('price') and offer.get('priceCurrency'):
                score += 5.0  # Cap at 30 if we go over

        return min(30.0, score)

    def _detect_buy_button(self, html_data: Dict[str, Any]) -> bool:
        """Detect buy button or add to cart."""
        text = html_data.get('text_content', '').lower()

        buy_keywords = [
            'add to cart', 'add to bag', 'buy now', 'purchase',
            'checkout', 'order now', 'add to basket', 'buy'
        ]

        return any(keyword in text for keyword in buy_keywords)

    def _score_trust_signals(self, html_data: Dict[str, Any], schema_data: Dict[str, Any], url: str) -> float:
        """Score trust signals (30 points max)."""
        score = 0.0

        # SSL (10 points)
        if url.startswith('https://'):
            score += 10.0

        # Reviews/ratings (10 points)
        reviews = schema_data.get('reviews', {})
        if reviews.get('has_reviews'):
            score += 10.0

        # Return policy (10 points)
        text = html_data.get('text_content', '').lower()
        policy_keywords = ['return policy', 'returns', 'refund', 'money back', 'guarantee']
        if any(keyword in text for keyword in policy_keywords):
            score += 10.0

        return score

    def _score_contact_info(self, html_data: Dict[str, Any], schema_data: Dict[str, Any]) -> float:
        """Score contact information (20 points max)."""
        text = html_data.get('text_content', '').lower()
        score = 0.0

        # Email (7 points)
        if self._detect_email(text):
            score += 7.0

        # Phone (7 points)
        if self._detect_phone(text):
            score += 7.0

        # Physical address or contact page (6 points)
        address_keywords = ['address', 'contact us', 'location', 'visit us']
        if any(keyword in text for keyword in address_keywords):
            score += 6.0

        return score

    def _detect_email(self, text: str) -> bool:
        """Detect email address."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return bool(re.search(email_pattern, text))

    def _detect_phone(self, text: str) -> bool:
        """Detect phone number."""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',     # (123) 456-7890
            r'\+\d{1,3}\s*\d{1,14}'             # International
        ]
        return any(re.search(pattern, text) for pattern in phone_patterns)

    def _score_payment_shipping_info(self, html_data: Dict[str, Any], schema_data: Dict[str, Any]) -> float:
        """Score payment and shipping information (20 points max)."""
        text = html_data.get('text_content', '').lower()
        score = 0.0

        # Payment methods mentioned (10 points)
        payment_keywords = [
            'visa', 'mastercard', 'paypal', 'payment', 'credit card',
            'debit card', 'apple pay', 'google pay'
        ]
        if any(keyword in text for keyword in payment_keywords):
            score += 10.0

        # Shipping info (10 points)
        shipping_keywords = [
            'shipping', 'delivery', 'free shipping', 'ships to',
            'ship', 'express delivery'
        ]
        if any(keyword in text for keyword in shipping_keywords):
            score += 10.0

        return score

    async def identify_gaps(self, score: EngineScore, parsed_data: Dict[str, Any]) -> List[Gap]:
        """Identify transaction readiness gaps."""
        gaps = []
        analysis_id = score.analysis_id

        html_data = parsed_data.get('html', {})
        schema_data = parsed_data.get('schema', {})

        # Check for buy button
        if not self._detect_buy_button(html_data):
            gaps.append(self.create_gap(
                analysis_id,
                "no_buy_button",
                "critical",
                "No clear call-to-action (buy button/add to cart) detected",
                "Add a prominent 'Add to Cart' or 'Buy Now' button for AI to recognize purchase capability"
            ))

        # Check for Offer schema
        if not schema_data.get('offers'):
            gaps.append(self.create_gap(
                analysis_id,
                "missing_offer_schema",
                "high",
                "Offer schema missing from Product markup",
                "Add Offer schema with price, currency, and availability information"
            ))

        # Check for reviews
        if not schema_data.get('reviews', {}).get('has_reviews'):
            gaps.append(self.create_gap(
                analysis_id,
                "no_reviews",
                "medium",
                "No review or rating information found",
                "Add AggregateRating or Review schema to build trust signals"
            ))

        # Check for SSL
        if not score.details.get('has_ssl'):
            gaps.append(self.create_gap(
                analysis_id,
                "no_ssl",
                "critical",
                "Site not using HTTPS (SSL)",
                "Enable HTTPS for secure transactions and improved trust"
            ))

        # Check for contact info
        text = html_data.get('text_content', '').lower()
        if not self._detect_email(text) and not self._detect_phone(text):
            gaps.append(self.create_gap(
                analysis_id,
                "no_contact_info",
                "high",
                "No contact information (email or phone) found",
                "Add visible contact information to build customer trust"
            ))

        return gaps
