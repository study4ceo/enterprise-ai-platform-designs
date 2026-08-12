"""
Relevance Scorers for RAG Evaluation

Checks:
1. Answer Relevance - Does the answer address the question?
2. Context Relevance - Are retrieved documents relevant to the query?
"""

import os
import logging
from typing import List, Dict
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)
else:
    groq_client = None
    logger.warning("GROQ_API_KEY not set - relevance checking will use embeddings only")

# Initialize embedding model (lightweight and fast)
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    embedding_model = None


# ========== ANSWER RELEVANCE ==========

async def check_answer_relevance(query: str, answer: str) -> float:
    """
    Check if answer addresses the query
    
    Uses both semantic similarity and LLM judgment for accuracy.
    
    Args:
        query: User's question
        answer: Generated answer
    
    Returns:
        Relevance score (0=irrelevant, 1=highly relevant)
    """
    if not query or not answer.strip():
        return 0.0
    
    try:
        # Method 1: Embedding similarity (fast)
        embedding_score = await _answer_relevance_embedding(query, answer)
        
        # Method 2: LLM judge (accurate)
        if groq_client:
            llm_score = await _answer_relevance_llm(query, answer)
            # Weighted average: 40% embedding, 60% LLM
            final_score = 0.4 * embedding_score + 0.6 * llm_score
        else:
            final_score = embedding_score
        
        return float(final_score)
    
    except Exception as e:
        logger.error(f"Error checking answer relevance: {e}")
        return 0.5


async def _answer_relevance_embedding(query: str, answer: str) -> float:
    """Embedding-based relevance (fast)"""
    
    if not embedding_model:
        return 0.5
    
    try:
        query_emb = embedding_model.encode([query])
        answer_emb = embedding_model.encode([answer])
        
        similarity = cosine_similarity(query_emb, answer_emb)[0][0]
        
        # Normalize to [0, 1] range
        # Cosine similarity is already in [-1, 1], typically positive for relevant text
        score = max(0.0, min(1.0, similarity))
        
        return float(score)
    
    except Exception as e:
        logger.error(f"Error in embedding relevance: {e}")
        return 0.5


async def _answer_relevance_llm(query: str, answer: str) -> float:
    """LLM-based relevance judgment (accurate)"""
    
    prompt = f"""Query: {query}

Answer: {answer}

Does the answer directly address the query?

Rate from 0.0 to 1.0:
- 1.0 = Perfectly addresses the query, comprehensive answer
- 0.8 = Good answer, addresses main points
- 0.6 = Partially answers, misses some aspects
- 0.4 = Tangentially related but doesn't answer
- 0.2 = Somewhat related but off-topic
- 0.0 = Completely irrelevant

Respond with ONLY a number between 0.0 and 1.0.

Score:"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast enough for relevance
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=10
        )
        
        score_text = response.choices[0].message.content.strip()
        score = float(score_text)
        
        # Clamp to [0, 1]
        score = max(0.0, min(1.0, score))
        
        return score
    
    except Exception as e:
        logger.error(f"Error in LLM relevance: {e}")
        return 0.5


async def check_answer_relevance_detailed(query: str, answer: str) -> Dict:
    """
    Detailed answer relevance analysis
    
    Returns:
        Dict with overall score and breakdown
    """
    if not query or not answer.strip():
        return {
            'score': 0.0,
            'embedding_score': 0.0,
            'llm_score': 0.0,
            'verdict': 'irrelevant'
        }
    
    try:
        embedding_score = await _answer_relevance_embedding(query, answer)
        
        llm_score = 0.0
        if groq_client:
            llm_score = await _answer_relevance_llm(query, answer)
        
        # Combined score
        if groq_client:
            final_score = 0.4 * embedding_score + 0.6 * llm_score
        else:
            final_score = embedding_score
        
        # Verdict
        if final_score >= 0.8:
            verdict = 'highly relevant'
        elif final_score >= 0.6:
            verdict = 'relevant'
        elif final_score >= 0.4:
            verdict = 'partially relevant'
        else:
            verdict = 'irrelevant'
        
        return {
            'score': final_score,
            'embedding_score': embedding_score,
            'llm_score': llm_score,
            'verdict': verdict
        }
    
    except Exception as e:
        logger.error(f"Error in detailed answer relevance: {e}")
        return {
            'score': 0.5,
            'embedding_score': 0.0,
            'llm_score': 0.0,
            'verdict': 'unknown',
            'error': str(e)
        }


# ========== CONTEXT RELEVANCE ==========

async def check_context_relevance(query: str, contexts: List[str], threshold: float = 0.3) -> float:
    """
    Check if retrieved contexts are relevant to the query
    
    Args:
        query: User's question
        contexts: List of retrieved documents
        threshold: Relevance threshold (default 0.3)
    
    Returns:
        Average relevance score (0=irrelevant, 1=highly relevant)
    """
    if not contexts or not query:
        return 0.0
    
    try:
        relevant_count = 0
        relevance_scores = []
        
        for context in contexts:
            is_relevant, score = await _is_context_relevant(query, context, threshold)
            relevance_scores.append(score)
            if is_relevant:
                relevant_count += 1
        
        # Average relevance score
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        return float(avg_relevance)
    
    except Exception as e:
        logger.error(f"Error checking context relevance: {e}")
        return 0.5


async def _is_context_relevant(query: str, context: str, threshold: float = 0.3) -> tuple:
    """
    Check if a single context is relevant to query
    
    Returns:
        (is_relevant: bool, relevance_score: float)
    """
    if not embedding_model:
        return False, 0.0
    
    try:
        query_emb = embedding_model.encode([query])
        context_emb = embedding_model.encode([context])
        
        similarity = cosine_similarity(query_emb, context_emb)[0][0]
        
        # Normalize
        score = max(0.0, min(1.0, similarity))
        
        is_relevant = score >= threshold
        
        return is_relevant, float(score)
    
    except Exception as e:
        logger.error(f"Error checking context relevance: {e}")
        return False, 0.0


async def check_context_relevance_detailed(query: str, contexts: List[str], threshold: float = 0.3) -> Dict:
    """
    Detailed context relevance analysis
    
    Returns:
        Dict with per-document relevance scores
    """
    if not contexts or not query:
        return {
            'overall_score': 0.0,
            'relevant_count': 0,
            'total_count': 0,
            'relevance_ratio': 0.0,
            'context_scores': []
        }
    
    try:
        context_scores = []
        relevant_count = 0
        
        for idx, context in enumerate(contexts):
            is_relevant, score = await _is_context_relevant(query, context, threshold)
            
            context_scores.append({
                'context_index': idx,
                'relevance_score': score,
                'is_relevant': is_relevant,
                'preview': context[:100] + '...' if len(context) > 100 else context
            })
            
            if is_relevant:
                relevant_count += 1
        
        # Calculate metrics
        scores_only = [cs['relevance_score'] for cs in context_scores]
        overall_score = sum(scores_only) / len(scores_only) if scores_only else 0.0
        relevance_ratio = relevant_count / len(contexts) if contexts else 0.0
        
        return {
            'overall_score': overall_score,
            'relevant_count': relevant_count,
            'total_count': len(contexts),
            'relevance_ratio': relevance_ratio,
            'context_scores': context_scores
        }
    
    except Exception as e:
        logger.error(f"Error in detailed context relevance: {e}")
        return {
            'overall_score': 0.0,
            'relevant_count': 0,
            'total_count': len(contexts) if contexts else 0,
            'relevance_ratio': 0.0,
            'context_scores': [],
            'error': str(e)
        }


# ========== CONTEXT PRECISION ==========

async def calculate_context_precision(query: str, contexts: List[str], threshold: float = 0.3) -> float:
    """
    Calculate Context Precision@k
    
    Checks if relevant contexts appear early in the ranking.
    
    Args:
        query: User's question
        contexts: List of contexts (in retrieval order)
        threshold: Relevance threshold
    
    Returns:
        Precision score (0-1)
    """
    if not contexts:
        return 0.0
    
    try:
        relevant_positions = []
        
        for idx, context in enumerate(contexts):
            is_relevant, _ = await _is_context_relevant(query, context, threshold)
            if is_relevant:
                relevant_positions.append(idx + 1)  # 1-indexed
        
        if not relevant_positions:
            return 0.0
        
        # Calculate precision: relevant docs / total docs up to position
        precisions = []
        for pos in relevant_positions:
            precision_at_pos = len([p for p in relevant_positions if p <= pos]) / pos
            precisions.append(precision_at_pos)
        
        # Average precision
        avg_precision = sum(precisions) / len(relevant_positions)
        
        return float(avg_precision)
    
    except Exception as e:
        logger.error(f"Error calculating context precision: {e}")
        return 0.0
