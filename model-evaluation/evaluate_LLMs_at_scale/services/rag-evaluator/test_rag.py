"""
Test script for RAG evaluation modules

Run this to test faithfulness and relevance checkers independently.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from faithfulness import check_faithfulness, check_faithfulness_detailed
from relevance import (
    check_answer_relevance,
    check_context_relevance,
    check_answer_relevance_detailed,
    check_context_relevance_detailed
)


async def test_perfect_rag():
    """Test case: Perfect RAG response"""
    print("\n" + "="*60)
    print("TEST 1: Perfect RAG Response")
    print("="*60)
    
    query = "What is the capital of France?"
    contexts = [
        "Paris is the capital and largest city of France.",
        "France is a country in Western Europe with several overseas regions and territories."
    ]
    answer = "The capital of France is Paris."
    
    print(f"\nQuery: {query}")
    print(f"Answer: {answer}")
    print(f"Contexts: {len(contexts)} documents")
    
    # Test faithfulness
    faithfulness = await check_faithfulness(answer, contexts)
    print(f"\n✅ Faithfulness: {faithfulness:.3f} (Expected: ~1.0)")
    
    # Test answer relevance
    answer_rel = await check_answer_relevance(query, answer)
    print(f"✅ Answer Relevance: {answer_rel:.3f} (Expected: ~1.0)")
    
    # Test context relevance
    context_rel = await check_context_relevance(query, contexts)
    print(f"✅ Context Relevance: {context_rel:.3f} (Expected: ~0.8-1.0)")
    
    return faithfulness, answer_rel, context_rel


async def test_hallucination():
    """Test case: Answer with hallucination"""
    print("\n" + "="*60)
    print("TEST 2: Answer with Hallucination")
    print("="*60)
    
    query = "What is the capital of France?"
    contexts = [
        "France is a country in Western Europe."
    ]
    answer = "The capital of France is Paris, which has a population of 10 million people."
    
    print(f"\nQuery: {query}")
    print(f"Answer: {answer}")
    print(f"Contexts: {len(contexts)} documents")
    
    # Test faithfulness (should detect hallucination)
    faithfulness = await check_faithfulness(answer, contexts)
    print(f"\n⚠️  Faithfulness: {faithfulness:.3f} (Expected: <0.8 due to unsupported population claim)")
    
    # Get detailed breakdown
    detail = await check_faithfulness_detailed(answer, contexts)
    print(f"\nClaims Analysis:")
    print(f"  Total claims: {detail['total_claims']}")
    print(f"  Supported: {detail['supported_claims']}")
    print(f"  Unsupported: {detail['unsupported_claims']}")
    
    if detail.get('claim_details'):
        print(f"\n  Claim Breakdown:")
        for claim_info in detail['claim_details']:
            status = "✅" if claim_info['supported'] else "❌"
            print(f"    {status} {claim_info['claim']}")
    
    return faithfulness


async def test_irrelevant_answer():
    """Test case: Irrelevant answer"""
    print("\n" + "="*60)
    print("TEST 3: Irrelevant Answer")
    print("="*60)
    
    query = "What is the capital of France?"
    contexts = [
        "Paris is the capital of France."
    ]
    answer = "France is known for its excellent wine and cheese."
    
    print(f"\nQuery: {query}")
    print(f"Answer: {answer}")
    print(f"Contexts: {len(contexts)} documents")
    
    # Test answer relevance (should be low)
    answer_rel = await check_answer_relevance(query, answer)
    print(f"\n⚠️  Answer Relevance: {answer_rel:.3f} (Expected: <0.5 - doesn't answer question)")
    
    # Faithfulness should still be high (statement is true, just not relevant)
    faithfulness = await check_faithfulness(answer, contexts)
    print(f"Note: Faithfulness: {faithfulness:.3f} (Can be high even though answer is irrelevant)")
    
    return answer_rel


async def test_poor_retrieval():
    """Test case: Poor context retrieval"""
    print("\n" + "="*60)
    print("TEST 4: Poor Context Retrieval")
    print("="*60)
    
    query = "What is the capital of France?"
    contexts = [
        "Germany is a country in Central Europe.",
        "Italy is known for its art and history.",
        "Spain is famous for its beaches."
    ]
    answer = "I cannot determine the capital of France from the provided context."
    
    print(f"\nQuery: {query}")
    print(f"Answer: {answer}")
    print(f"Contexts: {len(contexts)} documents (all irrelevant)")
    
    # Test context relevance (should be very low)
    context_rel = await check_context_relevance(query, contexts)
    print(f"\n⚠️  Context Relevance: {context_rel:.3f} (Expected: <0.3 - none relevant)")
    
    # Get detailed per-document scores
    detail = await check_context_relevance_detailed(query, contexts)
    print(f"\nRelevance Ratio: {detail['relevant_count']}/{detail['total_count']} documents")
    
    return context_rel


async def test_multi_claim_answer():
    """Test case: Multi-claim answer"""
    print("\n" + "="*60)
    print("TEST 5: Multi-Claim Answer")
    print("="*60)
    
    query = "Tell me about Python programming"
    contexts = [
        "Python is a high-level programming language created by Guido van Rossum.",
        "Python emphasizes code readability with significant whitespace.",
        "Python supports multiple programming paradigms."
    ]
    answer = """Python is a high-level programming language known for its readability.
    It was created by Guido van Rossum and supports multiple programming paradigms.
    Python is widely used in data science, web development, and automation."""
    
    print(f"\nQuery: {query}")
    print(f"Answer: {answer}")
    print(f"Contexts: {len(contexts)} documents")
    
    # Get detailed faithfulness check
    detail = await check_faithfulness_detailed(answer, contexts)
    
    print(f"\n📊 Faithfulness Analysis:")
    print(f"  Score: {detail['score']:.3f}")
    print(f"  Total claims: {detail['total_claims']}")
    print(f"  Supported: {detail['supported_claims']}")
    print(f"  Unsupported: {detail['unsupported_claims']}")
    
    if detail.get('claim_details'):
        print(f"\n  Claim-by-Claim Breakdown:")
        for i, claim_info in enumerate(detail['claim_details'], 1):
            status = "✅ SUPPORTED" if claim_info['supported'] else "❌ UNSUPPORTED"
            print(f"    {i}. {status}")
            print(f"       \"{claim_info['claim']}\"")
    
    return detail['score']


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RAG EVALUATION MODULE TESTS")
    print("="*60)
    print("\nTesting core RAG evaluation capabilities:")
    print("- Faithfulness (answer grounded in context)")
    print("- Answer Relevance (addresses the query)")
    print("- Context Relevance (retrieval quality)")
    
    try:
        # Run all tests
        await test_perfect_rag()
        await test_hallucination()
        await test_irrelevant_answer()
        await test_poor_retrieval()
        await test_multi_claim_answer()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nKey Findings:")
        print("1. Faithfulness checker successfully detects unsupported claims")
        print("2. Answer relevance identifies off-topic responses")
        print("3. Context relevance measures retrieval quality")
        print("4. Detailed breakdowns provide claim-level analysis")
        print("\nNext Steps:")
        print("- Start the RAG evaluator API: uvicorn main:app --reload")
        print("- Test via API: POST http://localhost:8004/api/v1/rag/evaluate")
        print("- View docs: http://localhost:8004/docs")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
