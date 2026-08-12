from rouge_score import rouge_scorer
import logging

logger = logging.getLogger(__name__)


async def calculate_rouge(candidate: str, reference: str = None, **kwargs) -> float:
    """
    Calculate ROUGE score (average of ROUGE-1, ROUGE-2, ROUGE-L)
    
    ROUGE (Recall-Oriented Understudy for Gisting Evaluation) measures
    overlap between generated text and reference text.
    
    Args:
        candidate: Generated text
        reference: Reference text
        **kwargs: Additional arguments (rouge_type: 'rouge1', 'rouge2', 'rougeL')
    
    Returns:
        ROUGE F1 score (0-1)
    """
    if not reference:
        return 0.0
    
    if not candidate.strip():
        return 0.0
    
    try:
        # Initialize scorer with all ROUGE variants
        scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
        
        # Calculate scores
        scores = scorer.score(reference, candidate)
        
        # Get specific rouge type if requested
        rouge_type = kwargs.get('rouge_type', 'all')
        
        if rouge_type in ['rouge1', 'rouge2', 'rougeL']:
            # Return F1 for specific type
            return float(scores[rouge_type].fmeasure)
        
        # Return average F1 of all ROUGE variants
        avg_score = (
            scores['rouge1'].fmeasure +
            scores['rouge2'].fmeasure +
            scores['rougeL'].fmeasure
        ) / 3.0
        
        return float(avg_score)
    
    except Exception as e:
        logger.error(f"Error calculating ROUGE: {e}")
        return 0.0


async def calculate_rouge_detailed(candidate: str, reference: str = None) -> dict:
    """
    Calculate detailed ROUGE scores
    
    Returns:
        Dict with precision, recall, F1 for each ROUGE variant
    """
    if not reference:
        return {
            'rouge1': {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0},
            'rouge2': {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0},
            'rougeL': {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0}
        }
    
    try:
        scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
        
        scores = scorer.score(reference, candidate)
        
        return {
            'rouge1': {
                'precision': float(scores['rouge1'].precision),
                'recall': float(scores['rouge1'].recall),
                'fmeasure': float(scores['rouge1'].fmeasure)
            },
            'rouge2': {
                'precision': float(scores['rouge2'].precision),
                'recall': float(scores['rouge2'].recall),
                'fmeasure': float(scores['rouge2'].fmeasure)
            },
            'rougeL': {
                'precision': float(scores['rougeL'].precision),
                'recall': float(scores['rougeL'].recall),
                'fmeasure': float(scores['rougeL'].fmeasure)
            }
        }
    
    except Exception as e:
        logger.error(f"Error calculating detailed ROUGE: {e}")
        return {
            'rouge1': {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0},
            'rouge2': {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0},
            'rougeL': {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0}
        }
