# Financial Knowledge Graph & Semantic Reasoning Platform - Architecture

**Date:** June 24, 2026  
**Version:** 1.0

---

## 1. System Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│   Web UI | Mobile | Jupyter | API Clients               │
└────────────────────┬─────────────────────────────────────┘
                     │
                HTTPS/GraphQL/REST
                     │
┌────────────────────▼─────────────────────────────────────┐
│         API GATEWAY (Golang 1.26.4 + Fiber 2.52)         │
│  OAuth 2.0 | GraphQL | Rate Limiting | Load Balancing   │
└────────────────────┬─────────────────────────────────────┘
                     │
                   gRPC
                     │
┌────────────────────▼─────────────────────────────────────┐
│              MICROSERVICES LAYER                         │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │
│  │ Query Engine   │  │  Graph ML      │  │  NL      │  │
│  │ (Golang 1.26.4)│  │  Pipeline      │  │  Query   │  │
│  │                │  │  (Python 3.13) │  │ (Python) │  │
│  └────────────────┘  └────────────────┘  └──────────┘  │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │
│  │ Ingestion      │  │  Reasoning     │  │  Entity  │  │
│  │ Service        │  │  Engine        │  │Resolution│  │
│  │ (Python 3.13)  │  │  (Python 3.13) │  │ (Python) │  │
│  └────────────────┘  └────────────────┘  └──────────┘  │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│           GRAPH DATABASE LAYER                           │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │ Neo4j 5.26     │  │ Apache Jena 5.2│                 │
│  │ Property Graph │  │ RDF Triple Store│                │
│  │ Causal Cluster │  │ SPARQL Endpoint│                 │
│  └────────────────┘  └────────────────┘                 │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Redis 7.4   │  │ PostgreSQL  │  │   Kafka     │
│ Cache       │  │   17.2      │  │    3.8      │
│ Cluster     │  │ Metadata DB │  │  Streams    │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## 2. Graph Query Engine Architecture

### **High-Performance Multi-Hop Query Execution**

```go
package query

import (
    "context"
    "github.com/neo4j/neo4j-go-driver/v5/neo4j"
    "time"
)

type GraphQueryEngine struct {
    neo4jDriver  neo4j.DriverWithContext
    jenaClient   *SparqlClient
    cache        *RedisCache
    reasoner     *ReasoningEngine
}

// Execute complex multi-hop relationship query
func (gqe *GraphQueryEngine) ExecuteMultiHopQuery(
    ctx context.Context,
    query *MultiHopQuery,
) (*GraphResult, error) {
    startTime := time.Now()
    
    // Check Redis cache first
    cacheKey := gqe.generateCacheKey(query)
    if cached, err := gqe.cache.Get(ctx, cacheKey); err == nil {
        return cached.(*GraphResult), nil
    }
    
    // Build optimized Cypher query with variable-length patterns
    cypherQuery := gqe.buildCypherQuery(query)
    
    // Execute on Neo4j with read session
    session := gqe.neo4jDriver.NewSession(ctx, neo4j.SessionConfig{
        AccessMode: neo4j.AccessModeRead,
        DatabaseName: "financial-kg",
    })
    defer session.Close(ctx)
    
    // Execute query with parameters
    result, err := session.Run(ctx, cypherQuery, map[string]any{
        "startId":   query.StartEntityID,
        "endId":     query.EndEntityID,
        "maxHops":   query.MaxHops,
        "relTypes":  query.RelationshipTypes,
        "limit":     query.Limit,
    })
    if err != nil {
        return nil, fmt.Errorf("neo4j query failed: %w", err)
    }
    
    // Parse and structure results
    graphResult := gqe.parseNeo4jResult(ctx, result)
    
    // Apply semantic reasoning if requested
    if query.EnableReasoning {
        graphResult = gqe.reasoner.ApplyInference(ctx, graphResult)
    }
    
    // Calculate path metrics
    graphResult.Metrics = gqe.calculatePathMetrics(graphResult)
    
    // Cache result (5 minute TTL)
    gqe.cache.SetWithExpiry(ctx, cacheKey, graphResult, 5*time.Minute)
    
    graphResult.QueryTimeMs = time.Since(startTime).Milliseconds()
    
    return graphResult, nil
}

func (gqe *GraphQueryEngine) buildCypherQuery(query *MultiHopQuery) string {
    // Build variable-length relationship pattern
    relPattern := "*1.." + strconv.Itoa(query.MaxHops)
    
    // Build relationship type filter
    var relTypeFilter string
    if len(query.RelationshipTypes) > 0 {
        relTypeFilter = ":" + strings.Join(query.RelationshipTypes, "|")
    }
    
    cypherQuery := fmt.Sprintf(`
        MATCH path = (start {id: $startId})-[r%s%s]-(end {id: $endId})
        WHERE ALL(rel IN relationships(path) WHERE rel.valid_to IS NULL OR rel.valid_to > datetime())
        WITH path, 
             nodes(path) as nodes,
             relationships(path) as rels,
             length(path) as pathLength
        ORDER BY pathLength ASC
        LIMIT $limit
        RETURN path, nodes, rels, pathLength,
               [node IN nodes | {
                   id: node.id,
                   type: labels(node)[0],
                   name: node.name,
                   properties: properties(node)
               }] as nodeDetails,
               [rel IN rels | {
                   type: type(rel),
                   properties: properties(rel)
               }] as relDetails
    `, relPattern, relTypeFilter)
    
    return cypherQuery
}

// Calculate aggregated ownership through multi-hop paths
func (gqe *GraphQueryEngine) CalculateIndirectOwnership(
    ctx context.Context,
    companyID string,
    personID string,
) (float64, error) {
    query := `
        MATCH path = (p:Person {id: $personId})-[:OWNS*1..5]->(c:Company {id: $companyId})
        WITH path, 
             reduce(ownership = 1.0, rel IN relationships(path) | 
                    ownership * rel.percentage / 100.0) as aggregatedOwnership
        RETURN aggregatedOwnership
        ORDER BY aggregatedOwnership DESC
        LIMIT 1
    `
    
    session := gqe.neo4jDriver.NewSession(ctx, neo4j.SessionConfig{
        AccessMode: neo4j.AccessModeRead,
    })
    defer session.Close(ctx)
    
    result, err := session.Run(ctx, query, map[string]any{
        "personId":  personID,
        "companyId": companyID,
    })
    if err != nil {
        return 0, err
    }
    
    if result.Next(ctx) {
        record := result.Record()
        ownership, _ := record.Get("aggregatedOwnership")
        return ownership.(float64), nil
    }
    
    return 0, nil
}
```

---

## 3. Entity Resolution Pipeline

### **Fuzzy Matching and Deduplication**

```python
from fuzzywuzzy import fuzz
from neo4j import GraphDatabase
import asyncio

class EntityResolutionPipeline:
    """Advanced entity resolution with fuzzy matching"""
    
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self.similarity_threshold = 0.85
        self.identifier_priority = ['lei', 'isin', 'cik', 'tax_id']
    
    async def resolve_and_merge(
        self,
        entity: Entity,
        entity_type: str
    ) -> str:
        """Resolve entity to existing node or create new"""
        
        # Stage 1: Exact identifier match (highest confidence)
        if entity.identifiers:
            existing_id = await self.match_by_identifier(
                entity.identifiers, entity_type
            )
            if existing_id:
                await self.merge_entity_data(existing_id, entity)
                return existing_id
        
        # Stage 2: Fuzzy name matching with attribute comparison
        candidates = await self.fuzzy_name_search(
            entity.name, entity_type, threshold=self.similarity_threshold
        )
        
        if candidates:
            # Stage 3: Multi-attribute similarity scoring
            best_match = await self.score_candidates(entity, candidates)
            
            if best_match and best_match.confidence > 0.90:
                await self.merge_entities(best_match.entity_id, entity)
                return best_match.entity_id
        
        # Stage 4: Create new entity if no confident match
        new_id = await self.create_new_entity(entity, entity_type)
        return new_id
    
    async def fuzzy_name_search(
        self,
        name: str,
        entity_type: str,
        threshold: float
    ) -> list:
        """Search for entities with similar names"""
        
        query = f"""
        MATCH (e:{entity_type})
        RETURN e.id as id, 
               e.name as name,
               e.properties as properties,
               e.identifiers as identifiers
        """
        
        async with self.neo4j_driver.session() as session:
            result = await session.run(query)
            records = await result.values()
            
            candidates = []
            normalized_name = self.normalize_name(name)
            
            for record in records:
                candidate_name = self.normalize_name(record['name'])
                
                # Multiple fuzzy matching algorithms
                ratio_score = fuzz.ratio(normalized_name, candidate_name) / 100.0
                token_sort = fuzz.token_sort_ratio(normalized_name, candidate_name) / 100.0
                token_set = fuzz.token_set_ratio(normalized_name, candidate_name) / 100.0
                
                # Weighted average
                similarity = (ratio_score * 0.4 + token_sort * 0.3 + token_set * 0.3)
                
                if similarity >= threshold:
                    candidates.append({
                        'id': record['id'],
                        'name': record['name'],
                        'similarity': similarity,
                        'properties': record['properties'],
                        'identifiers': record['identifiers']
                    })
            
            # Sort by similarity descending
            return sorted(candidates, key=lambda x: x['similarity'], reverse=True)
    
    async def score_candidates(
        self,
        entity: Entity,
        candidates: list
    ) -> Optional[MatchResult]:
        """Score candidates using multiple attributes"""
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = candidate['similarity'] * 0.5  # Name similarity weight
            
            # Country match
            if entity.country and candidate['properties'].get('country'):
                if entity.country == candidate['properties']['country']:
                    score += 0.2
            
            # Industry match
            if entity.industry and candidate['properties'].get('industry'):
                if entity.industry == candidate['properties']['industry']:
                    score += 0.15
            
            # Founding date proximity
            if entity.founded_date and candidate['properties'].get('founded_date'):
                date_diff = abs(
                    (entity.founded_date - candidate['properties']['founded_date']).days
                )
                if date_diff < 365:  # Within 1 year
                    score += 0.10
            
            # Identifier overlap
            if entity.identifiers and candidate['identifiers']:
                overlap = set(entity.identifiers.keys()) & set(candidate['identifiers'].keys())
                if overlap:
                    score += 0.05 * len(overlap)
            
            if score > best_score:
                best_score = score
                best_match = MatchResult(
                    entity_id=candidate['id'],
                    confidence=score
                )
        
        return best_match
```

---

## 4. Semantic Reasoning Engine

### **OWL 2 Ontology and SWRL Rules**

```python
from owlready2 import *
from rdflib import Graph, Namespace, URIRef, Literal

class SemanticReasoningEngine:
    """OWL 2 reasoning with transitive and inverse relations"""
    
    def __init__(self):
        # Load financial ontology
        self.onto = get_ontology("http://finance-kg.org/ontology#").load()
        
        # Define namespaces
        self.FIN = Namespace("http://finance-kg.org/ontology#")
        
        # Initialize Pellet reasoner
        with self.onto:
            sync_reasoner_pellet(
                infer_property_values=True,
                infer_data_property_values=True
            )
    
    def define_transitive_relationships(self):
        """Define transitive relationship rules"""
        
        with self.onto:
            # Indirect ownership (transitive)
            class indirectly_owns(ObjectProperty):
                equivalent_to = [owns.transitive_closure()]
            
            # Subsidiary chain (transitive)
            class indirect_subsidiary(ObjectProperty):
                equivalent_to = [subsidiary_of.transitive_closure()]
            
            # Control relationship (transitive)
            class controls(ObjectProperty):
                pass
            
            # Define rule: ownership > 50% implies control
            class OwnershipControlRule(Thing):
                equivalent_to = [
                    owns.some(Company) & 
                    owns.has_value(float, lambda x: x > 50.0)
                ]
    
    def infer_relationships(
        self,
        subgraph: SubGraph
    ) -> SubGraph:
        """Apply reasoning to infer implicit relationships"""
        
        # Create temporary ontology with subgraph data
        temp_onto = self.create_temp_ontology(subgraph)
        
        # Run reasoner
        with temp_onto:
            sync_reasoner_pellet()
        
        # Extract inferred facts
        inferred_rels = []
        
        # Transitive ownership
        for entity in temp_onto.individuals():
            if hasattr(entity, 'indirectly_owns'):
                for target in entity.indirectly_owns:
                    # Calculate aggregated ownership percentage
                    ownership_chain = self.find_ownership_path(
                        entity.id, target.id, subgraph
                    )
                    aggregated_pct = self.calculate_aggregated_ownership(
                        ownership_chain
                    )
                    
                    inferred_rels.append({
                        'source': entity.id,
                        'target': target.id,
                        'type': 'INDIRECTLY_OWNS',
                        'inferred': True,
                        'properties': {
                            'aggregated_percentage': aggregated_pct,
                            'path_length': len(ownership_chain)
                        },
                        'derivation': 'transitive_closure'
                    })
        
        # Inverse relationships
        for entity in temp_onto.individuals():
            if hasattr(entity, 'is_director_of'):
                for company in entity.is_director_of:
                    inferred_rels.append({
                        'source': company.id,
                        'target': entity.id,
                        'type': 'HAS_DIRECTOR',
                        'inferred': True,
                        'derivation': 'inverse_relationship'
                    })
        
        # Add inferred relationships to subgraph
        subgraph.relationships.extend(inferred_rels)
        subgraph.inference_count = len(inferred_rels)
        
        return subgraph
    
    def calculate_aggregated_ownership(
        self,
        ownership_chain: list
    ) -> float:
        """Calculate ownership through chain"""
        
        aggregated = 1.0
        for rel in ownership_chain:
            percentage = rel.get('percentage', 0) / 100.0
            aggregated *= percentage
        
        return aggregated * 100.0  # Convert back to percentage
```

---

## 5. Graph Neural Network Architecture

### **GNN for Link Prediction and Node Classification**

```python
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, SAGEConv
from torch_geometric.data import Data, DataLoader

class FinancialGraphNeuralNetwork(torch.nn.Module):
    """Multi-layer GNN with attention mechanism"""
    
    def __init__(
        self,
        num_node_features: int,
        hidden_channels: int = 128,
        num_classes: int = 10,
        num_layers: int = 3,
        dropout: float = 0.5
    ):
        super().__init__()
        
        # Graph Attention Network layers
        self.convs = torch.nn.ModuleList()
        self.convs.append(
            GATConv(num_node_features, hidden_channels, heads=8, dropout=dropout)
        )
        
        for _ in range(num_layers - 2):
            self.convs.append(
                GATConv(hidden_channels * 8, hidden_channels, heads=8, dropout=dropout)
            )
        
        self.convs.append(
            GATConv(hidden_channels * 8, num_classes, heads=1, concat=False, dropout=dropout)
        )
        
        self.dropout = dropout
    
    def forward(self, x, edge_index, edge_attr=None):
        """Forward pass through GNN layers"""
        
        for i, conv in enumerate(self.convs[:-1]):
            x = conv(x, edge_index)
            x = F.elu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Final layer
        x = self.convs[-1](x, edge_index)
        
        return x
    
    def encode(self, x, edge_index):
        """Generate node embeddings"""
        self.eval()
        with torch.no_grad():
            embeddings = self(x, edge_index)
        return embeddings

class GraphMLPipeline:
    """Complete ML pipeline for graph learning"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.embedding_dim = 128
    
    def train_link_predictor(
        self,
        graph_data: Data,
        num_epochs: int = 300,
        learning_rate: float = 0.005
    ):
        """Train GNN for link prediction"""
        
        # Initialize model
        self.model = FinancialGraphNeuralNetwork(
            num_node_features=graph_data.num_features,
            hidden_channels=self.embedding_dim,
            num_classes=self.embedding_dim
        ).to(self.device)
        
        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=5e-4
        )
        
        # Move data to device
        graph_data = graph_data.to(self.device)
        
        # Training loop
        self.model.train()
        for epoch in range(num_epochs):
            optimizer.zero_grad()
            
            # Forward pass
            embeddings = self.model(graph_data.x, graph_data.edge_index)
            
            # Link prediction loss (dot product of embeddings)
            pos_edge_index = graph_data.edge_index
            neg_edge_index = self.sample_negative_edges(graph_data)
            
            # Positive edges
            pos_src = embeddings[pos_edge_index[0]]
            pos_dst = embeddings[pos_edge_index[1]]
            pos_scores = (pos_src * pos_dst).sum(dim=1)
            pos_loss = -torch.log(torch.sigmoid(pos_scores) + 1e-15).mean()
            
            # Negative edges
            neg_src = embeddings[neg_edge_index[0]]
            neg_dst = embeddings[neg_edge_index[1]]
            neg_scores = (neg_src * neg_dst).sum(dim=1)
            neg_loss = -torch.log(1 - torch.sigmoid(neg_scores) + 1e-15).mean()
            
            loss = pos_loss + neg_loss
            
            loss.backward()
            optimizer.step()
            
            if epoch % 20 == 0:
                print(f'Epoch {epoch}, Loss: {loss.item():.4f}')
        
        return self.model
    
    def predict_links(
        self,
        node_pairs: list,
        graph_data: Data
    ) -> list:
        """Predict probability of links between node pairs"""
        
        self.model.eval()
        graph_data = graph_data.to(self.device)
        
        with torch.no_grad():
            embeddings = self.model(graph_data.x, graph_data.edge_index)
            
            predictions = []
            for src_id, dst_id in node_pairs:
                src_emb = embeddings[src_id]
                dst_emb = embeddings[dst_id]
                
                # Dot product similarity
                score = torch.sigmoid(torch.dot(src_emb, dst_emb)).item()
                predictions.append(score)
        
        return predictions
    
    def explain_prediction(
        self,
        src_id: int,
        dst_id: int,
        graph_data: Data,
        k_hops: int = 2
    ) -> dict:
        """Explain link prediction using k-hop neighborhood"""
        
        # Extract k-hop subgraph around nodes
        subgraph = self.extract_k_hop_subgraph(
            [src_id, dst_id], graph_data, k_hops
        )
        
        # Get embeddings
        embeddings = self.model.encode(subgraph.x, subgraph.edge_index)
        
        # Find most influential neighbors
        src_neighbors = self.get_neighbors(src_id, subgraph)
        dst_neighbors = self.get_neighbors(dst_id, subgraph)
        
        # Calculate neighbor influence scores
        src_influences = []
        for neighbor in src_neighbors:
            influence = torch.cosine_similarity(
                embeddings[src_id].unsqueeze(0),
                embeddings[neighbor].unsqueeze(0)
            ).item()
            src_influences.append((neighbor, influence))
        
        return {
            'subgraph_nodes': subgraph.num_nodes,
            'subgraph_edges': subgraph.num_edges,
            'top_src_influences': sorted(src_influences, key=lambda x: x[1], reverse=True)[:5],
            'common_neighbors': len(set(src_neighbors) & set(dst_neighbors))
        }
```

---

## 6. Caching Strategy

### **Multi-Layer Redis Caching**

```go
type CacheManager struct {
    redis *redis.ClusterClient
    ttls  map[string]time.Duration
}

func NewCacheManager() *CacheManager {
    return &CacheManager{
        redis: redis.NewClusterClient(&redis.ClusterOptions{
            Addrs: []string{
                "redis-1:6379",
                "redis-2:6379",
                "redis-3:6379",
            },
        }),
        ttls: map[string]time.Duration{
            "subgraph":       10 * time.Minute,
            "query_result":   5 * time.Minute,
            "entity":         30 * time.Minute,
            "relationship":   30 * time.Minute,
            "path_finding":   10 * time.Minute,
            "gnn_embedding":  1 * time.Hour,
        },
    }
}

func (cm *CacheManager) GetOrCompute(
    ctx context.Context,
    key string,
    cacheType string,
    computeFn func() (interface{}, error),
) (interface{}, error) {
    // Try cache first
    cached, err := cm.redis.Get(ctx, key).Result()
    if err == nil {
        var result interface{}
        json.Unmarshal([]byte(cached), &result)
        return result, nil
    }
    
    // Cache miss - compute
    result, err := computeFn()
    if err != nil {
        return nil, err
    }
    
    // Store in cache
    ttl := cm.ttls[cacheType]
    resultJSON, _ := json.Marshal(result)
    cm.redis.Set(ctx, key, resultJSON, ttl)
    
    return result, nil
}
```

---

## 7. Deployment Architecture

```yaml
# Neo4j Causal Cluster
apiVersion: v1
kind: StatefulSet
metadata:
  name: neo4j-core
spec:
  serviceName: neo4j-core
  replicas: 3
  template:
    spec:
      containers:
      - name: neo4j
        image: neo4j:5.26-enterprise
        ports:
        - containerPort: 7474  # HTTP
        - containerPort: 7473  # HTTPS
        - containerPort: 7687  # Bolt
        env:
        - name: NEO4J_dbms_mode
          value: "CORE"
        - name: NEO4J_causal__clustering_minimum__core__cluster__size__at__formation
          value: "3"
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
          limits:
            memory: "32Gi"
            cpu: "8"
```

---

**Status:** ✅ Complete  
**Version:** 1.0  
**Date:** June 24, 2026
