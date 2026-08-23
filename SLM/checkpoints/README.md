# Checkpoints Directory

This directory stores training checkpoints and fine-tuned models.

## Structure

```
checkpoints/
├── job-abc12345/          # Training job ID
│   ├── checkpoint-500/    # Step checkpoints
│   │   ├── adapter_config.json
│   │   ├── adapter_model.bin
│   │   └── optimizer.pt
│   ├── checkpoint-1000/
│   └── final/             # Final trained model
│       ├── adapter_config.json
│       └── adapter_model.bin
├── job-def67890/
└── ...
```

## Contents

Each checkpoint contains:
- **adapter_model.bin** - LoRA adapter weights (~100-500 MB)
- **adapter_config.json** - LoRA configuration
- **optimizer.pt** - Optimizer state (for resuming)
- **trainer_state.json** - Training state
- **training_args.bin** - Training arguments

## Usage

Checkpoints are automatically created:
- Every N steps (configured in training)
- At end of each epoch
- When training completes

## Recovery

To resume training from checkpoint:
```python
trainer.train(resume_from_checkpoint="checkpoints/job-xxx/checkpoint-1000")
```

## Storage

- Per checkpoint: 200 MB - 1 GB
- Total: 1-10 GB per training job
- Auto-cleanup: Keeps last 3 checkpoints

## Notes

- Only LoRA adapters stored (not full model)
- Need base model + adapter to use
- Can be uploaded to MinIO for backup
