from openai import AsyncOpenAI
import tiktoken
import logging

logger = logging.getLogger(__name__)


class GPTClient:
    """Client for OpenAI GPT API"""
    
    # Pricing per 1M tokens
    PRICING = {
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-4o": {"input": 5.00, "output": 15.00},
    }
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.encoders = {}
    
    def _get_encoder(self, model: str):
        """Get token encoder for model"""
        if model not in self.encoders:
            try:
                self.encoders[model] = tiktoken.encoding_for_model(model)
            except:
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        return self.encoders[model]
    
    async def generate(self, prompt: str, model: str = "gpt-3.5-turbo") -> dict:
        """Generate response from GPT"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Get token usage
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
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
            logger.error(f"GPT API error: {e}")
            raise
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost"""
        # Get base model name
        base_model = model.split("-")[0] + "-" + model.split("-")[1]
        if base_model not in self.PRICING:
            base_model = "gpt-3.5-turbo"
        
        pricing = self.PRICING.get(base_model, self.PRICING["gpt-3.5-turbo"])
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
