from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


async def calculate_bleu(candidate: str, reference: str = None, **kwargs) -> float:
    """
    Calculate BLEU score
    
    Args:
        candidate: Generated text
        reference: Reference text
    
    Returns:
        BLEU score (0-1)
    """
    if not reference:
        return 0.0
    
    # Tokenize
    reference_tokens = nltk.word_tokenize(reference.lower())
    candidate_tokens = nltk.word_tokenize(candidate.lower())
    
    # Calculate BLEU with smoothing
    smoothing = SmoothingFunction().method1
    
    try:
        score = sentence_bleu(
            [reference_tokens],
            candidate_tokens,
            smoothing_function=smoothing
        )
        return float(score)
    except:
        return 0.0
