#!/usr/bin/env python3
"""
Model Evaluation for Creative Automation Hub
Evaluate text generation quality (Groq/Anthropic)
"""

import os
import json
import time
from dataclasses import dataclass
from typing import List, Dict
import numpy as np

# Evaluation libraries
from bert_score import score as bert_score
from rouge_score import rouge_scorer
from groq import Groq
from anthropic import Anthropic


@dataclass
class TestCase:
    """Single test case"""
    prompt: str
    content_type: str  # "social", "blog", "ad"
    tone: str  # "professional", "casual", "friendly"
    reference: str  # Expected output (human-written)
    criteria: Dict[str, str]  # Custom evaluation criteria


class CreativeHubEvaluator:
    """Evaluate text generation models"""
    
    def __init__(self, groq_key: str = None, anthropic_key: str = None):
        self.groq_client = Groq(api_key=groq_key or os.getenv('GROQ_API_KEY'))
        self.anthropic_client = Anthropic(api_key=anthropic_key or os.getenv('ANTHROPIC_API_KEY'))
        
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
    
    def generate_groq(self, prompt: str, content_type: str, tone: str) -> str:
        """Generate text using Groq"""
        system_prompt = f"You are a {tone} {content_type} writer. Write engaging content."
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def generate_anthropic(self, prompt: str, content_type: str, tone: str) -> str:
        """Generate text using Anthropic"""
        system_prompt = f"You are a {tone} {content_type} writer. Write engaging content."
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def evaluate_single(self, generated: str, reference: str) -> Dict:
        """Evaluate single generation"""
        
        # 1. ROUGE scores
        rouge = self.rouge_scorer.score(reference, generated)
        
        # 2. BERTScore (semantic similarity)
        P, R, F1 = bert_score([generated], [reference], lang='en', verbose=False)
        
        # 3. Length similarity
        len_ratio = len(generated) / max(len(reference), 1)
        
        # 4. Keyword presence
        ref_words = set(reference.lower().split())
        gen_words = set(generated.lower().split())
        keyword_overlap = len(ref_words & gen_words) / max(len(ref_words), 1)
        
        return {
            'rouge1': rouge['rouge1'].fmeasure,
            'rouge2': rouge['rouge2'].fmeasure,
            'rougeL': rouge['rougeL'].fmeasure,
            'bert_precision': P.item(),
            'bert_recall': R.item(),
            'bert_f1': F1.item(),
            'length_ratio': len_ratio,
            'keyword_overlap': keyword_overlap
        }
    
    def llm_as_judge(self, prompt: str, generated: str, criteria: Dict[str, str]) -> Dict:
        """Use GPT-4 to evaluate quality"""
        
        eval_prompt = f"""Evaluate this generated content:

Prompt: {prompt}

Generated Content:
{generated}

Evaluate on these criteria (score 1-5):
"""
        
        for criterion, description in criteria.items():
            eval_prompt += f"\n{criterion}: {description}"
        
        eval_prompt += "\n\nProvide scores in JSON format: {\"criterion\": score, ...}"
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert content evaluator. Provide scores in JSON format."},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0
        )
        
        try:
            scores = json.loads(response.choices[0].message.content)
            return scores
        except:
            return {}
    
    def run_comparison(self, test_case: TestCase) -> Dict:
        """Compare Groq vs Anthropic on single test"""
        
        print(f"Testing: {test_case.prompt[:50]}...")
        
        # Time Groq
        start = time.time()
        groq_output = self.generate_groq(
            test_case.prompt,
            test_case.content_type,
            test_case.tone
        )
        groq_time = time.time() - start
        
        # Time Anthropic
        start = time.time()
        anthropic_output = self.generate_anthropic(
            test_case.prompt,
            test_case.content_type,
            test_case.tone
        )
        anthropic_time = time.time() - start
        
        # Evaluate both
        groq_metrics = self.evaluate_single(groq_output, test_case.reference)
        anthropic_metrics = self.evaluate_single(anthropic_output, test_case.reference)
        
        # LLM-as-judge
        groq_judge = self.llm_as_judge(test_case.prompt, groq_output, test_case.criteria)
        anthropic_judge = self.llm_as_judge(test_case.prompt, anthropic_output, test_case.criteria)
        
        return {
            'prompt': test_case.prompt,
            'reference': test_case.reference,
            'groq': {
                'output': groq_output,
                'metrics': groq_metrics,
                'judge_scores': groq_judge,
                'time': groq_time
            },
            'anthropic': {
                'output': anthropic_output,
                'metrics': anthropic_metrics,
                'judge_scores': anthropic_judge,
                'time': anthropic_time
            }
        }
    
    def run_batch(self, test_cases: List[TestCase]) -> List[Dict]:
        """Run evaluation on multiple test cases"""
        results = []
        
        for i, test_case in enumerate(test_cases):
            print(f"\n[{i+1}/{len(test_cases)}]")
            result = self.run_comparison(test_case)
            results.append(result)
        
        return results
    
    def aggregate_results(self, results: List[Dict]) -> Dict:
        """Calculate aggregate statistics"""
        
        metrics = ['rouge1', 'rouge2', 'rougeL', 'bert_f1', 'keyword_overlap']
        
        groq_scores = {m: [] for m in metrics}
        anthropic_scores = {m: [] for m in metrics}
        
        groq_times = []
        anthropic_times = []
        
        for r in results:
            for m in metrics:
                groq_scores[m].append(r['groq']['metrics'][m])
                anthropic_scores[m].append(r['anthropic']['metrics'][m])
            
            groq_times.append(r['groq']['time'])
            anthropic_times.append(r['anthropic']['time'])
        
        return {
            'groq': {
                **{f'{m}_mean': np.mean(groq_scores[m]) for m in metrics},
                **{f'{m}_std': np.std(groq_scores[m]) for m in metrics},
                'avg_time': np.mean(groq_times)
            },
            'anthropic': {
                **{f'{m}_mean': np.mean(anthropic_scores[m]) for m in metrics},
                **{f'{m}_std': np.std(anthropic_scores[m]) for m in metrics},
                'avg_time': np.mean(anthropic_times)
            },
            'winner': self.determine_winner(groq_scores, anthropic_scores)
        }
    
    def determine_winner(self, groq_scores: Dict, anthropic_scores: Dict) -> str:
        """Determine overall winner"""
        groq_avg = np.mean([np.mean(v) for v in groq_scores.values()])
        anthropic_avg = np.mean([np.mean(v) for v in anthropic_scores.values()])
        
        if groq_avg > anthropic_avg:
            return 'Groq'
        elif anthropic_avg > groq_avg:
            return 'Anthropic'
        else:
            return 'Tie'
    
    def save_results(self, results: List[Dict], filename: str = 'eval_results.json'):
        """Save results to JSON"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")
    
    def print_summary(self, aggregate: Dict):
        """Print summary statistics"""
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        
        print("\nGroq (llama-3.3-70b):")
        print(f"  ROUGE-1:      {aggregate['groq']['rouge1_mean']:.3f} ± {aggregate['groq']['rouge1_std']:.3f}")
        print(f"  ROUGE-L:      {aggregate['groq']['rougeL_mean']:.3f} ± {aggregate['groq']['rougeL_std']:.3f}")
        print(f"  BERTScore F1: {aggregate['groq']['bert_f1_mean']:.3f} ± {aggregate['groq']['bert_f1_std']:.3f}")
        print(f"  Avg Time:     {aggregate['groq']['avg_time']:.2f}s")
        
        print("\nAnthropic (claude-sonnet-4):")
        print(f"  ROUGE-1:      {aggregate['anthropic']['rouge1_mean']:.3f} ± {aggregate['anthropic']['rouge1_std']:.3f}")
        print(f"  ROUGE-L:      {aggregate['anthropic']['rougeL_mean']:.3f} ± {aggregate['anthropic']['rougeL_std']:.3f}")
        print(f"  BERTScore F1: {aggregate['anthropic']['bert_f1_mean']:.3f} ± {aggregate['anthropic']['bert_f1_std']:.3f}")
        print(f"  Avg Time:     {aggregate['anthropic']['avg_time']:.2f}s")
        
        print(f"\n{'='*60}")
        print(f"Winner: {aggregate['winner']}")
        print(f"{'='*60}\n")


def create_test_suite() -> List[TestCase]:
    """Create test cases for Creative Automation Hub"""
    
    return [
        TestCase(
            prompt="Write a tweet about sustainable fashion",
            content_type="social",
            tone="friendly",
            reference="🌱 Love fashion AND the planet? Sustainable style is the way forward! Choose brands that care, buy less but better, and give your clothes a second life. Every choice makes a difference. #SustainableFashion #EcoStyle",
            criteria={
                "engagement": "Is it engaging and shareable?",
                "clarity": "Is the message clear?",
                "call_to_action": "Does it inspire action?"
            }
        ),
        TestCase(
            prompt="Write a blog intro about remote work benefits",
            content_type="blog",
            tone="professional",
            reference="Remote work has transformed from a rare perk to a standard practice for millions worldwide. This shift brings compelling advantages: increased flexibility, reduced commute stress, and improved work-life balance. In this article, we'll explore the key benefits that make remote work attractive to both employees and employers.",
            criteria={
                "professionalism": "Is the tone professional?",
                "structure": "Is it well-structured?",
                "informativeness": "Does it provide value?"
            }
        ),
        TestCase(
            prompt="Create ad copy for a project management tool",
            content_type="ad",
            tone="professional",
            reference="Stop juggling tools. TaskMaster brings your team together with intuitive project tracking, real-time collaboration, and automated workflows. Get started free—no credit card required.",
            criteria={
                "persuasiveness": "Is it convincing?",
                "clarity": "Is the value proposition clear?",
                "call_to_action": "Strong CTA?"
            }
        )
    ]


def main():
    """Run evaluation"""
    
    # Initialize evaluator
    evaluator = CreativeHubEvaluator()
    
    # Create test suite
    test_cases = create_test_suite()
    
    print("Starting Creative Automation Hub Model Evaluation")
    print(f"Test cases: {len(test_cases)}")
    print(f"Models: Groq (llama-3.3-70b) vs Anthropic (claude-sonnet-4)")
    
    # Run evaluation
    results = evaluator.run_batch(test_cases)
    
    # Aggregate results
    aggregate = evaluator.aggregate_results(results)
    
    # Print summary
    evaluator.print_summary(aggregate)
    
    # Save results
    evaluator.save_results(results)
    
    # Print individual results
    print("\nDetailed Results:")
    for i, result in enumerate(results):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Prompt: {result['prompt']}")
        print(f"\nGroq Output:\n{result['groq']['output'][:200]}...")
        print(f"\nAnthropic Output:\n{result['anthropic']['output'][:200]}...")
        print(f"\nGroq Metrics: ROUGE-1={result['groq']['metrics']['rouge1']:.3f}, BERT={result['groq']['metrics']['bert_f1']:.3f}")
        print(f"Anthropic Metrics: ROUGE-1={result['anthropic']['metrics']['rouge1']:.3f}, BERT={result['anthropic']['metrics']['bert_f1']:.3f}")


if __name__ == '__main__':
    main()
