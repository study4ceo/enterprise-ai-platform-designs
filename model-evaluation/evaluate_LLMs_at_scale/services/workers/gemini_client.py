import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API"""
    
    # Pricing per 1M tokens
    PRICING = {
        "gemini-pro": {"input": 0.50, "output": 1.50},
        "gemini-1.5-pro": {"input": 3.50, "output": 10.50},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    }
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.models = {}
    
    def _get_model(self, model_name: str):
        """Get or create model instance"""
        if model_name not in self.models:
            self.models[model_name] = genai.GenerativeModel(model_name)
        return self.models[model_name]
    
    async def generate(self, prompt: str, model: str = "gemini-pro") -> dict:
        """Generate response from Gemini"""
        try:
            model_instance = self._get_model(model)
            
            response = await model_instance.generate_content_async(prompt)
            
            # Extract response text
            response_text = response.text
            
            # Count tokens (approximate)
            input_tokens = await self._count_tokens(prompt, model)
            output_tokens = await self._count_tokens(response_text, model)
            total_tokens = input_tokens + output_tokens
            
            # Calculate cost
            cost_usd = self._calculate_cost(model, input_tokens, output_tokens)
            
            return {
                "response": response_text,
                "tokens_used": total_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
                "model": model
            }
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    async def _count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text"""
        try:
            model_instance = self._get_model(model)
            result = await model_instance.count_tokens_async(text)
            return result.total_tokens
        except:
            # Fallback: approximate 4 chars = 1 token
            return len(text) // 4
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost"""
        pricing = self.PRICING.get(model, self.PRICING["gemini-pro"])
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
