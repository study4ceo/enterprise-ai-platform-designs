import re
import string
import logging

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison
    - Lowercase
    - Remove punctuation
    - Remove extra whitespace
    - Remove articles (a, an, the)
    """
    # Lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove articles
    text = re.sub(r'\b(a|an|the)\b', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


async def calculate_exact_match(candidate: str, reference: str = None, **kwargs) -> float:
    """
    Calculate Exact Match score
    
    Returns 1.0 if normalized strings match exactly, 0.0 otherwise.
    Commonly used for QA tasks where answer must be precise.
    
    Args:
        candidate: Generated text
        reference: Reference text
        **kwargs: Additional arguments (strict: bool - if True, no normalization)
    
    Returns:
        1.0 if exact match, 0.0 otherwise
    """
    if not reference:
        return 0.0
    
    if not candidate.strip():
        return 0.0
    
    try:
        strict = kwargs.get('strict', False)
        
        if strict:
            # Strict matching - no normalization
            return 1.0 if candidate == reference else 0.0
        
        # Normalized matching
        candidate_norm = normalize_text(candidate)
        reference_norm = normalize_text(reference)
        
        return 1.0 if candidate_norm == reference_norm else 0.0
    
    except Exception as e:
        logger.error(f"Error calculating exact match: {e}")
        return 0.0


async def calculate_f1_token(candidate: str, reference: str = None) -> float:
    """
    Calculate token-level F1 score
    
    Often used alongside exact match for QA evaluation.
    Measures overlap of tokens between candidate and reference.
    
    Returns:
        F1 score (0-1)
    """
    if not reference:
        return 0.0
    
    if not candidate.strip():
        return 0.0
    
    try:
        # Normalize and tokenize
        candidate_tokens = set(normalize_text(candidate).split())
        reference_tokens = set(normalize_text(reference).split())
        
        if len(candidate_tokens) == 0 or len(reference_tokens) == 0:
            return 0.0
        
        # Calculate overlap
        common = candidate_tokens & reference_tokens
        
        if len(common) == 0:
            return 0.0
        
        # Calculate precision and recall
        precision = len(common) / len(candidate_tokens)
        recall = len(common) / len(reference_tokens)
        
        # Calculate F1
        f1 = 2 * (precision * recall) / (precision + recall)
        
        return float(f1)
    
    except Exception as e:
        logger.error(f"Error calculating F1 token: {e}")
        return 0.0


async def calculate_substring_match(candidate: str, reference: str = None) -> float:
    """
    Calculate if reference is a substring of candidate (or vice versa)
    
    Useful for checking if key information is present.
    
    Returns:
        1.0 if either is substring of other, 0.0 otherwise
    """
    if not reference or not candidate:
        return 0.0
    
    try:
        candidate_norm = normalize_text(candidate)
        reference_norm = normalize_text(reference)
        
        if reference_norm in candidate_norm or candidate_norm in reference_norm:
            return 1.0
        
        return 0.0
    
    except Exception as e:
        logger.error(f"Error calculating substring match: {e}")
        return 0.0
