import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)
else:
    groq_client = None
    logger.warning("GROQ_API_KEY not set - hallucination detection will use fallback")


async def detect_hallucination(candidate: str, reference: str = None, **kwargs) -> float:
    """
    Detect hallucinations in generated text
    
    Hallucination = generating information not supported by the context/reference.
    Uses LLM-as-Judge (Groq) for fast, accurate detection.
    
    Args:
        candidate: Generated text to check
        reference: Reference context (ground truth or retrieved docs)
        **kwargs: Additional arguments (context: str - for RAG use cases)
    
    Returns:
        Hallucination score (0=no hallucination, 1=full hallucination)
    """
    if not reference and not kwargs.get('context'):
        # No reference to check against
        return 0.0
    
    if not candidate.strip():
        return 0.0
    
    context = kwargs.get('context', reference)
    
    try:
        if groq_client:
            # Use Groq LLM-as-Judge (fast and accurate)
            return await _detect_hallucination_llm(candidate, context)
        else:
            # Fallback to heuristic-based detection
            return await _detect_hallucination_heuristic(candidate, context)
    
    except Exception as e:
        logger.error(f"Error detecting hallucination: {e}")
        return 0.5  # Return neutral score on error


async def _detect_hallucination_llm(candidate: str, context: str) -> float:
    """Use LLM to detect hallucinations"""
    
    prompt = f"""You are an expert at detecting hallucinations in AI-generated text.

Context (Source of Truth):
{context}

Generated Response:
{candidate}

Task: Identify if the generated response contains ANY information not supported by the context.

Instructions:
1. Extract all factual claims from the generated response
2. Check if EACH claim is supported by the context
3. Calculate: (unsupported claims) / (total claims)

Respond with ONLY a number between 0 and 1:
- 0.0 = No hallucinations (all claims supported)
- 0.5 = Some hallucinations  
- 1.0 = Severe hallucinations (most claims unsupported)

Score:"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Fast and accurate
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,  # Deterministic
            max_tokens=10
        )
        
        score_text = response.choices[0].message.content.strip()
        
        # Parse score
        score = float(score_text)
        
        # Clamp to [0, 1]
        score = max(0.0, min(1.0, score))
        
        return score
    
    except Exception as e:
        logger.error(f"Error in LLM hallucination detection: {e}")
        return 0.5


async def _detect_hallucination_heuristic(candidate: str, context: str) -> float:
    """Heuristic-based hallucination detection (fallback)"""
    
    # Simple overlap-based heuristic
    candidate_words = set(candidate.lower().split())
    context_words = set(context.lower().split())
    
    if len(candidate_words) == 0:
        return 0.0
    
    # Calculate overlap
    overlap = candidate_words & context_words
    overlap_ratio = len(overlap) / len(candidate_words)
    
    # Convert to hallucination score (inverse of overlap)
    # High overlap = low hallucination
    hallucination_score = 1.0 - overlap_ratio
    
    return float(hallucination_score)


async def detect_hallucination_detailed(candidate: str, reference: str = None, **kwargs) -> dict:
    """
    Detailed hallucination detection with claim-level analysis
    
    Returns:
        Dict with overall score and detected hallucinated claims
    """
    context = kwargs.get('context', reference)
    
    if not context:
        return {
            'score': 0.0,
            'claims_total': 0,
            'claims_supported': 0,
            'claims_unsupported': 0,
            'hallucinated_claims': []
        }
    
    try:
        if not groq_client:
            score = await _detect_hallucination_heuristic(candidate, context)
            return {
                'score': score,
                'claims_total': 0,
                'claims_supported': 0,
                'claims_unsupported': 0,
                'hallucinated_claims': []
            }
        
        # Extract claims
        claims = await _extract_claims(candidate)
        
        if not claims:
            return {
                'score': 0.0,
                'claims_total': 0,
                'claims_supported': 0,
                'claims_unsupported': 0,
                'hallucinated_claims': []
            }
        
        # Check each claim
        hallucinated_claims = []
        supported_count = 0
        
        for claim in claims:
            is_supported = await _verify_claim(claim, context)
            if is_supported:
                supported_count += 1
            else:
                hallucinated_claims.append(claim)
        
        unsupported_count = len(claims) - supported_count
        hallucination_score = unsupported_count / len(claims) if claims else 0.0
        
        return {
            'score': hallucination_score,
            'claims_total': len(claims),
            'claims_supported': supported_count,
            'claims_unsupported': unsupported_count,
            'hallucinated_claims': hallucinated_claims
        }
    
    except Exception as e:
        logger.error(f"Error in detailed hallucination detection: {e}")
        return {
            'score': 0.5,
            'claims_total': 0,
            'claims_supported': 0,
            'claims_unsupported': 0,
            'hallucinated_claims': []
        }


async def _extract_claims(text: str) -> list:
    """Extract factual claims from text"""
    
    prompt = f"""Extract all factual claims from this text as a numbered list.
Only include statements that can be verified as true or false.

Text: {text}

Claims (one per line):"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast for extraction
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        claims_text = response.choices[0].message.content
        
        # Parse claims (remove numbers and empty lines)
        claims = []
        for line in claims_text.split('\n'):
            line = line.strip()
            # Remove leading numbers like "1. " or "1) "
            line = line.lstrip('0123456789.)-) ').strip()
            if line:
                claims.append(line)
        
        return claims
    
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        return []


async def _verify_claim(claim: str, context: str) -> bool:
    """Verify if a claim is supported by context"""
    
    prompt = f"""Context: {context}

Claim: {claim}

Is this claim directly supported by the context above?
Answer with only "YES" or "NO".

Answer:"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=5
        )
        
        answer = response.choices[0].message.content.strip().upper()
        
        return "YES" in answer
    
    except Exception as e:
        logger.error(f"Error verifying claim: {e}")
        return False
