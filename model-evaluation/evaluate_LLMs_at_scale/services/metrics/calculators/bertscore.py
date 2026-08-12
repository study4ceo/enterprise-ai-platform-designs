from bert_score import score as bert_score
import logging

logger = logging.getLogger(__name__)


async def calculate_bertscore(candidate: str, reference: str = None, **kwargs) -> float:
    """
    Calculate BERTScore using contextual embeddings
    
    BERTScore measures semantic similarity using BERT embeddings.
    More accurate than lexical metrics like BLEU/ROUGE.
    
    Args:
        candidate: Generated text
        reference: Reference text
        **kwargs: Additional arguments (model: 'bert-base-uncased', lang: 'en')
    
    Returns:
        BERTScore F1 (0-1)
    """
    if not reference:
        return 0.0
    
    if not candidate.strip():
        return 0.0
    
    try:
        # Get model and language
        model_type = kwargs.get('model', 'bert-base-uncased')
        lang = kwargs.get('lang', 'en')
        
        # Calculate BERTScore
        # Returns (precision, recall, f1) tensors
        P, R, F1 = bert_score(
            [candidate],
            [reference],
            model_type=model_type,
            lang=lang,
            verbose=False,
            device='cpu'  # Use CPU for compatibility
        )
        
        # Return F1 score
        return float(F1.item())
    
    except Exception as e:
        logger.error(f"Error calculating BERTScore: {e}")
        return 0.0


async def calculate_bertscore_detailed(candidate: str, reference: str = None, **kwargs) -> dict:
    """
    Calculate detailed BERTScore with precision, recall, F1
    
    Returns:
        Dict with precision, recall, F1
    """
    if not reference:
        return {
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0
        }
    
    try:
        model_type = kwargs.get('model', 'bert-base-uncased')
        lang = kwargs.get('lang', 'en')
        
        P, R, F1 = bert_score(
            [candidate],
            [reference],
            model_type=model_type,
            lang=lang,
            verbose=False,
            device='cpu'
        )
        
        return {
            'precision': float(P.item()),
            'recall': float(R.item()),
            'f1': float(F1.item())
        }
    
    except Exception as e:
        logger.error(f"Error calculating detailed BERTScore: {e}")
        return {
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0
        }
