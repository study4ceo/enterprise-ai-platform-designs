# Models Directory

This directory stores downloaded language models.

## Structure

```
models/
├── llama-3.2-1b/           # Model files
│   ├── config.json
│   ├── tokenizer.json
│   └── pytorch_model.bin
├── mistral-7b/
└── ...
```

## Usage

Models are automatically downloaded here when you:
1. Use the API: `POST /api/v1/models/download`
2. Start training with a model_id

## Storage

- Base models: 2-14 GB each
- Fine-tuned models: +100-500 MB (LoRA adapters)

## Notes

- Models are cached from HuggingFace
- Can also manually place models here
- Use symlinks to save space if needed
