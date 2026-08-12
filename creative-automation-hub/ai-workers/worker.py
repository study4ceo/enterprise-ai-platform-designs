#!/usr/bin/env python3
"""
AI Worker - Processes jobs from Redis queue
"""
import os
import json
import time
import redis
from dotenv import load_dotenv
from text_generator import TextGenerator
from image_generator import ImageGenerator

load_dotenv()

class Worker:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', ''),
            decode_responses=True
        )
        self.text_gen = TextGenerator()
        self.image_gen = ImageGenerator()
        self.poll_interval = int(os.getenv('POLL_INTERVAL', 1))
        
    def process_text_job(self, job):
        """Process text generation job"""
        try:
            input_data = job['input']
            variants = []
            
            for i in range(input_data.get('variants', 3)):
                text = self.text_gen.generate(
                    prompt=input_data['prompt'],
                    content_type=input_data.get('type', 'social'),
                    tone=input_data.get('tone', 'professional'),
                    max_length=input_data.get('max_length', 500)
                )
                variants.append({
                    'id': i + 1,
                    'content': text
                })
            
            return {
                'variants': variants,
                'count': len(variants)
            }
        except Exception as e:
            raise Exception(f"Text generation failed: {str(e)}")
    
    def process_image_job(self, job):
        """Process image generation job"""
        try:
            input_data = job['input']
            variants = []
            
            for i in range(input_data.get('variants', 2)):
                image_url = self.image_gen.generate(
                    prompt=input_data['prompt'],
                    width=input_data.get('width', 1024),
                    height=input_data.get('height', 1024),
                    style=input_data.get('style', 'realistic')
                )
                variants.append({
                    'id': i + 1,
                    'url': image_url
                })
            
            return {
                'variants': variants,
                'count': len(variants)
            }
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    def update_job_status(self, job_id, status, output=None, error=None):
        """Update job status in Redis"""
        job_key = f"job:{job_id}"
        job_data = self.redis.get(job_key)
        if job_data:
            job = json.loads(job_data)
            job['status'] = status
            if output:
                job['output'] = output
            if error:
                job['error'] = error
            
            self.redis.set(job_key, json.dumps(job), ex=86400)
            
            # Publish update
            update = {
                'job_id': job_id,
                'status': status,
                'output': output,
                'error': error
            }
            self.redis.publish('job_updates', json.dumps(update))
    
    def run(self):
        """Main worker loop"""
        print(f"🤖 AI Worker started (LLM: {os.getenv('LLM_PROVIDER', 'groq')})")
        print("Waiting for jobs...")
        
        while True:
            try:
                # Check text queue
                job_data = self.redis.rpop('queue:text')
                if job_data:
                    job = json.loads(job_data)
                    print(f"📝 Processing text job: {job['id']}")
                    
                    self.update_job_status(job['id'], 'processing')
                    output = self.process_text_job(job)
                    self.update_job_status(job['id'], 'completed', output=output)
                    
                    print(f"✓ Text job completed: {job['id']}")
                
                # Check image queue
                job_data = self.redis.rpop('queue:image')
                if job_data:
                    job = json.loads(job_data)
                    print(f"🖼️  Processing image job: {job['id']}")
                    
                    self.update_job_status(job['id'], 'processing')
                    output = self.process_image_job(job)
                    self.update_job_status(job['id'], 'completed', output=output)
                    
                    print(f"✓ Image job completed: {job['id']}")
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"❌ Worker error: {e}")
                if 'job' in locals():
                    self.update_job_status(job['id'], 'failed', error=str(e))
                time.sleep(self.poll_interval)

if __name__ == '__main__':
    worker = Worker()
    worker.run()
