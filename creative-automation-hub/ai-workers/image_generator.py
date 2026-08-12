"""
Image generation using Stability AI or placeholder
"""
import os
import requests

class ImageGenerator:
    def __init__(self):
        self.api_key = os.getenv('STABILITY_API_KEY')
        self.use_placeholder = not self.api_key
    
    def generate(self, prompt, width=1024, height=1024, style='realistic'):
        """Generate image"""
        
        if self.use_placeholder:
            # Use placeholder for MVP
            return self._generate_placeholder(prompt, width, height)
        
        # Use Stability AI
        return self._generate_stable_diffusion(prompt, width, height, style)
    
    def _generate_placeholder(self, prompt, width, height):
        """Generate placeholder image URL"""
        # Use a free placeholder service
        text = prompt[:50].replace(' ', '+')
        return f"https://via.placeholder.com/{width}x{height}/3357FF/ffffff?text={text}"
    
    def _generate_stable_diffusion(self, prompt, width, height, style):
        """Generate using Stability AI"""
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
            "style_preset": style if style else "photographic"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Stability AI error: {response.text}")
        
        data = response.json()
        # Save image and return URL
        # For MVP, return base64 or upload to S3
        return data['artifacts'][0]['base64']
