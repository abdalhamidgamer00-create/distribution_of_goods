"""Product type classification"""

import re


def classify_product_type(product_name: str) -> str:
    """
    Classify product type based on product name
    
    Args:
        product_name: Product name string
        
    Returns:
        Product type category: 'tablets_and_capsules', 'injections', 'syrups', 'creams', 'sachets', 'other'
    """
    if not product_name:
        return 'other'
    
    product_lower = product_name.lower()
    
    # Tablets and capsules are combined into one category
    if any(keyword in product_lower for keyword in ['tab', 'tablet', 'قرص', 'tablets']):
        return 'tablets_and_capsules'
    
    if any(keyword in product_lower for keyword in ['cap', 'capsule', 'كبسولة', 'capsules']):
        return 'tablets_and_capsules'
    
    # Check for shampoo first to avoid false match with "amp" in injections
    if 'shampoo' in product_lower or 'شامبو' in product_lower:
        return 'other'
    
    # Check for "amp" as a standalone word or in context (not in shampoo)
    # Match "amp" at word boundaries (start, end, or surrounded by spaces/hyphens)
    if re.search(r'\bamp\b', product_lower):
        return 'injections'
    
    if any(keyword in product_lower for keyword in ['injection', 'inject', 'حقن', 'ampoule', 'vial', 'قارورة']):
        return 'injections'
    
    if any(keyword in product_lower for keyword in ['syrup', 'شراب', 'susp', 'suspension', 'معلق']):
        return 'syrups'
    
    if any(keyword in product_lower for keyword in ['cream', 'ointment', 'oint', 'gel', 'كريم', 'مرهم']):
        return 'creams'
    
    if any(keyword in product_lower for keyword in ['sachet', 'sachets', 'sach', 'كيس', 'أكياس']):
        return 'sachets'
    
    return 'other'


def get_product_categories() -> list:
    """
    Get list of all product categories
    
    Returns:
        List of category names
    """
    return ['tablets_and_capsules', 'injections', 'syrups', 'creams', 'sachets', 'other']
