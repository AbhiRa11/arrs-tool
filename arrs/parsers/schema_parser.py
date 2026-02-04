"""Schema.org and structured data extraction."""
import json
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import extruct
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class SchemaParser:
    """Extract structured data from HTML."""

    def __init__(self, html: str, base_url: str):
        """
        Initialize parser.

        Args:
            html: Raw HTML content
            base_url: Base URL
        """
        self.html = html
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'lxml')

    def extract_all_schemas(self) -> Dict[str, Any]:
        """
        Extract all structured data formats.

        Returns:
            Dictionary of extracted data
        """
        try:
            # Use extruct to extract all formats
            data = extruct.extract(
                self.html,
                base_url=self.base_url,
                syntaxes=['json-ld', 'microdata', 'opengraph', 'rdfa']
            )

            return {
                "json_ld": data.get('json-ld', []),
                "microdata": data.get('microdata', []),
                "opengraph": data.get('opengraph', []),
                "rdfa": data.get('rdfa', [])
            }
        except Exception as e:
            logger.warning(f"Schema extraction failed: {e}")
            return {
                "json_ld": [],
                "microdata": [],
                "opengraph": [],
                "rdfa": []
            }

    def find_product_schema(self) -> Optional[Dict[str, Any]]:
        """
        Find Product schema specifically.

        Returns:
            Product schema data or None
        """
        schemas = self.extract_all_schemas()

        # Check JSON-LD
        for item in schemas.get('json_ld', []):
            if self._is_product_schema(item):
                return item

        # Check microdata
        for item in schemas.get('microdata', []):
            if item.get('type') == 'http://schema.org/Product':
                return item

        return None

    def find_organization_schema(self) -> Optional[Dict[str, Any]]:
        """
        Find Organization schema.

        Returns:
            Organization schema data or None
        """
        schemas = self.extract_all_schemas()

        # Check JSON-LD
        for item in schemas.get('json_ld', []):
            if self._is_organization_schema(item):
                return item

        # Check microdata
        for item in schemas.get('microdata', []):
            if item.get('type') == 'http://schema.org/Organization':
                return item

        return None

    def _is_product_schema(self, schema: Dict[str, Any]) -> bool:
        """Check if schema is a Product type."""
        schema_type = schema.get('@type', '')
        if isinstance(schema_type, list):
            return 'Product' in schema_type
        return schema_type == 'Product'

    def _is_organization_schema(self, schema: Dict[str, Any]) -> bool:
        """Check if schema is an Organization type."""
        schema_type = schema.get('@type', '')
        if isinstance(schema_type, list):
            return 'Organization' in schema_type
        return schema_type == 'Organization'

    def validate_product_schema(self, product_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate Product schema completeness.

        Args:
            product_schema: Product schema to validate (or will find it)

        Returns:
            Validation results
        """
        if product_schema is None:
            product_schema = self.find_product_schema()

        if not product_schema:
            return {
                "present": False,
                "completeness": 0.0,
                "missing_fields": [
                    "name", "image", "description", "brand", "offers",
                    "sku", "gtin", "mpn", "aggregateRating", "review"
                ]
            }

        # Required fields for good Product schema
        recommended_fields = [
            "name", "image", "description", "brand", "offers",
            "sku", "gtin", "mpn", "aggregateRating", "review"
        ]

        present_fields = []
        missing_fields = []

        for field in recommended_fields:
            if field in product_schema and product_schema[field]:
                present_fields.append(field)
            else:
                missing_fields.append(field)

        completeness = len(present_fields) / len(recommended_fields)

        return {
            "present": True,
            "completeness": completeness,
            "present_fields": present_fields,
            "missing_fields": missing_fields,
            "field_count": len(present_fields)
        }

    def extract_offers(self) -> List[Dict[str, Any]]:
        """
        Extract product offers/pricing.

        Returns:
            List of offers
        """
        product_schema = self.find_product_schema()
        if not product_schema:
            return []

        offers = product_schema.get('offers', [])
        if isinstance(offers, dict):
            offers = [offers]

        return offers

    def extract_reviews(self) -> Dict[str, Any]:
        """
        Extract review and rating information.

        Returns:
            Review data
        """
        product_schema = self.find_product_schema()
        if not product_schema:
            return {
                "has_reviews": False,
                "aggregate_rating": None,
                "review_count": 0
            }

        aggregate_rating = product_schema.get('aggregateRating', {})
        reviews = product_schema.get('review', [])

        if isinstance(reviews, dict):
            reviews = [reviews]

        return {
            "has_reviews": bool(aggregate_rating or reviews),
            "aggregate_rating": aggregate_rating,
            "review_count": len(reviews),
            "rating_value": aggregate_rating.get('ratingValue') if aggregate_rating else None,
            "rating_count": aggregate_rating.get('ratingCount') if aggregate_rating else None
        }

    def extract_brand_info(self) -> Optional[str]:
        """
        Extract brand name.

        Returns:
            Brand name or None
        """
        # Try Product schema first
        product_schema = self.find_product_schema()
        if product_schema and 'brand' in product_schema:
            brand = product_schema['brand']
            if isinstance(brand, dict):
                return brand.get('name')
            return str(brand)

        # Try Organization schema
        org_schema = self.find_organization_schema()
        if org_schema and 'name' in org_schema:
            return org_schema['name']

        return None
