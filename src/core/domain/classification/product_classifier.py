"""Product type classification"""

import re


# Classification rules: category -> keywords
CLASSIFICATION_RULES = {
    'tablets_and_capsules': ['tab', 'tablet', 'قرص', 'tablets', 'cap', 'capsule', 'كبسولة', 'capsules'],
    'injections': ['injection', 'inject', 'حقن', 'ampoule', 'vial', 'قارورة'],
    'syrups': ['syrup', 'شراب', 'susp', 'suspension', 'معلق'],
    'creams': ['cream', 'ointment', 'oint', 'gel', 'كريم', 'مرهم'],
    'sachets': ['sachet', 'sachets', 'sach', 'كيس', 'أكياس'],
}


def _match_keywords(product_lower: str, keywords: list) -> bool:
    """Check if product name matches any keyword."""
    return any(keyword in product_lower for keyword in keywords)


def classify_product_type(product_name: str) -> str:
    """Classify product type based on product name."""
    if not product_name:
        return 'other'
    
    product_lower = product_name.lower()
    
    # Check for shampoo first to avoid false match with "amp"
    if 'shampoo' in product_lower or 'شامبو' in product_lower:
        return 'other'
    
    # Check for "amp" as standalone word
    if re.search(r'\bamp\b', product_lower):
        return 'injections'
    
    # Check classification rules
    for category, keywords in CLASSIFICATION_RULES.items():
        if _match_keywords(product_lower, keywords):
            return category
    
    return 'other'


def get_product_categories() -> list:
    """
    Get list of all product categories
    
    Returns:
        List of category names
    """
    return ['tablets_and_capsules', 'injections', 'syrups', 'creams', 'sachets', 'other']
