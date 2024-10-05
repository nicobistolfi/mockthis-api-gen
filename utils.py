import re

def to_snake_case(string):
    # Step 1: Replace any non-alphanumeric characters with underscores
    s1 = re.sub(r'[^a-zA-Z0-9]', '_', string)
    
    # Step 2: Convert camelCase to snake_case
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    
    # Step 3: Convert any remaining uppercase characters to lowercase
    s3 = s2.lower()
    
    # Step 4: Replace multiple consecutive underscores with a single underscore
    s4 = re.sub(r'_+', '_', s3)
    
    # Step 5: Remove leading and trailing underscores
    return s4.strip('_')