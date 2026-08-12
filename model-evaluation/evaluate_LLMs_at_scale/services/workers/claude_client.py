from anthropic import AsyncAnthropic
import logging

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for Anthropic Claude API"""
    
    # Pricing per 1M tokens
    PRICING = {
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    }
    
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate(self, prompt: str, model: str = "claude-3-sonnet-20240229") -> dict:
        """Generate response from Claude"""
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response
            response_text = response.content[0].text
            
            # Get token usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
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
            logger.error(f"Claude API error: {e}")
            raise
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost"""
        # Extract base model name
        if "opus" in model.lower():
            base_model = "claude-3-opus"
        elif "sonnet" in model.lower():
            base_model = "claude-3-sonnet"
        elif "haiku" in model.lower():
            base_model = "claude-3-haiku"
        else:
            base_model = "claude-3-sonnet"
        
        pricing = self.PRICING[base_model]
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
