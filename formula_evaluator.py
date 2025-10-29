"""
Formula evaluator for past client segments
Converts human-readable formulas to pandas queries
"""
import pandas as pd
import re

# Column name mapping from formula syntax to actual CSV columns
COLUMN_MAPPING = {
    'Age': 'AGE',
    'EmploymentStatus': 'EMPLOYMENT_STATUS',
    'YearsOwned': 'LENGTH_OF_RESIDENCE',
    'Equity': 'EQUITY',
    'Rate': 'CURRENT_SALE_MTG_1_INT_RATE',
    'Mortgage_Balance': 'CURRENT_SALE_MTG_1_LOAN_AMOUNT',
    'HomeSQFT': 'SUM_BUILDING_SQFT',
    'MedianSQFT': 'MEDIAN_SQFT',
    'LastSaleDate': 'SALE_YEAR',
    'IsOwner': 'IS_OWNER',
    'InterestRate': 'CURRENT_SALE_MTG_1_INT_RATE',
    'MedianHomePrice': 'MEDIAN_HOME_PRICE'
}

def parse_formula(formula_str):
    """
    Convert human-readable formula to pandas-compatible query
    
    Examples:
        "Age >= 60 and EmploymentStatus ≠ 'Retired'" 
        -> "AGE >= 60 and EMPLOYMENT_STATUS != 'Retired'"
        
        "Equity >= 200000 and Rate >= 0.065"
        -> "EQUITY >= 200000 and CURRENT_SALE_MTG_1_INT_RATE >= 0.065"
    
    Args:
        formula_str: Human-readable formula string
    
    Returns:
        str: Pandas query string
    """
    query = formula_str
    
    # Replace special characters
    query = query.replace('≠', '!=')
    query = query.replace('≥', '>=')
    query = query.replace('≤', '<=')
    
    # Handle BETWEEN syntax: "Age BETWEEN 30 AND 45" -> "(AGE >= 30) & (AGE <= 45)"
    between_pattern = r'(\w+)\s+BETWEEN\s+(\d+)\s+AND\s+(\d+)'
    def replace_between(match):
        col = match.group(1)
        min_val = match.group(2)
        max_val = match.group(3)
        mapped_col = COLUMN_MAPPING.get(col, col)
        return f"({mapped_col} >= {min_val}) & ({mapped_col} <= {max_val})"
    
    query = re.sub(between_pattern, replace_between, query, flags=re.IGNORECASE)
    
    # Replace column names with actual CSV column names
    for formula_name, csv_name in COLUMN_MAPPING.items():
        # Use word boundaries to avoid partial replacements
        query = re.sub(r'\b' + formula_name + r'\b', csv_name, query)
    
    # Replace logical operators
    query = query.replace(' and ', ' & ')
    query = query.replace(' AND ', ' & ')
    query = query.replace(' or ', ' | ')
    query = query.replace(' OR ', ' | ')
    
    return query

def evaluate_formula(df, formula_str):
    """
    Evaluate a formula against a dataframe and return matching count
    
    Args:
        df: Pandas DataFrame with client data
        formula_str: Human-readable formula string
    
    Returns:
        int: Count of rows matching the formula
    """
    try:
        # Parse formula to pandas query
        query = parse_formula(formula_str)
        
        # Evaluate query
        result = df.query(query)
        return len(result)
    
    except Exception as e:
        print(f"Error evaluating formula '{formula_str}': {str(e)}")
        print(f"Parsed query: {query}")
        return 0

def validate_formula(formula_str):
    """
    Validate a formula for syntax errors
    
    Args:
        formula_str: Formula string to validate
    
    Returns:
        dict: {'valid': bool, 'message': str, 'parsed': str}
    """
    try:
        # Try to parse the formula
        parsed = parse_formula(formula_str)
        
        # Check for common issues
        if not parsed.strip():
            return {
                'valid': False,
                'message': 'Formula cannot be empty',
                'parsed': ''
            }
        
        # Check for balanced parentheses
        if parsed.count('(') != parsed.count(')'):
            return {
                'valid': False,
                'message': 'Unbalanced parentheses',
                'parsed': parsed
            }
        
        return {
            'valid': True,
            'message': 'Formula is valid',
            'parsed': parsed
        }
    
    except Exception as e:
        return {
            'valid': False,
            'message': f'Syntax error: {str(e)}',
            'parsed': ''
        }

def get_available_fields():
    """
    Get list of available fields for formula building
    
    Returns:
        list: List of dicts with field info
    """
    return [
        {'name': 'Age', 'type': 'numeric', 'description': 'Client age'},
        {'name': 'YearsOwned', 'type': 'numeric', 'description': 'Years of ownership'},
        {'name': 'Equity', 'type': 'numeric', 'description': 'Home equity ($)'},
        {'name': 'Rate', 'type': 'numeric', 'description': 'Mortgage interest rate (decimal)'},
        {'name': 'Mortgage_Balance', 'type': 'numeric', 'description': 'Current mortgage balance ($)'},
        {'name': 'HomeSQFT', 'type': 'numeric', 'description': 'Home square footage'},
        {'name': 'MedianSQFT', 'type': 'numeric', 'description': 'ZIP median square footage'},
        {'name': 'MedianHomePrice', 'type': 'numeric', 'description': 'ZIP median home price ($)'},
        {'name': 'LastSaleDate', 'type': 'numeric', 'description': 'Year of last sale'},
        {'name': 'EmploymentStatus', 'type': 'text', 'description': 'Employment status'},
        {'name': 'IsOwner', 'type': 'boolean', 'description': 'Currently owns property'}
    ]

