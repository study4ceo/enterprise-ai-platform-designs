# Datasets Directory

This directory stores training datasets.

## Supported Formats

### JSON/JSONL
```json
[
  {"text": "Training example 1"},
  {"text": "Training example 2"}
]
```

Or with instruction format:
```json
[
  {
    "instruction": "What is AI?",
    "input": "",
    "output": "AI is artificial intelligence..."
  }
]
```

### CSV
```csv
text
"First example"
"Second example"
```

## Usage

Upload datasets via:
1. API: `POST /api/v1/datasets/upload`
2. Manual copy to this directory

## Storage

- Text datasets: 10 MB - 10 GB
- Preprocessed/tokenized: +50% size

## Best Practices

- Clean data before upload
- Balance classes for classification
- Include validation split
- Use consistent format
