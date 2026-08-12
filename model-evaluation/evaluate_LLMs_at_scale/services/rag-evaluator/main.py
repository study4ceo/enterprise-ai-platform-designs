"""
RAG Evaluator Service - Main API

Provides endpoints for evaluating RAG (Retrieval-Augmented Generation) systems.
Measures faithfulness, relevance, and other RAG-specific metrics.
"""

import asyncio
import logging
import sys
import time
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

sys.path.append('../shared')

from shared.database import DatabaseManager, get_session
from shared.redis_client import RedisClient
from shared.models import (
    RAGEvaluationRequest,
    RAGEvaluationResponse,
    RAGEvaluationListResponse,
    RAGStatsResponse,
    RAGEvaluationDetailed
)

from faithfulness import check_faithfulness, check_faithfulness_detailed
from relevance import (
    check_answer_relevance,
    check_context_relevance,
    check_answer_relevance_detailed,
    check_context_relevance_detailed,
    calculate_context_precision
)
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Evaluator Service",
    description="Evaluate RAG systems with comprehensive metrics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_manager = DatabaseManager(settings.DATABASE_URL)
redis_client = RedisClient(settings.REDIS_URL)


# ========== STARTUP & SHUTDOWN ==========

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    await redis_client.connect()
    logger.info(f"{settings.SERVICE_NAME} started successfully on port {settings.SERVICE_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")
    await redis_client.close()
    await db_manager.close()
    logger.info(f"{settings.SERVICE_NAME} shut down successfully")


# ========== HEALTH CHECK ==========

@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with dependency status"""
    health = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {}
    }
    
    # Check Redis
    try:
        await redis_client.ping()
        health["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check Database
    try:
        async for session in get_session():
            await session.execute(select(1))
            health["dependencies"]["database"] = "healthy"
            break
    except Exception as e:
        health["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    return health


# ========== RAG EVALUATION ENDPOINTS ==========

@app.post(
    "/api/v1/rag/evaluate",
    response_model=RAGEvaluationResponse,
    tags=["RAG Evaluation"]
)
async def evaluate_rag(
    request: RAGEvaluationRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Evaluate a RAG response
    
    Calculates:
    - Faithfulness (answer grounded in context)
    - Answer Relevance (addresses the query)
    - Context Relevance (retrieval quality)
    - Context Precision (ranking quality)
    
    Uses Groq for fast, accurate LLM-as-Judge evaluation.
    """
    evaluation_id = uuid4()
    start_time = time.time()
    
    logger.info(f"Starting RAG evaluation {evaluation_id}")
    
    try:
        # Extract contexts from retrieved documents
        contexts = [doc.content for doc in request.retrieved_docs]
        
        # Check cache first
        cache_key = f"rag_eval:{hash(request.query_text + request.generated_answer + str(contexts))}"
        cached_result = await redis_client.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for evaluation {evaluation_id}")
            return RAGEvaluationResponse(**cached_result)
        
        # Calculate metrics in parallel for speed
        faithfulness, answer_rel, context_rel, context_prec = await asyncio.gather(
            check_faithfulness(request.generated_answer, contexts),
            check_answer_relevance(request.query_text, request.generated_answer),
            check_context_relevance(request.query_text, contexts),
            calculate_context_precision(request.query_text, contexts)
        )
        
        # Calculate total time
        total_time_ms = int((time.time() - start_time) * 1000)
        
        # Estimate cost (Groq usage for faithfulness + answer relevance)
        # ~1000 tokens for faithfulness, ~100 for relevance = ~$0.001
        estimated_cost = 0.0011
        
        # Create response
        response = RAGEvaluationResponse(
            evaluation_id=evaluation_id,
            query_text=request.query_text,
            generated_answer=request.generated_answer,
            reference_answer=request.reference_answer,
            num_retrieved_docs=len(request.retrieved_docs),
            faithfulness_score=faithfulness,
            answer_relevance_score=answer_rel,
            context_relevance_score=context_rel,
            context_precision_score=context_prec,
            total_time_ms=total_time_ms,
            total_cost_usd=estimated_cost,
            timestamp=datetime.utcnow()
        )
        
        # Cache result
        await redis_client.set(
            cache_key,
            response.dict(),
            ttl=settings.CACHE_TTL
        )
        
        # Store in database (async, don't wait)
        asyncio.create_task(_store_evaluation(session, request, response))
        
        logger.info(
            f"Evaluation {evaluation_id} complete - "
            f"Faithfulness: {faithfulness:.3f}, "
            f"Answer Rel: {answer_rel:.3f}, "
            f"Context Rel: {context_rel:.3f}, "
            f"Time: {total_time_ms}ms"
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error in RAG evaluation {evaluation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@app.post(
    "/api/v1/rag/evaluate/detailed",
    response_model=RAGEvaluationDetailed,
    tags=["RAG Evaluation"]
)
async def evaluate_rag_detailed(
    request: RAGEvaluationRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Evaluate RAG with detailed breakdown
    
    Returns:
    - All standard metrics
    - Claim-level faithfulness analysis
    - Per-document relevance scores
    - Detailed breakdowns
    """
    evaluation_id = uuid4()
    start_time = time.time()
    
    logger.info(f"Starting detailed RAG evaluation {evaluation_id}")
    
    try:
        contexts = [doc.content for doc in request.retrieved_docs]
        
        # Get detailed metrics
        faithfulness_detail, answer_rel_detail, context_rel_detail = await asyncio.gather(
            check_faithfulness_detailed(request.generated_answer, contexts),
            check_answer_relevance_detailed(request.query_text, request.generated_answer),
            check_context_relevance_detailed(request.query_text, contexts)
        )
        
        context_prec = await calculate_context_precision(request.query_text, contexts)
        
        total_time_ms = int((time.time() - start_time) * 1000)
        
        response = RAGEvaluationDetailed(
            evaluation_id=evaluation_id,
            query_text=request.query_text,
            generated_answer=request.generated_answer,
            reference_answer=request.reference_answer,
            num_retrieved_docs=len(request.retrieved_docs),
            faithfulness_score=faithfulness_detail['score'],
            answer_relevance_score=answer_rel_detail['score'],
            context_relevance_score=context_rel_detail['overall_score'],
            context_precision_score=context_prec,
            faithfulness_detail=faithfulness_detail,
            answer_relevance_detail=answer_rel_detail,
            context_relevance_detail=context_rel_detail,
            total_time_ms=total_time_ms,
            total_cost_usd=0.0011,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Detailed evaluation {evaluation_id} complete in {total_time_ms}ms")
        
        return response
    
    except Exception as e:
        logger.error(f"Error in detailed evaluation {evaluation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailed evaluation failed: {str(e)}"
        )


@app.post(
    "/api/v1/rag/evaluate/batch",
    response_model=List[RAGEvaluationResponse],
    tags=["RAG Evaluation"]
)
async def evaluate_rag_batch(
    requests: List[RAGEvaluationRequest],
    session: AsyncSession = Depends(get_session)
):
    """
    Batch evaluate multiple RAG responses
    
    Evaluates all requests in parallel for speed.
    """
    logger.info(f"Starting batch evaluation of {len(requests)} RAG responses")
    
    try:
        # Process all evaluations in parallel
        tasks = [evaluate_rag(req, session) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        successful_results = [
            r for r in results
            if not isinstance(r, Exception)
        ]
        
        logger.info(
            f"Batch evaluation complete - "
            f"{len(successful_results)}/{len(requests)} successful"
        )
        
        return successful_results
    
    except Exception as e:
        logger.error(f"Error in batch evaluation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch evaluation failed: {str(e)}"
        )


@app.get(
    "/api/v1/rag/evaluations",
    response_model=RAGEvaluationListResponse,
    tags=["RAG Evaluation"]
)
async def list_evaluations(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session)
):
    """
    List RAG evaluations with pagination
    """
    try:
        # This will need actual database implementation
        # For now, return empty list
        return RAGEvaluationListResponse(
            evaluations=[],
            total=0,
            skip=skip,
            limit=limit
        )
    
    except Exception as e:
        logger.error(f"Error listing evaluations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list evaluations: {str(e)}"
        )


@app.get(
    "/api/v1/rag/stats",
    response_model=RAGStatsResponse,
    tags=["RAG Evaluation"]
)
async def get_rag_stats(session: AsyncSession = Depends(get_session)):
    """
    Get aggregate RAG evaluation statistics
    """
    try:
        # This will need actual database implementation
        # For now, return default stats
        return RAGStatsResponse(
            total_evaluations=0,
            avg_faithfulness=0.0,
            avg_answer_relevance=0.0,
            avg_context_relevance=0.0,
            avg_evaluation_time_ms=0,
            total_cost_usd=0.0
        )
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


# ========== HELPER FUNCTIONS ==========

async def _store_evaluation(
    session: AsyncSession,
    request: RAGEvaluationRequest,
    response: RAGEvaluationResponse
):
    """Store evaluation in database (async background task)"""
    try:
        # Database storage implementation would go here
        # For now, just log
        logger.info(f"Would store evaluation {response.evaluation_id} in database")
    except Exception as e:
        logger.error(f"Error storing evaluation: {e}", exc_info=True)


# ========== MAIN ==========

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=True  # For development
    )
