"""
Text generation using Groq or Anthropic
"""
import os
from groq import Groq
from anthropic import Anthropic

class TextGenerator:
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'groq')
        
        if self.provider == 'groq':
            self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            self.model = 'llama-3.3-70b-versatile'
        else:
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.model = 'claude-sonnet-4-20250514'
    
    def generate(self, prompt, content_type='social', tone='professional', max_length=500):
        """Generate text content"""
        
        # Build system prompt
        system_prompt = self._build_system_prompt(content_type, tone, max_length)
        
        # Generate
        if self.provider == 'groq':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_length
            )
            return response.choices[0].message.content
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_length,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    def _build_system_prompt(self, content_type, tone, max_length):
        """Build system prompt based on content type"""
        prompts = {
            'blog': f"You are a professional blog writer. Write engaging, SEO-optimized blog content in a {tone} tone. Keep it under {max_length} words.",
            'social': f"You are a social media expert. Create engaging, viral-worthy social media posts in a {tone} tone. Keep it concise and catchy.",
            'ad': f"You are a copywriter. Create compelling ad copy that drives conversions in a {tone} tone. Focus on benefits and call-to-action.",
            'default': f"You are a content writer. Create high-quality content in a {tone} tone."
        }
        return prompts.get(content_type, prompts['default'])
