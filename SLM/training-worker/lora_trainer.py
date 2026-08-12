"""
LoRA Trainer - Parameter-efficient fine-tuning using LoRA
"""

import os
import logging
import torch
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from datasets import load_dataset, Dataset
import wandb

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class LoRATrainingConfig:
    """LoRA training configuration"""
    # Model
    model_path: str
    output_dir: str
    
    # LoRA params
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: list = None
    
    # Training params
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 1
    warmup_steps: int = 100
    max_seq_length: int = 2048
    
    # Evaluation
    eval_steps: int = 100
    save_steps: int = 500
    logging_steps: int = 10
    
    # Optimization
    optim: str = "paged_adamw_8bit"
    gradient_checkpointing: bool = True
    fp16: bool = False
    bf16: bool = False
    
    # WandB
    wandb_project: Optional[str] = None
    wandb_run_name: Optional[str] = None


class LoRATrainer:
    """
    LoRA (Low-Rank Adaptation) Trainer.
    Implements parameter-efficient fine-tuning using LoRA adapters.
    """
    
    def __init__(self, config: LoRATrainingConfig):
        """
        Args:
            config: LoRA training configuration
        """
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        logger.info(f"LoRATrainer initialized. Device: {self.device}")
        
        # Setup WandB if enabled
        if config.wandb_project and settings.WANDB_ENABLED:
            wandb.init(
                project=config.wandb_project,
                name=config.wandb_run_name,
                config=config.__dict__
            )
    
    def load_model(self) -> None:
        """Load base model and apply LoRA adapters"""
        logger.info(f"Loading base model from {self.config.model_path}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            # Set padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load base model
            model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
                trust_remote_code=True
            )
            
            # Enable gradient checkpointing for memory efficiency
            if self.config.gradient_checkpointing:
                model.gradient_checkpointing_enable()
            
            # Prepare model for training (freeze base model weights)
            model = prepare_model_for_kbit_training(model)
            
            # Configure LoRA
            target_modules = self.config.target_modules or [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]
            
            lora_config = LoraConfig(
                r=self.config.lora_rank,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=target_modules,
                bias="none",
                task_type=TaskType.CAUSAL_LM
            )
            
            # Apply LoRA adapters
            self.model = get_peft_model(model, lora_config)
            
            # Print trainable parameters
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_percent = 100 * trainable_params / total_params
            
            logger.info(f"Trainable params: {trainable_params:,} ({trainable_percent:.2f}%)")
            logger.info(f"Total params: {total_params:,}")
            
            self.model.print_trainable_parameters()
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise
    
    def prepare_dataset(
        self,
        dataset_path: str,
        train_split: str = "train",
        eval_split: Optional[str] = "validation"
    ) -> tuple:
        """
        Load and prepare dataset for training.
        
        Args:
            dataset_path: Path to dataset file or HuggingFace dataset name
            train_split: Name of training split
            eval_split: Name of evaluation split
        
        Returns:
            Tuple of (train_dataset, eval_dataset)
        """
        logger.info(f"Loading dataset from {dataset_path}")
        
        try:
            # Load dataset
            if os.path.exists(dataset_path):
                # Load from local file
                if dataset_path.endswith('.json') or dataset_path.endswith('.jsonl'):
                    dataset = load_dataset('json', data_files=dataset_path)
                elif dataset_path.endswith('.csv'):
                    dataset = load_dataset('csv', data_files=dataset_path)
                else:
                    dataset = load_dataset(dataset_path)
            else:
                # Load from HuggingFace
                dataset = load_dataset(dataset_path)
            
            # Get splits
            if train_split in dataset:
                train_data = dataset[train_split]
            else:
                train_data = dataset['train'] if 'train' in dataset else list(dataset.values())[0]
            
            eval_data = None
            if eval_split and eval_split in dataset:
                eval_data = dataset[eval_split]
            elif 'validation' in dataset:
                eval_data = dataset['validation']
            elif 'test' in dataset:
                eval_data = dataset['test']
            else:
                # Create validation split from training data
                logger.info("Creating 10% validation split from training data")
                split_data = train_data.train_test_split(test_size=0.1, seed=42)
                train_data = split_data['train']
                eval_data = split_data['test']
            
            # Tokenize datasets
            def tokenize_function(examples):
                # Assume dataset has 'text' or 'prompt'+'completion' columns
                if 'text' in examples:
                    texts = examples['text']
                elif 'prompt' in examples and 'completion' in examples:
                    texts = [f"{p}\n{c}" for p, c in zip(examples['prompt'], examples['completion'])]
                else:
                    raise ValueError("Dataset must have 'text' or 'prompt'+'completion' columns")
                
                # Tokenize
                tokenized = self.tokenizer(
                    texts,
                    truncation=True,
                    max_length=self.config.max_seq_length,
                    padding=False,
                    return_tensors=None
                )
                
                # Add labels (for causal LM, labels = input_ids)
                tokenized["labels"] = tokenized["input_ids"].copy()
                
                return tokenized
            
            train_dataset = train_data.map(
                tokenize_function,
                batched=True,
                remove_columns=train_data.column_names,
                desc="Tokenizing training data"
            )
            
            eval_dataset = None
            if eval_data:
                eval_dataset = eval_data.map(
                    tokenize_function,
                    batched=True,
                    remove_columns=eval_data.column_names,
                    desc="Tokenizing evaluation data"
                )
            
            logger.info(f"Training samples: {len(train_dataset)}")
            if eval_dataset:
                logger.info(f"Evaluation samples: {len(eval_dataset)}")
            
            return train_dataset, eval_dataset
        
        except Exception as e:
            logger.error(f"Failed to prepare dataset: {e}", exc_info=True)
            raise
    
    def train(
        self,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None,
        callbacks: list = None
    ) -> Dict[str, Any]:
        """
        Train the model with LoRA adapters.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset (optional)
            callbacks: List of trainer callbacks
        
        Returns:
            Training metrics dictionary
        """
        logger.info("Starting LoRA training...")
        start_time = datetime.now()
        
        try:
            # Setup training arguments
            training_args = TrainingArguments(
                output_dir=self.config.output_dir,
                num_train_epochs=self.config.num_epochs,
                per_device_train_batch_size=self.config.batch_size,
                per_device_eval_batch_size=self.config.batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                warmup_steps=self.config.warmup_steps,
                logging_steps=self.config.logging_steps,
                save_steps=self.config.save_steps,
                eval_steps=self.config.eval_steps if eval_dataset else None,
                evaluation_strategy="steps" if eval_dataset else "no",
                save_strategy="steps",
                load_best_model_at_end=True if eval_dataset else False,
                metric_for_best_model="eval_loss" if eval_dataset else None,
                greater_is_better=False,
                fp16=self.config.fp16,
                bf16=self.config.bf16,
                optim=self.config.optim,
                gradient_checkpointing=self.config.gradient_checkpointing,
                report_to="wandb" if settings.WANDB_ENABLED else "none",
                save_total_limit=3,
                logging_dir=os.path.join(self.config.output_dir, "logs"),
                disable_tqdm=False,
                remove_unused_columns=False,
            )
            
            # Data collator for language modeling
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            # Initialize callbacks
            callback_list = callbacks or []
            if eval_dataset:
                # Add early stopping
                callback_list.append(
                    EarlyStoppingCallback(early_stopping_patience=3)
                )
            
            # Create trainer
            self.trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                callbacks=callback_list
            )
            
            # Train
            train_result = self.trainer.train()
            
            # Save final model
            self.trainer.save_model()
            self.tokenizer.save_pretrained(self.config.output_dir)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Extract metrics
            metrics = {
                "train_loss": train_result.metrics.get("train_loss"),
                "train_samples_per_second": train_result.metrics.get("train_samples_per_second"),
                "train_steps_per_second": train_result.metrics.get("train_steps_per_second"),
                "total_steps": train_result.global_step,
                "duration_seconds": duration,
                "duration_minutes": duration / 60
            }
            
            if eval_dataset:
                eval_result = self.trainer.evaluate()
                metrics.update({
                    "eval_loss": eval_result.get("eval_loss"),
                    "eval_perplexity": torch.exp(torch.tensor(eval_result.get("eval_loss", 0))).item()
                })
            
            logger.info(f"Training completed in {duration/60:.2f} minutes")
            logger.info(f"Final metrics: {metrics}")
            
            return metrics
        
        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            raise
    
    def save_checkpoint(self, checkpoint_dir: str) -> str:
        """
        Save training checkpoint.
        
        Args:
            checkpoint_dir: Directory to save checkpoint
        
        Returns:
            Path to saved checkpoint
        """
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        self.trainer.save_model(checkpoint_dir)
        self.tokenizer.save_pretrained(checkpoint_dir)
        
        logger.info(f"Checkpoint saved to {checkpoint_dir}")
        return checkpoint_dir
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current GPU memory statistics"""
        if self.device == "cuda":
            return {
                "allocated_mb": torch.cuda.memory_allocated() // (1024 * 1024),
                "reserved_mb": torch.cuda.memory_reserved() // (1024 * 1024),
                "max_allocated_mb": torch.cuda.max_memory_allocated() // (1024 * 1024)
            }
        return {}
    
    def cleanup(self):
        """Cleanup resources"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if self.trainer:
            del self.trainer
        
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        if settings.WANDB_ENABLED:
            wandb.finish()
        
        logger.info("Resources cleaned up")
