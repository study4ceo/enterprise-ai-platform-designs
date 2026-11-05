# Vector Databases: Pinecone & ChromaDB Architecture

## Overview
Comprehensive guide to vector databases for embeddings storage, semantic search, RAG applications, and ML feature stores.

---

## Vector Database Fundamentals

### What are Vector Embeddings?
- High-dimensional numerical representations of data (text, images, audio)
- Capture semantic meaning
- Enable similarity search
- Typical dimensions: 384, 768, 1536, 3072

### Why Vector Databases?
Traditional databases aren't optimized for:
- High-dimensional vector similarity search
- Approximate nearest neighbor (ANN) queries
- Real-time embedding retrieval at scale

---

## Pinecone (Managed Cloud Service)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Application Layer                                           │
│  - Web Apps                                                  │
│  - Lambda Functions                                          │
│  - ML Services                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Embedding Generation                                        │
│  - Bedrock Titan Embeddings                                  │
│  - OpenAI Embeddings                                         │
│  - SageMaker Custom Models                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Pinecone Index (Managed)                                    │
│  - Serverless (auto-scaling)                                 │
│  - Pod-based (dedicated resources)                           │
│  - Multiple replicas                                         │
│  - Automatic sharding                                        │
└─────────────────────────────────────────────────────────────┘
```

### Setup & Configuration

```python
from pinecone import Pinecone, ServerlessSpec
import os

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Create serverless index (recommended for most use cases)
pc.create_index(
    name="knowledge-base",
    dimension=1536,  # OpenAI/Titan embedding dimension
    metric="cosine",  # cosine, euclidean, or dotproduct
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

# Or create pod-based index (for consistent performance)
pc.create_index(
    name="high-performance-index",
    dimension=1536,
    metric="cosine",
    spec=PodSpec(
        environment="us-east-1-aws",
        pod_type="p1.x1",  # p1.x1, p1.x2, p2.x1, s1.x1
        pods=2,
        replicas=2
    )
)

# Connect to index
index = pc.Index("knowledge-base")

# Get index stats
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces']}")
```

### Basic Operations

#### 1. Upsert (Insert/Update)
```python
from langchain_community.embeddings import BedrockEmbeddings
import uuid

embeddings_model = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1"
)

# Prepare data
documents = [
    {
        "id": str(uuid.uuid4()),
        "text": "AWS Lambda is a serverless compute service.",
        "metadata": {
            "source": "aws-docs",
            "category": "compute",
            "timestamp": "2024-01-01"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "text": "Amazon S3 provides object storage.",
        "metadata": {
            "source": "aws-docs",
            "category": "storage",
            "timestamp": "2024-01-01"
        }
    }
]

# Generate embeddings and upsert
vectors = []
for doc in documents:
    embedding = embeddings_model.embed_query(doc['text'])
    vectors.append({
        "id": doc['id'],
        "values": embedding,
        "metadata": {
            **doc['metadata'],
            "text": doc['text']  # Store text in metadata
        }
    })

# Batch upsert
index.upsert(vectors=vectors, namespace="aws-knowledge")

# Or upsert in batches for large datasets
from pinecone import UpsertBatch

batch_size = 100
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i+batch_size]
    index.upsert(vectors=batch, namespace="aws-knowledge")
```

#### 2. Query (Semantic Search)
```python
# Generate query embedding
query = "Tell me about serverless computing"
query_embedding = embeddings_model.embed_query(query)

# Search
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    namespace="aws-knowledge",
    filter={
        "category": {"$eq": "compute"},
        "timestamp": {"$gte": "2024-01-01"}
    }
)

# Process results
for match in results['matches']:
    print(f"Score: {match['score']:.4f}")
    print(f"Text: {match['metadata']['text']}")
    print(f"Source: {match['metadata']['source']}")
    print("---")
```

#### 3. Metadata Filtering
```python
# Supported operators
filters = {
    # Equality
    "category": {"$eq": "compute"},
    
    # Inequality
    "priority": {"$ne": "low"},
    
    # Comparison
    "score": {"$gte": 0.8},
    "timestamp": {"$lte": "2024-12-31"},
    
    # In/Not In
    "status": {"$in": ["active", "pending"]},
    "type": {"$nin": ["archived", "deleted"]},
    
    # Logical operators
    "$and": [
        {"category": {"$eq": "compute"}},
        {"score": {"$gte": 0.8}}
    ],
    "$or": [
        {"priority": {"$eq": "high"}},
        {"urgent": {"$eq": True}}
    ]
}

results = index.query(
    vector=query_embedding,
    top_k=10,
    filter=filters,
    include_metadata=True
)
```

#### 4. Fetch by ID
```python
# Fetch specific vectors
vectors = index.fetch(
    ids=["id1", "id2", "id3"],
    namespace="aws-knowledge"
)

for id, vector_data in vectors['vectors'].items():
    print(f"ID: {id}")
    print(f"Metadata: {vector_data['metadata']}")
```

#### 5. Delete
```python
# Delete by IDs
index.delete(ids=["id1", "id2"], namespace="aws-knowledge")

# Delete by filter
index.delete(
    filter={"category": {"$eq": "outdated"}},
    namespace="aws-knowledge"
)

# Delete entire namespace
index.delete(delete_all=True, namespace="aws-knowledge")

# Delete index (careful!)
pc.delete_index("knowledge-base")
```

### Advanced Patterns

#### Hybrid Search (Vector + Keyword)
```python
from pinecone_text.sparse import BM25Encoder

# Create sparse encoder
bm25 = BM25Encoder()
bm25.fit(documents)  # Fit on your corpus

# Generate sparse and dense embeddings
query = "serverless functions"
dense_vector = embeddings_model.embed_query(query)
sparse_vector = bm25.encode_queries(query)

# Hybrid search
results = index.query(
    vector=dense_vector,
    sparse_vector=sparse_vector,
    top_k=10,
    include_metadata=True
)
```

#### Multi-Tenancy with Namespaces
```python
class MultiTenantVectorStore:
    
    def __init__(self, index_name: str):
        self.index = pc.Index(index_name)
    
    def upsert_tenant_data(self, tenant_id: str, documents: list):
        """Store data in tenant-specific namespace."""
        vectors = []
        for doc in documents:
            embedding = embeddings_model.embed_query(doc['text'])
            vectors.append({
                "id": doc['id'],
                "values": embedding,
                "metadata": {
                    **doc['metadata'],
                    "tenant_id": tenant_id,
                    "text": doc['text']
                }
            })
        
        self.index.upsert(
            vectors=vectors,
            namespace=f"tenant-{tenant_id}"
        )
    
    def query_tenant_data(self, tenant_id: str, query: str, top_k: int = 5):
        """Query within tenant namespace."""
        query_embedding = embeddings_model.embed_query(query)
        
        return self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=f"tenant-{tenant_id}",
            include_metadata=True
        )
```

#### Versioning Strategy
```python
def version_aware_upsert(index, doc_id: str, text: str, version: str):
    """Store versioned documents."""
    embedding = embeddings_model.embed_query(text)
    
    # Create versioned ID
    versioned_id = f"{doc_id}:v{version}"
    
    index.upsert(vectors=[{
        "id": versioned_id,
        "values": embedding,
        "metadata": {
            "doc_id": doc_id,
            "version": version,
            "text": text,
            "is_latest": True,
            "timestamp": datetime.now().isoformat()
        }
    }])
    
    # Mark previous versions as not latest
    index.update(
        id=doc_id,
        set_metadata={"is_latest": False}
    )
```

---

## ChromaDB (Self-Hosted / Embedded)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  ChromaDB Deployment Options                                 │
│                                                              │
│  1. In-Memory (Development)                                  │
│  2. Persistent Local (SQLite + DuckDB)                       │
│  3. Client-Server (Docker/ECS)                               │
│  4. Distributed (Kubernetes)                                 │
└─────────────────────────────────────────────────────────────┘
```

### Setup & Configuration

#### 1. In-Memory (Development)
```python
import chromadb

# Create in-memory client
client = chromadb.Client()

# Create collection
collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # cosine, l2, ip
)
```

#### 2. Persistent Local
```python
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data"
))

collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)
```

#### 3. Client-Server Mode
```python
# Start server (Docker)
# docker run -p 8000:8000 chromadb/chroma

# Connect client
client = chromadb.HttpClient(
    host="localhost",
    port=8000
)

collection = client.get_or_create_collection("documents")
```

#### 4. AWS ECS Deployment
```python
# Dockerfile for ChromaDB
"""
FROM chromadb/chroma:latest

# Add custom configuration
COPY chroma_config.yaml /chroma/config.yaml

EXPOSE 8000

CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# ECS Task Definition
task_definition = {
    "family": "chromadb",
    "containerDefinitions": [{
        "name": "chromadb",
        "image": "your-ecr-repo/chromadb:latest",
        "memory": 4096,
        "cpu": 2048,
        "portMappings": [{
            "containerPort": 8000,
            "protocol": "tcp"
        }],
        "environment": [{
            "name": "CHROMA_SERVER_AUTH_CREDENTIALS",
            "value": "stored-in-secrets-manager"
        }],
        "mountPoints": [{
            "sourceVolume": "chroma-data",
            "containerPath": "/chroma/data"
        }]
    }],
    "volumes": [{
        "name": "chroma-data",
        "efsVolumeConfiguration": {
            "fileSystemId": "fs-xxxxx",  # EFS for persistence
            "transitEncryption": "ENABLED"
        }
    }]
}
```

### Basic Operations

#### 1. Add Documents
```python
from langchain_community.embeddings import BedrockEmbeddings

embeddings_model = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1"
)

documents = [
    "AWS Lambda is a serverless compute service",
    "Amazon S3 provides object storage",
    "Amazon DynamoDB is a NoSQL database"
]

metadatas = [
    {"source": "aws-docs", "category": "compute"},
    {"source": "aws-docs", "category": "storage"},
    {"source": "aws-docs", "category": "database"}
]

ids = ["doc1", "doc2", "doc3"]

# Generate embeddings
embeddings = [
    embeddings_model.embed_query(doc) 
    for doc in documents
]

# Add to collection
collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)
```

#### 2. Query
```python
# Query by text (auto-generates embedding)
results = collection.query(
    query_texts=["Tell me about serverless computing"],
    n_results=5,
    where={"category": "compute"},  # Optional filter
    include=["documents", "metadatas", "distances"]
)

print(results['documents'])
print(results['metadatas'])
print(results['distances'])

# Query by embedding
query_embedding = embeddings_model.embed_query("serverless functions")
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)
```

#### 3. Update
```python
# Update documents
collection.update(
    ids=["doc1"],
    documents=["Updated text for AWS Lambda"],
    metadatas=[{"source": "aws-docs", "category": "compute", "updated": "2024-01-15"}]
)

# Update only metadata
collection.update(
    ids=["doc1"],
    metadatas=[{"last_accessed": "2024-01-15"}]
)
```

#### 4. Delete
```python
# Delete by IDs
collection.delete(ids=["doc1", "doc2"])

# Delete by filter
collection.delete(where={"category": "outdated"})

# Delete entire collection
client.delete_collection(name="documents")
```

#### 5. Get Documents
```python
# Get specific documents
docs = collection.get(
    ids=["doc1", "doc2"],
    include=["documents", "metadatas", "embeddings"]
)

# Get with filter
docs = collection.get(
    where={"category": "compute"},
    limit=10
)

# Get all
all_docs = collection.get()
```

### Advanced Features

#### Custom Embedding Functions
```python
from chromadb.utils import embedding_functions

# Use custom embedding function
bedrock_ef = embedding_functions.BedrockEmbeddingFunction(
    model_name="amazon.titan-embed-text-v1"
)

collection = client.create_collection(
    name="custom-embeddings",
    embedding_function=bedrock_ef
)

# Now embeddings are generated automatically
collection.add(
    documents=["Text to embed"],
    ids=["id1"]
)
# No need to pass embeddings parameter
```

#### Distance Metrics
```python
# Cosine similarity (default)
cosine_collection = client.create_collection(
    name="cosine",
    metadata={"hnsw:space": "cosine"}
)

# L2 (Euclidean) distance
l2_collection = client.create_collection(
    name="l2",
    metadata={"hnsw:space": "l2"}
)

# Inner product
ip_collection = client.create_collection(
    name="ip",
    metadata={"hnsw:space": "ip"}
)
```

#### Filtering Operators
```python
# Equality
results = collection.query(
    query_texts=["query"],
    where={"category": "compute"}
)

# Not equal
results = collection.query(
    query_texts=["query"],
    where={"category": {"$ne": "deprecated"}}
)

# In / Not In
results = collection.query(
    query_texts=["query"],
    where={"category": {"$in": ["compute", "storage"]}}
)

# Greater than / Less than
results = collection.query(
    query_texts=["query"],
    where={"priority": {"$gte": 5}}
)

# And / Or
results = collection.query(
    query_texts=["query"],
    where={
        "$and": [
            {"category": "compute"},
            {"priority": {"$gte": 5}}
        ]
    }
)
```

---

## Pinecone vs ChromaDB Comparison

| Feature | Pinecone | ChromaDB |
|---------|----------|----------|
| **Hosting** | Fully managed cloud | Self-hosted or cloud |
| **Pricing** | Pay-per-use | Free (self-hosted) |
| **Scalability** | Auto-scaling, unlimited | Manual scaling |
| **Latency** | <100ms (serverless) | Depends on deployment |
| **Persistence** | Built-in | File-based or cloud storage |
| **Multi-tenancy** | Namespaces | Collections |
| **Metadata Filtering** | Rich filtering | Basic filtering |
| **Hybrid Search** | Native support | Requires custom implementation |
| **Setup Complexity** | Minimal | Moderate to high |
| **Best For** | Production, scale | Development, cost-sensitive |

---

## Integration with LangChain

### Pinecone + LangChain
```python
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import S3FileLoader

# Load documents
loader = S3FileLoader("my-bucket", "documents/report.pdf")
documents = loader.load()

# Split text
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(documents)

# Create embeddings
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")

# Create vector store
vectorstore = PineconeVectorStore.from_documents(
    documents=splits,
    embedding=embeddings,
    index_name="knowledge-base",
    namespace="documents"
)

# Use as retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# Query
docs = retriever.get_relevant_documents("What are the key findings?")
```

### ChromaDB + LangChain
```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Create embeddings
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")

# Load and split documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(documents)

# Create vector store
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name="documents"
)

# Use as retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Query
docs = retriever.get_relevant_documents("Tell me about AWS services")
```

---

## Production Architecture

### Complete RAG System with Pinecone
```
┌─────────────────────────────────────────────────────────────┐
│  User Request                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  API Gateway + Lambda                                        │
│  - Rate limiting                                             │
│  - Authentication                                            │
│  - Request validation                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Query Embedding (Bedrock Titan)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Vector Search (Pinecone)                                    │
│  - Similarity search                                         │
│  - Metadata filtering                                        │
│  - Namespace isolation                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Context Assembly                                            │
│  - Reranking (optional)                                      │
│  - Context window management                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LLM Generation (Bedrock Claude)                             │
│  - Prompt engineering                                        │
│  - Response synthesis                                        │
│  - Citation generation                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Response + Citations                                        │
└─────────────────────────────────────────────────────────────┘
```

### Performance Optimization

#### 1. Caching Layer
```python
import redis
import hashlib
import json

class CachedVectorSearch:
    
    def __init__(self, index, embeddings_model, redis_client):
        self.index = index
        self.embeddings_model = embeddings_model
        self.cache = redis_client
    
    def search(self, query: str, top_k: int = 5, ttl: int = 3600):
        """Search with caching."""
        
        # Generate cache key
        cache_key = hashlib.md5(
            f"{query}:{top_k}".encode()
        ).hexdigest()
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Generate embedding and search
        embedding = self.embeddings_model.embed_query(query)
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Cache results
        self.cache.setex(
            cache_key,
            ttl,
            json.dumps(results['matches'], default=str)
        )
        
        return results['matches']
```

#### 2. Batch Processing
```python
def batch_embed_and_upsert(documents: list, batch_size: int = 100):
    """Efficiently process large document sets."""
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        
        # Batch generate embeddings
        texts = [doc['text'] for doc in batch]
        embeddings = embeddings_model.embed_documents(texts)
        
        # Prepare vectors
        vectors = []
        for doc, embedding in zip(batch, embeddings):
            vectors.append({
                "id": doc['id'],
                "values": embedding,
                "metadata": doc['metadata']
            })
        
        # Batch upsert
        index.upsert(vectors=vectors)
        
        print(f"Processed {i+len(batch)}/{len(documents)}")
```

#### 3. Monitoring
```python
def monitor_vector_operations():
    """Monitor Pinecone operations with CloudWatch."""
    
    cloudwatch = boto3.client('cloudwatch')
    
    # Track query latency
    import time
    start = time.time()
    results = index.query(...)
    latency = time.time() - start
    
    cloudwatch.put_metric_data(
        Namespace='VectorDB',
        MetricData=[{
            'MetricName': 'QueryLatency',
            'Value': latency,
            'Unit': 'Seconds'
        }]
    )
    
    # Track result quality
    cloudwatch.put_metric_data(
        Namespace='VectorDB',
        MetricData=[{
            'MetricName': 'TopResultScore',
            'Value': results['matches'][0]['score'],
            'Unit': 'None'
        }]
    )
```

---

## Cost Optimization

### Pinecone
```python
# Use serverless for variable workloads
# Pay only for operations and storage

# Estimate costs
def estimate_pinecone_cost(
    num_vectors: int,
    dimension: int,
    queries_per_month: int,
    writes_per_month: int
):
    """Estimate monthly Pinecone costs."""
    
    # Storage: ~$0.096/GB/month
    gb_storage = (num_vectors * dimension * 4) / (1024**3)  # 4 bytes per float
    storage_cost = gb_storage * 0.096
    
    # Operations (serverless)
    # Read units: $0.40 per million
    # Write units: $2.00 per million
    read_cost = (queries_per_month / 1_000_000) * 0.40
    write_cost = (writes_per_month / 1_000_000) * 2.00
    
    return {
        "storage": storage_cost,
        "reads": read_cost,
        "writes": write_cost,
        "total": storage_cost + read_cost + write_cost
    }

print(estimate_pinecone_cost(1_000_000, 1536, 100_000, 10_000))
```

### ChromaDB
```python
# Self-hosted cost estimation
def estimate_chromadb_cost(
    num_vectors: int,
    dimension: int,
    instance_type: str = "t3.xlarge"
):
    """Estimate monthly self-hosted costs."""
    
    # Storage calculation
    gb_storage = (num_vectors * dimension * 4) / (1024**3)
    ebs_cost = gb_storage * 0.10  # $0.10/GB/month for gp3
    
    # Compute (example for t3.xlarge)
    instance_costs = {
        "t3.xlarge": 149.28,  # $0.1664/hour * 730 hours
        "t3.2xlarge": 298.56,
        "r5.xlarge": 226.92
    }
    compute_cost = instance_costs.get(instance_type, 149.28)
    
    return {
        "storage": ebs_cost,
        "compute": compute_cost,
        "total": ebs_cost + compute_cost
    }
```

---

## Best Practices

### Pinecone
1. ✅ Use serverless for unpredictable workloads
2. ✅ Use namespaces for multi-tenancy
3. ✅ Implement metadata filtering to reduce search space
4. ✅ Cache frequently queried results
5. ✅ Monitor query latency and adjust replicas
6. ✅ Use batch operations for bulk updates
7. ✅ Implement retry logic with exponential backoff

### ChromaDB
1. ✅ Use client-server mode for production
2. ✅ Deploy on ECS/EKS with EFS for persistence
3. ✅ Implement backup strategy
4. ✅ Use collections for logical separation
5. ✅ Monitor resource usage (memory, CPU)
6. ✅ Consider read replicas for high-read workloads
7. ✅ Implement authentication and encryption

### General
1. ✅ Choose embedding dimension wisely (higher ≠ better)
2. ✅ Normalize embeddings for cosine similarity
3. ✅ Store original text in metadata
4. ✅ Implement versioning for documents
5. ✅ Monitor embedding quality over time
6. ✅ Use appropriate distance metrics
7. ✅ Test thoroughly before production
8. ✅ Implement proper error handling
9. ✅ Log all operations for debugging
10. ✅ Plan for disaster recovery

---

## Migration Between Vector DBs

```python
def migrate_pinecone_to_chromadb(
    pinecone_index,
    chroma_collection,
    batch_size: int = 100
):
    """Migrate data from Pinecone to ChromaDB."""
    
    # Fetch all IDs from Pinecone
    stats = pinecone_index.describe_index_stats()
    total_vectors = stats['total_vector_count']
    
    # Fetch and migrate in batches
    processed = 0
    while processed < total_vectors:
        # Fetch batch from Pinecone
        vectors = pinecone_index.fetch(
            ids=[...],  # Get IDs somehow
            include_values=True,
            include_metadata=True
        )
        
        # Prepare for ChromaDB
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for id, data in vectors['vectors'].items():
            ids.append(id)
            embeddings.append(data['values'])
            metadatas.append(data['metadata'])
            documents.append(data['metadata'].get('text', ''))
        
        # Add to ChromaDB
        chroma_collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        processed += len(ids)
        print(f"Migrated {processed}/{total_vectors}")
```
