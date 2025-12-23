"""Product type classification"""

import re


# =============================================================================
# CONSTANTS
# =============================================================================

CLASSIFICATION_RULES = {
    'tablets_and_capsules': [
        'tab', 'tablet', 'قرص', 'tablets', 
        'cap', 'capsule', 'كبسولة', 'capsules'
    ],
    'injections': ['injection', 'inject', 'حقن', 'ampoule', 'vial', 'قارورة'],
    'syrups': ['syrup', 'شراب', 'susp', 'suspension', 'معلق'],
    'creams': ['cream', 'ointment', 'oint', 'gel', 'كريم', 'مرهم'],
    'sachets': ['sachet', 'sachets', 'sach', 'كيس', 'أكياس'],
}


# =============================================================================
# PUBLIC API
# =============================================================================

def classify_product_type(product_name: str) -> str:
    """Classify product type based on product name."""
    if not product_name:
        return 'other'
    
    product_lower = product_name.lower()
    special_case = _check_special_cases(product_lower)
    if special_case:
        return special_case
        
    return _find_matching_category(product_lower)


def get_product_categories() -> list:
    """Get list of all product categories."""
    return [
        'tablets_and_capsules', 
        'injections', 
        'syrups', 
        'creams', 
        'sachets', 
        'other'
    ]


# =============================================================================
# CLASSIFICATION HELPERS
# =============================================================================

def _match_keywords(product_lower: str, keywords: list) -> bool:
    """Check if product name matches any keyword."""
    return any(keyword in product_lower for keyword in keywords)


def _check_special_cases(product_lower: str) -> str:
    """Check for special case products, return category or None."""
    if 'shampoo' in product_lower or 'شامبو' in product_lower:
        return 'other'
    if re.search(r'\bamp\b', product_lower):
        return 'injections'
    return None


def _find_matching_category(product_lower: str) -> str:
    """Find matching category from classification rules."""
    for category, keywords in CLASSIFICATION_RULES.items():
        if _match_keywords(product_lower, keywords):
            return category
    return 'other'
