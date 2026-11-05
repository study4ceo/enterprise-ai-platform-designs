# Knowledge Base Architecture with AWS & Vector Databases

## Overview
Enterprise knowledge base system leveraging RAG (Retrieval Augmented Generation), vector databases, and AWS services for intelligent document management and question-answering.

---

## Architecture Components

### 1. Document Ingestion Pipeline

```
Documents (PDF, DOCX, TXT, HTML) 
  → S3 Bucket
  → EventBridge Trigger
  → Lambda Processing
  → Document Parsing (Textract/PyPDF)
  → Chunking Strategy
  → Embedding Generation (Bedrock Titan/OpenAI)
  → Vector Storage (Pinecone/ChromaDB/OpenSearch)
  → Metadata Storage (DynamoDB)
```

### 2. Storage Layers

#### Document Storage
- **S3**: Raw documents with versioning
- **DynamoDB**: Metadata, document hierarchy, permissions
- **Aurora/RDS**: Relational data, user preferences

#### Vector Storage Options

**Option A: Pinecone (Managed)**
```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-api-key")
index = pc.Index("knowledge-base")

# Upsert vectors
index.upsert(vectors=[
    {
        "id": "doc-1-chunk-1",
        "values": embedding_vector,  # 1536 dims for OpenAI
        "metadata": {
            "text": chunk_text,
            "doc_id": "doc-1",
            "source": "s3://bucket/file.pdf",
            "page": 1,
            "timestamp": "2024-01-01"
        }
    }
])

# Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    filter={"doc_id": {"$eq": "doc-1"}}
)
```

**Option B: ChromaDB (Self-hosted)**
```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))

collection = client.create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)

# Add documents
collection.add(
    documents=[chunk_text],
    embeddings=[embedding_vector],
    metadatas=[{
        "doc_id": "doc-1",
        "source": "report.pdf",
        "page": 1
    }],
    ids=["doc-1-chunk-1"]
)

# Query
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"doc_id": "doc-1"}
)
```

**Option C: OpenSearch (AWS Native)**
```python
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

client = OpenSearch(
    hosts=[{'host': 'your-opensearch.region.es.amazonaws.com', 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    connection_class=RequestsHttpConnection
)

# Create index with k-NN
index_body = {
    "settings": {
        "index.knn": True
    },
    "mappings": {
        "properties": {
            "embedding": {
                "type": "knn_vector",
                "dimension": 1536,
                "method": {
                    "name": "hnsw",
                    "engine": "nmslib"
                }
            },
            "text": {"type": "text"},
            "metadata": {"type": "object"}
        }
    }
}

# Index document
client.index(
    index="knowledge-base",
    body={
        "embedding": embedding_vector,
        "text": chunk_text,
        "metadata": metadata
    }
)

# k-NN search
query = {
    "size": 5,
    "query": {
        "knn": {
            "embedding": {
                "vector": query_embedding,
                "k": 5
            }
        }
    }
}
results = client.search(index="knowledge-base", body=query)
```

**Option D: pgvector (PostgreSQL Extension)**
```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create table
CREATE TABLE knowledge_chunks (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(255),
    chunk_text TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index
CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Insert
INSERT INTO knowledge_chunks (doc_id, chunk_text, embedding, metadata)
VALUES ('doc-1', 'chunk text', '[0.1, 0.2, ...]', '{"page": 1}');

-- Query
SELECT chunk_text, metadata, 1 - (embedding <=> '[query_vector]') AS similarity
FROM knowledge_chunks
ORDER BY embedding <=> '[query_vector]'
LIMIT 5;
```

### 3. Document Processing Pipeline

#### Lambda Document Processor
```python
import boto3
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings

s3 = boto3.client('s3')
textract = boto3.client('textract')
bedrock = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    # Get document from S3
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Extract text
    if key.endswith('.pdf'):
        response = textract.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        job_id = response['JobId']
        
        # Wait and get result
        result = textract.get_document_text_detection(JobId=job_id)
        text = '\n'.join([
            block['Text'] for block in result['Blocks'] 
            if block['BlockType'] == 'LINE'
        ])
    else:
        obj = s3.get_object(Bucket=bucket, Key=key)
        text = obj['Body'].read().decode('utf-8')
    
    # Chunk text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Generate embeddings
    embeddings = BedrockEmbeddings(
        client=bedrock,
        model_id="amazon.titan-embed-text-v1"
    )
    
    # Store in vector DB
    for i, chunk in enumerate(chunks):
        embedding = embeddings.embed_query(chunk)
        
        # Store in Pinecone/ChromaDB/OpenSearch
        store_vector(
            id=f"{key}-chunk-{i}",
            vector=embedding,
            text=chunk,
            metadata={
                'source': key,
                'bucket': bucket,
                'chunk_index': i
            }
        )
    
    return {'statusCode': 200, 'body': f'Processed {len(chunks)} chunks'}
```

### 4. RAG Query Pipeline

#### Query Flow
```
User Query 
  → Embedding Generation
  → Vector Search (top-k similar chunks)
  → Reranking (optional)
  → Context Assembly
  → LLM Prompt Construction
  → Bedrock/OpenAI Generation
  → Response + Citations
```

#### Implementation with LangChain
```python
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.llms import Bedrock
from langchain.prompts import PromptTemplate

# Initialize components
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1"
)

vectorstore = Pinecone.from_existing_index(
    index_name="knowledge-base",
    embedding=embeddings
)

llm = Bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"max_tokens": 2000}
)

# Custom prompt
prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer with citations:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

# Query
result = qa_chain({"query": "What are the key findings?"})
print(result['result'])
print(f"Sources: {[doc.metadata['source'] for doc in result['source_documents']]}")
```

### 5. Advanced RAG Techniques

#### Hybrid Search (Vector + Keyword)
```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# Vector retriever
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# BM25 keyword retriever
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 10

# Ensemble retriever
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5]
)
```

#### Reranking with Cohere/Bedrock
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

compressor = CohereRerank(model="rerank-english-v2.0")

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 20})
)

# Returns top 5 after reranking 20 candidates
compressed_docs = compression_retriever.get_relevant_documents(
    "What are the revenue figures?"
)
```

#### Parent Document Retrieval
```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# Small chunks for retrieval, large chunks for context
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

store = InMemoryStore()

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)
```

### 6. Knowledge Base AWS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Document Sources                                            │
│  - S3 Uploads                                                │
│  - SharePoint/Confluence (AppFlow)                           │
│  - Email Attachments (SES)                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Ingestion Layer                                             │
│  - EventBridge (S3 events)                                   │
│  - Lambda (orchestration)                                    │
│  - Step Functions (complex workflows)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Processing                                                  │
│  - Textract (PDF/images)                                     │
│  - Comprehend (entity extraction)                            │
│  - Lambda (chunking, embedding)                              │
│  - Bedrock Titan Embeddings                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Storage                                                     │
│  - S3 (raw documents)                                        │
│  - Pinecone/ChromaDB/OpenSearch (vectors)                    │
│  - DynamoDB (metadata, permissions)                          │
│  - RDS pgvector (alternative vector store)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Query Interface                                             │
│  - API Gateway + Lambda                                      │
│  - AppSync (GraphQL)                                         │
│  - ECS/Fargate (LangChain app)                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Response Generation                                         │
│  - Bedrock Claude 3                                          │
│  - LangChain RAG Chain                                       │
│  - Citation tracking                                         │
└─────────────────────────────────────────────────────────────┘
```

### 7. AWS Bedrock Knowledge Base (Managed Service)

```python
import boto3

bedrock_agent = boto3.client('bedrock-agent')

# Create knowledge base
kb_response = bedrock_agent.create_knowledge_base(
    name='enterprise-kb',
    description='Enterprise knowledge base',
    roleArn='arn:aws:iam::123456789:role/BedrockKBRole',
    knowledgeBaseConfiguration={
        'type': 'VECTOR',
        'vectorKnowledgeBaseConfiguration': {
            'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'
        }
    },
    storageConfiguration={
        'type': 'OPENSEARCH_SERVERLESS',
        'opensearchServerlessConfiguration': {
            'collectionArn': 'arn:aws:aoss:us-east-1:123456789:collection/xyz',
            'vectorIndexName': 'knowledge-index',
            'fieldMapping': {
                'vectorField': 'embedding',
                'textField': 'text',
                'metadataField': 'metadata'
            }
        }
    }
)

# Create data source
ds_response = bedrock_agent.create_data_source(
    knowledgeBaseId=kb_response['knowledgeBase']['knowledgeBaseId'],
    name='s3-documents',
    dataSourceConfiguration={
        'type': 'S3',
        's3Configuration': {
            'bucketArn': 'arn:aws:s3:::my-documents'
        }
    }
)

# Start ingestion job
bedrock_agent.start_ingestion_job(
    knowledgeBaseId=kb_id,
    dataSourceId=ds_id
)

# Query knowledge base
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

response = bedrock_agent_runtime.retrieve_and_generate(
    input={'text': 'What are the revenue projections?'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': kb_id,
            'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
        }
    }
)

print(response['output']['text'])
print(response['citations'])
```

### 8. Monitoring & Observability

#### CloudWatch Metrics
- Document processing latency
- Embedding generation time
- Vector search latency
- LLM response time
- Cost per query (token usage)

#### LangSmith Integration
```python
import os
from langsmith import Client

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "knowledge-base-prod"

client = Client()

# Trace queries automatically
# All LangChain operations are logged to LangSmith
result = qa_chain({"query": "example query"})

# Custom logging
with client.trace("custom-operation") as run:
    # Your code
    pass
```

### 9. Cost Optimization

#### Caching Strategy
```python
from langchain.cache import RedisCache
from langchain.globals import set_llm_cache
import redis

# Redis for LLM response caching
redis_client = redis.Redis(host='your-elasticache.amazonaws.com', port=6379)
set_llm_cache(RedisCache(redis_client))

# Semantic caching
from langchain.cache import RedisSemanticCache

set_llm_cache(RedisSemanticCache(
    redis_url="redis://your-elasticache.amazonaws.com:6379",
    embedding=embeddings,
    score_threshold=0.95  # Cache if similarity > 95%
))
```

#### Vector DB Cost Comparison

| Service | Cost Model | Best For |
|---------|-----------|----------|
| Pinecone | $0.096/GB + compute | Production, managed |
| ChromaDB | Self-hosted | Cost-sensitive, small scale |
| OpenSearch | Instance-based | AWS-native, hybrid search |
| pgvector | RDS costs | Existing PostgreSQL |

### 10. Security & Compliance

```python
# Row-level security with metadata filtering
def query_with_permissions(user_id, query):
    # Get user's accessible doc IDs
    accessible_docs = get_user_permissions(user_id)
    
    # Filter search
    results = vectorstore.similarity_search(
        query,
        k=5,
        filter={"doc_id": {"$in": accessible_docs}}
    )
    
    return results

# Audit logging
def log_query(user_id, query, results):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('kb-audit-log')
    
    table.put_item(Item={
        'query_id': str(uuid.uuid4()),
        'user_id': user_id,
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'sources_accessed': [doc.metadata['source'] for doc in results]
    })
```

---

## Deployment Architecture

### Option 1: Serverless (Small-Medium Scale)
```
API Gateway → Lambda (query handler) → Pinecone/OpenSearch
                ↓
            Bedrock (embeddings + LLM)
```

### Option 2: Container-based (Medium-Large Scale)
```
ALB → ECS Fargate (LangChain app) → ChromaDB/pgvector
                ↓
            Bedrock (embeddings + LLM)
```

### Option 3: Fully Managed
```
API → Bedrock Knowledge Base → OpenSearch Serverless
                ↓
            Bedrock Claude
```

---

## Use Cases

1. **Enterprise Documentation**: Internal wikis, policies, procedures
2. **Customer Support**: FAQ, troubleshooting guides, product docs
3. **Research Assistant**: Academic papers, research notes
4. **Legal/Compliance**: Contract search, regulatory documents
5. **Technical Documentation**: API docs, architecture diagrams

---

## Next Steps

1. Choose vector database based on scale and requirements
2. Implement document ingestion pipeline
3. Test chunking strategies for your documents
4. Optimize embedding model selection
5. Implement RAG chain with LangChain
6. Add monitoring with LangSmith
7. Implement caching for cost optimization
8. Add security and permissions layer
