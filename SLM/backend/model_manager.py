"""
Model Manager - Handle model loading, caching, and inference
"""

import os
import logging
import torch
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
from functools import lru_cache

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TextIteratorStreamer,
    GenerationConfig
)
from peft import PeftModel, PeftConfig
import psutil
from threading import Thread

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class LoadedModel:
    """Container for a loaded model"""
    model_id: str
    model: Any
    tokenizer: Any
    quantization: Optional[str]
    load_time: datetime
    memory_mb: int
    device: str
    is_peft: bool = False


class ModelManager:
    """
    Manages model loading, caching, and inference.
    Implements LRU cache to keep hot models in memory.
    """
    
    def __init__(self, max_models: int = None):
        """
        Args:
            max_models: Maximum number of models to keep in memory (default from settings)
        """
        self.max_models = max_models or settings.MAX_LOADED_MODELS
        self.loaded_models: Dict[str, LoadedModel] = {}
        self.access_times: Dict[str, datetime] = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"ModelManager initialized. Device: {self.device}")
        if self.device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    def _get_available_memory_mb(self) -> int:
        """Get available system memory in MB"""
        if self.device == "cuda":
            return (torch.cuda.get_device_properties(0).total_memory - 
                   torch.cuda.memory_allocated(0)) // (1024 * 1024)
        else:
            return psutil.virtual_memory().available // (1024 * 1024)
    
    def _estimate_model_size_mb(self, parameters: int, quantization: Optional[str] = None) -> int:
        """Estimate model size in memory"""
        if quantization == "int4":
            bytes_per_param = 0.5
        elif quantization == "int8":
            bytes_per_param = 1
        elif quantization == "fp16":
            bytes_per_param = 2
        else:  # fp32
            bytes_per_param = 4
        
        # Add 20% overhead for buffers, activations, etc.
        return int((parameters * bytes_per_param * 1.2) / (1024 * 1024))
    
    def _evict_lru_model(self):
        """Evict least recently used model from cache"""
        if not self.loaded_models:
            return
        
        # Find LRU model
        lru_model_id = min(self.access_times.items(), key=lambda x: x[1])[0]
        
        logger.info(f"Evicting LRU model: {lru_model_id}")
        loaded_model = self.loaded_models[lru_model_id]
        
        # Free memory
        del loaded_model.model
        del loaded_model.tokenizer
        del self.loaded_models[lru_model_id]
        del self.access_times[lru_model_id]
        
        # Clear CUDA cache if on GPU
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info(f"Model {lru_model_id} evicted. Memory freed: {loaded_model.memory_mb} MB")
    
    def _get_quantization_config(self, quantization: Optional[str]) -> Optional[BitsAndBytesConfig]:
        """Get quantization configuration"""
        if quantization == "int4":
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
        elif quantization == "int8":
            return BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0,
            )
        return None
    
    async def load_model(
        self, 
        model_id: str, 
        local_path: str,
        quantization: Optional[str] = None,
        is_peft: bool = False,
        base_model_path: Optional[str] = None
    ) -> LoadedModel:
        """
        Load a model into memory.
        
        Args:
            model_id: Unique model identifier
            local_path: Path to model weights
            quantization: Quantization type (int4, int8, fp16, None)
            is_peft: Whether this is a PEFT (LoRA) model
            base_model_path: Path to base model (required for PEFT)
        
        Returns:
            LoadedModel instance
        """
        # Check if already loaded
        if model_id in self.loaded_models:
            logger.info(f"Model {model_id} already loaded")
            self.access_times[model_id] = datetime.now()
            return self.loaded_models[model_id]
        
        logger.info(f"Loading model {model_id} from {local_path}")
        start_time = datetime.now()
        
        try:
            # Prepare quantization config
            quant_config = self._get_quantization_config(quantization)
            
            # Load model
            if is_peft:
                # Load PEFT model (LoRA adapter)
                logger.info(f"Loading PEFT model with base model: {base_model_path}")
                
                # Load base model first
                base_model = AutoModelForCausalLM.from_pretrained(
                    base_model_path,
                    quantization_config=quant_config,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if quantization == "fp16" else torch.float32,
                    trust_remote_code=True
                )
                
                # Load PEFT adapter
                model = PeftModel.from_pretrained(base_model, local_path)
                tokenizer = AutoTokenizer.from_pretrained(base_model_path)
            else:
                # Load standard model
                model = AutoModelForCausalLM.from_pretrained(
                    local_path,
                    quantization_config=quant_config,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if quantization == "fp16" else torch.float32,
                    trust_remote_code=True
                )
                tokenizer = AutoTokenizer.from_pretrained(local_path)
            
            # Set padding token if not set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Move to device if CPU
            if self.device == "cpu":
                model = model.to(self.device)
            
            # Estimate memory usage
            if self.device == "cuda":
                memory_mb = torch.cuda.memory_allocated(0) // (1024 * 1024)
            else:
                # Rough estimate for CPU
                param_count = sum(p.numel() for p in model.parameters())
                memory_mb = self._estimate_model_size_mb(param_count, quantization)
            
            load_time = (datetime.now() - start_time).total_seconds()
            
            # Create loaded model object
            loaded = LoadedModel(
                model_id=model_id,
                model=model,
                tokenizer=tokenizer,
                quantization=quantization,
                load_time=datetime.now(),
                memory_mb=memory_mb,
                device=self.device,
                is_peft=is_peft
            )
            
            # Evict LRU models if needed
            while len(self.loaded_models) >= self.max_models:
                self._evict_lru_model()
            
            # Cache the model
            self.loaded_models[model_id] = loaded
            self.access_times[model_id] = datetime.now()
            
            logger.info(
                f"Model {model_id} loaded successfully in {load_time:.2f}s. "
                f"Memory: {memory_mb} MB"
            )
            
            return loaded
        
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}", exc_info=True)
            raise
    
    async def unload_model(self, model_id: str):
        """Unload a specific model from memory"""
        if model_id not in self.loaded_models:
            logger.warning(f"Model {model_id} not loaded")
            return
        
        loaded = self.loaded_models[model_id]
        
        # Free memory
        del loaded.model
        del loaded.tokenizer
        del self.loaded_models[model_id]
        del self.access_times[model_id]
        
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info(f"Model {model_id} unloaded")
    
    def get_loaded_models(self) -> List[Dict[str, Any]]:
        """Get list of currently loaded models"""
        return [
            {
                "model_id": loaded.model_id,
                "quantization": loaded.quantization,
                "memory_mb": loaded.memory_mb,
                "device": loaded.device,
                "is_peft": loaded.is_peft,
                "load_time": loaded.load_time.isoformat()
            }
            for loaded in self.loaded_models.values()
        ]
    
    async def generate(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        stop_sequences: Optional[List[str]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text using a loaded model.
        
        Args:
            model_id: Model identifier
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: List of stop sequences
            stream: Whether to stream output
        
        Returns:
            Dictionary with generated text and metadata
        """
        # Get model (load if not in cache)
        if model_id not in self.loaded_models:
            raise ValueError(f"Model {model_id} not loaded")
        
        loaded = self.loaded_models[model_id]
        self.access_times[model_id] = datetime.now()
        
        start_time = datetime.now()
        
        try:
            # Tokenize input
            inputs = loaded.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=settings.DEFAULT_MAX_SEQ_LENGTH
            )
            
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            input_length = inputs["input_ids"].shape[1]
            
            # Prepare generation config
            gen_config = GenerationConfig(
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=temperature > 0,
                pad_token_id=loaded.tokenizer.pad_token_id,
                eos_token_id=loaded.tokenizer.eos_token_id,
            )
            
            # Generate
            with torch.no_grad():
                outputs = loaded.model.generate(
                    **inputs,
                    generation_config=gen_config
                )
            
            # Decode output
            generated_text = loaded.tokenizer.decode(
                outputs[0][input_length:],
                skip_special_tokens=True
            )
            
            # Apply stop sequences
            if stop_sequences:
                for stop in stop_sequences:
                    if stop in generated_text:
                        generated_text = generated_text[:generated_text.index(stop)]
            
            # Calculate metrics
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            tokens_generated = outputs.shape[1] - input_length
            tokens_per_second = tokens_generated * 1000 / latency_ms if latency_ms > 0 else 0
            
            return {
                "generated_text": generated_text,
                "prompt_tokens": input_length,
                "generated_tokens": tokens_generated,
                "total_tokens": outputs.shape[1],
                "latency_ms": latency_ms,
                "tokens_per_second": tokens_per_second
            }
        
        except Exception as e:
            logger.error(f"Generation failed for model {model_id}: {e}", exc_info=True)
            raise
    
    async def chat(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Chat completion using conversation history.
        
        Args:
            model_id: Model identifier
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stream: Whether to stream output
        
        Returns:
            Dictionary with response and metadata
        """
        # Get model
        if model_id not in self.loaded_models:
            raise ValueError(f"Model {model_id} not loaded")
        
        loaded = self.loaded_models[model_id]
        
        # Format conversation
        # Most chat models use specific formats, we'll use a generic one
        conversation = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                conversation += f"System: {content}\n\n"
            elif role == "user":
                conversation += f"User: {content}\n\n"
            elif role == "assistant":
                conversation += f"Assistant: {content}\n\n"
        
        conversation += "Assistant: "
        
        # Use generate method
        result = await self.generate(
            model_id=model_id,
            prompt=conversation,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=stream
        )
        
        return {
            "response": result["generated_text"],
            "prompt_tokens": result["prompt_tokens"],
            "response_tokens": result["generated_tokens"],
            "total_tokens": result["total_tokens"],
            "latency_ms": result["latency_ms"],
            "tokens_per_second": result["tokens_per_second"]
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        stats = {
            "loaded_models": len(self.loaded_models),
            "max_models": self.max_models,
            "device": self.device
        }
        
        if self.device == "cuda":
            stats.update({
                "gpu_memory_allocated_mb": torch.cuda.memory_allocated(0) // (1024 * 1024),
                "gpu_memory_reserved_mb": torch.cuda.memory_reserved(0) // (1024 * 1024),
                "gpu_memory_total_mb": torch.cuda.get_device_properties(0).total_memory // (1024 * 1024),
            })
        else:
            mem = psutil.virtual_memory()
            stats.update({
                "system_memory_used_mb": mem.used // (1024 * 1024),
                "system_memory_total_mb": mem.total // (1024 * 1024),
                "system_memory_percent": mem.percent
            })
        
        return stats


# Global model manager instance
model_manager = ModelManager()
