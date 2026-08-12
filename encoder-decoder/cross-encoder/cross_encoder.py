from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load a cross-encoder model (e.g., MS MARCO fine-tuned)
model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

query = "What is BM25?"
documents = [
    "BM25 is a ranking function used by search engines.",
    "Vector search uses embeddings for semantic similarity.",
    "BM25 was developed in the Okapi system."
]

scores = []
for doc in documents:
    inputs = tokenizer(query, doc, return_tensors="pt", truncation=True)
    with torch.no_grad():
        score = model(**inputs).logits.squeeze().item()
    scores.append((doc, score))

# Sort by score
reranked = sorted(scores, key=lambda x: x[1], reverse=True)
for doc, score in reranked:
    print(f"{score:.4f} -> {doc}")
