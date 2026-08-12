"""
Faithfulness Checker for RAG Evaluation

Checks if generated answers are grounded in the retrieved context.
Uses Groq LLM-as-Judge for fast and accurate verification.
"""

import os
import logging
from typing import List, Dict
from groq import Groq

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)
else:
    groq_client = None
    logger.warning("GROQ_API_KEY not set - faithfulness checking will use fallback")


async def check_faithfulness(answer: str, contexts: List[str]) -> float:
    """
    Check if answer claims are supported by retrieved contexts
    
    This is the MOST CRITICAL metric for RAG evaluation.
    Prevents hallucinations by verifying every claim.
    
    Args:
        answer: Generated answer to check
        contexts: List of retrieved document texts
    
    Returns:
        Faithfulness score (0=unfaithful, 1=fully faithful)
    """
    if not contexts or not answer.strip():
        return 0.0
    
    try:
        if groq_client:
            return await _check_faithfulness_llm(answer, contexts)
        else:
            return await _check_faithfulness_heuristic(answer, contexts)
    
    except Exception as e:
        logger.error(f"Error checking faithfulness: {e}")
        return 0.5


async def _check_faithfulness_llm(answer: str, contexts: List[str]) -> float:
    """LLM-based faithfulness checking (accurate)"""
    
    # Step 1: Extract claims from answer
    claims = await extract_claims(answer)
    
    if not claims:
        return 1.0  # No claims = nothing to verify = faithful
    
    # Step 2: Verify each claim against contexts
    supported_count = 0
    
    for claim in claims:
        is_supported = await verify_claim(claim, contexts)
        if is_supported:
            supported_count += 1
    
    # Faithfulness = supported claims / total claims
    faithfulness_score = supported_count / len(claims)
    
    return float(faithfulness_score)


async def extract_claims(answer: str) -> List[str]:
    """Extract factual claims from answer"""
    
    prompt = f"""Extract all factual claims from this answer as a numbered list.
Only include statements that can be verified as true or false.
Ignore opinions, questions, and non-factual content.

Answer: {answer}

Claims (one per line, numbered):"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Good balance of speed and accuracy
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=500
        )
        
        claims_text = response.choices[0].message.content.strip()
        
        # Parse claims
        claims = []
        for line in claims_text.split('\n'):
            line = line.strip()
            # Remove leading numbers and markers
            line = line.lstrip('0123456789.)-* ').strip()
            if line and len(line) > 10:  # Filter out too-short fragments
                claims.append(line)
        
        return claims
    
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        return []


async def verify_claim(claim: str, contexts: List[str]) -> bool:
    """Verify if a claim is supported by any context"""
    
    context_text = "\n\n---\n\n".join(contexts)
    
    prompt = f"""Context Documents:
{context_text}

Claim to Verify: {claim}

Is this claim directly supported by the context documents above?

Rules:
- Answer YES only if the claim is explicitly stated or can be directly inferred
- Answer NO if the claim adds information not in the context
- Answer NO if unsure

Answer (YES or NO):"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,  # Deterministic
            max_tokens=5
        )
        
        verdict = response.choices[0].message.content.strip().upper()
        
        return "YES" in verdict
    
    except Exception as e:
        logger.error(f"Error verifying claim: {e}")
        return False


async def _check_faithfulness_heuristic(answer: str, contexts: List[str]) -> float:
    """Heuristic-based faithfulness (fallback)"""
    
    # Simple word overlap heuristic
    answer_words = set(answer.lower().split())
    context_words = set()
    
    for context in contexts:
        context_words.update(context.lower().split())
    
    if not answer_words:
        return 1.0
    
    # Calculate overlap
    overlap = answer_words & context_words
    overlap_ratio = len(overlap) / len(answer_words)
    
    # High overlap = high faithfulness
    return float(overlap_ratio)


async def check_faithfulness_detailed(answer: str, contexts: List[str]) -> Dict:
    """
    Detailed faithfulness analysis with claim-level breakdown
    
    Returns:
        Dict with score, claims, and verification details
    """
    if not contexts or not answer.strip():
        return {
            'score': 0.0,
            'total_claims': 0,
            'supported_claims': 0,
            'unsupported_claims': 0,
            'claim_details': []
        }
    
    try:
        if not groq_client:
            score = await _check_faithfulness_heuristic(answer, contexts)
            return {
                'score': score,
                'total_claims': 0,
                'supported_claims': 0,
                'unsupported_claims': 0,
                'claim_details': []
            }
        
        # Extract claims
        claims = await extract_claims(answer)
        
        if not claims:
            return {
                'score': 1.0,
                'total_claims': 0,
                'supported_claims': 0,
                'unsupported_claims': 0,
                'claim_details': []
            }
        
        # Verify each claim
        claim_details = []
        supported_count = 0
        
        for claim in claims:
            is_supported = await verify_claim(claim, contexts)
            
            claim_details.append({
                'claim': claim,
                'supported': is_supported,
                'status': 'SUPPORTED' if is_supported else 'UNSUPPORTED'
            })
            
            if is_supported:
                supported_count += 1
        
        unsupported_count = len(claims) - supported_count
        faithfulness_score = supported_count / len(claims)
        
        return {
            'score': faithfulness_score,
            'total_claims': len(claims),
            'supported_claims': supported_count,
            'unsupported_claims': unsupported_count,
            'claim_details': claim_details
        }
    
    except Exception as e:
        logger.error(f"Error in detailed faithfulness check: {e}")
        return {
            'score': 0.5,
            'total_claims': 0,
            'supported_claims': 0,
            'unsupported_claims': 0,
            'claim_details': [],
            'error': str(e)
        }


async def identify_hallucinations(answer: str, contexts: List[str]) -> Dict:
    """
    Identify specific hallucinated statements
    
    Returns:
        Dict with hallucinated claims and suggested corrections
    """
    detailed = await check_faithfulness_detailed(answer, contexts)
    
    hallucinations = [
        claim_info['claim']
        for claim_info in detailed.get('claim_details', [])
        if not claim_info['supported']
    ]
    
    return {
        'has_hallucinations': len(hallucinations) > 0,
        'hallucination_count': len(hallucinations),
        'hallucination_rate': 1.0 - detailed['score'],
        'hallucinated_claims': hallucinations
    }
