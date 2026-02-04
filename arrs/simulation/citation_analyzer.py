"""Analyze Claude responses for brand citations."""
import re
from typing import Dict, List, Any


class CitationAnalyzer:
    """Analyze AI responses for brand mentions and citations."""

    def analyze_citation(self, response: str, brand: str) -> Dict[str, Any]:
        """
        Analyze response for brand citations.

        Args:
            response: Claude's response text
            brand: Brand name to search for

        Returns:
            Citation analysis
        """
        # Case-insensitive search
        brand_lower = brand.lower()
        response_lower = response.lower()

        # Count mentions
        citation_count = response_lower.count(brand_lower)
        cited = citation_count > 0

        # Extract contexts where brand is mentioned
        contexts = self._extract_contexts(response, brand) if cited else []

        # Determine sentiment of mentions
        sentiment = self._analyze_sentiment(contexts) if contexts else "neutral"

        return {
            "cited": cited,
            "count": citation_count,
            "contexts": contexts,
            "sentiment": sentiment
        }

    def _extract_contexts(self, response: str, brand: str, context_window: int = 100) -> List[str]:
        """
        Extract surrounding context for each brand mention.

        Args:
            response: Response text
            brand: Brand name
            context_window: Characters before/after mention

        Returns:
            List of context snippets
        """
        contexts = []

        # Find all positions where brand is mentioned (case-insensitive)
        pattern = re.compile(re.escape(brand), re.IGNORECASE)

        for match in pattern.finditer(response):
            start = max(0, match.start() - context_window)
            end = min(len(response), match.end() + context_window)

            context = response[start:end]
            contexts.append(context.strip())

        return contexts

    def _analyze_sentiment(self, contexts: List[str]) -> str:
        """
        Analyze sentiment of brand mentions.

        Args:
            contexts: Context snippets

        Returns:
            Overall sentiment: positive, negative, or neutral
        """
        positive_keywords = [
            "recommend", "best", "excellent", "great", "top", "leading",
            "popular", "trusted", "reliable", "quality", "premium"
        ]

        negative_keywords = [
            "not recommend", "avoid", "poor", "lacking", "missing",
            "insufficient", "weak", "limited", "concerns"
        ]

        positive_score = 0
        negative_score = 0

        for context in contexts:
            context_lower = context.lower()

            for keyword in positive_keywords:
                if keyword in context_lower:
                    positive_score += 1

            for keyword in negative_keywords:
                if keyword in context_lower:
                    negative_score += 1

        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"

    def extract_important_attributes(self, attribute_response: str) -> List[str]:
        """
        Extract important attributes from Claude's attribute response.

        Args:
            attribute_response: Response about important attributes

        Returns:
            List of attribute categories
        """
        attributes = []

        # Common attribute patterns
        attribute_patterns = [
            # Numbered lists
            r'\d+\.\s*([^\n:]+)',
            # Bullet points
            r'[-•]\s*([^\n:]+)',
            # Bold or emphasized
            r'\*\*([^\*]+)\*\*'
        ]

        for pattern in attribute_patterns:
            matches = re.findall(pattern, attribute_response)
            attributes.extend([m.strip() for m in matches])

        # Deduplicate and clean
        attributes = list(set(attributes))

        # Filter out very short matches
        attributes = [attr for attr in attributes if len(attr) > 10]

        return attributes[:10]  # Return top 10

    def identify_gaps_from_response(
        self,
        recommendation_response: str,
        brand: str
    ) -> List[Dict[str, str]]:
        """
        Identify what Claude mentioned as important that might be missing.

        Args:
            recommendation_response: Claude's recommendation
            brand: Brand name

        Returns:
            List of potential gaps
        """
        gaps = []

        # Keywords that indicate missing information
        gap_indicators = {
            "price": ["pricing", "cost", "price point", "how much"],
            "availability": ["available", "in stock", "where to buy"],
            "reviews": ["reviews", "ratings", "customer feedback"],
            "specifications": ["specs", "technical details", "dimensions"],
            "warranty": ["warranty", "guarantee"],
            "shipping": ["shipping", "delivery"],
            "certifications": ["certified", "certification", "standards"]
        }

        response_lower = recommendation_response.lower()

        for gap_type, keywords in gap_indicators.items():
            if any(keyword in response_lower for keyword in keywords):
                # Check if it's mentioned as missing or uncertain
                uncertainty_words = ["unclear", "unknown", "not sure", "don't know", "missing"]

                # Look for these patterns near the keywords
                for keyword in keywords:
                    if keyword in response_lower:
                        # Get context around keyword
                        idx = response_lower.find(keyword)
                        context = response_lower[max(0, idx-50):min(len(response_lower), idx+50)]

                        if any(unc in context for unc in uncertainty_words):
                            gaps.append({
                                "type": gap_type,
                                "keyword": keyword,
                                "context": context.strip()
                            })
                            break

        return gaps
