"""Constants for combiners."""

# Product types for categorization
PRODUCT_TYPES = [
    'tablets_and_capsules', 
    'injections', 
    'syrups', 
    'creams', 
    'sachets', 
    'other'
]

# Classification keywords for product type detection
PRODUCT_TYPE_KEYWORDS = {
    'tablets_and_capsules': (['قرص', 'كبسول', 'tab', 'cap'], ['tab', 'cap', 'قرص', 'كبسول']),
    'injections': (['أمبول', 'حقن', 'amp', 'inj', 'vial'], ['amp', 'inj', 'vial', 'أمبول']),
    'syrups': (['شراب', 'syrup', 'زجاجة'], ['syrup', 'شراب', 'susp']),
    'creams': (['كريم', 'cream', 'مرهم', 'oint'], ['cream', 'oint', 'gel', 'كريم']),
    'sachets': (['كيس', 'sachet', 'ظرف'], ['sachet', 'كيس']),
}
