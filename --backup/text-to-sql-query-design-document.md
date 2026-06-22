# Text-to-SQL Query Generator - Design Document

**Document Date:** June 18, 2026  
**Tech Stack Status:** Latest & Greatest as of this date  
**Project Type:** AI-Powered Natural Language Database Query System

---

## 📋 Executive Summary

A sophisticated AI-powered platform that converts natural language questions into optimized SQL queries. The system understands database schemas, generates accurate queries, executes them safely, and presents results in human-readable formats with visualizations.

---

## 🎯 Use Cases

1. **Business Analysts**: Query databases without SQL knowledge
2. **Product Managers**: Extract insights from production data quickly
3. **Customer Support**: Pull customer data for ticket resolution
4. **Data Scientists**: Rapid exploratory data analysis
5. **Non-Technical Stakeholders**: Self-service data access
6. **Developers**: Accelerate query writing with AI assistance

---

## 🚀 Latest & Greatest Tech Stack (June 2026)

### **Frontend**

| Technology | Version | Why This Choice |
|------------|---------|-----------------|
| **Next.js** | 16.x | App Router, Server Components, streaming responses |
| **React** | 19.2.7 | Latest concurrent features, automatic batching |
| **TypeScript** | 5.5+ | Enhanced type safety, superior inference |
| **Tailwind CSS** | 4.x | Performance improvements, container queries |
| **shadcn/ui** | Latest | Beautiful, accessible components |
| **TanStack Query** | 5.x | Powerful data fetching and caching |
| **Monaco Editor** | 0.50+ | VS Code-powered SQL editor with syntax highlighting |
| **Recharts** | 2.x | Data visualization library |
| **React Flow** | 12.x | Schema visualization and ER diagrams |

### **Backend**

| Technology | Version | Why This Choice |
|------------|---------|-----------------|
| **Node.js** | 22.x LTS | Native TypeScript support, performance |
| **Hono** | 4.x | Ultra-fast edge-first web framework |
| **tRPC** | 11.x | End-to-end typesafe APIs |
| **Prisma** | 6.x | Type-safe ORM with excellent migrations |
| **PostgreSQL** | 16.x | Advanced features, JSON support, full-text search |
| **Redis** | 7.x | Query caching, rate limiting, session storage |

### **AI/ML Stack**

| Technology | Version | Why This Choice |
|------------|---------|-----------------|
| **OpenAI GPT-5.5** | Latest | Superior code generation, SQL understanding |
| **Claude Opus 4.8** | Latest | Excellent reasoning, context understanding (500K+ tokens) |
| **LangChain** | 0.2.x | AI orchestration, agent workflows |
| **Vanna AI** | 0.8.x | Specialized text-to-SQL framework with RAG |
| **SQLGlot** | 25.x | SQL parsing, optimization, transpilation |
| **Instructor** | 1.x | Structured output extraction with Pydantic |

### **Database Connectors**

| Technology | Version | Why This Choice |
|------------|---------|-----------------|
| **node-postgres** | 8.x | PostgreSQL driver |
| **mysql2** | 3.x | MySQL/MariaDB driver |
| **tedious** | 18.x | SQL Server driver |
| **better-sqlite3** | 11.x | SQLite driver (edge-compatible) |
| **mongodb** | 6.x | MongoDB driver |
| **Prisma** | 6.x | Universal ORM supporting all major databases |

### **Authentication & Security**

| Technology | Version | Why This Choice |
|------------|---------|-----------------|
| **Clerk** | 5.x | Enterprise auth with RBAC |
| **PASETO** | v4 | Secure token format |
| **Unkey** | Latest | API key management and rate limiting |
| **SQL Injection Prevention** | Built-in | Parameterized queries, query validation |

### **Monitoring & Observability**

| Technology | Version | Why This Choice |
|------------|---------|-----------------|
| **Sentry** | Latest | Error tracking, performance monitoring |
| **Axiom** | Latest | Structured logging, query analytics |
| **Highlight.io** | Latest | Session replay, debugging |

### **Testing**

| Technology | Version | Why This Choice |
|------------|---------|-----------------|
| **Vitest** | 2.x | Fast test runner |
| **Playwright** | 1.45+ | E2E testing |
| **sql-test-kit** | Custom | SQL query validation framework |

---

## 🏗️ System Architecture

### **Architecture Pattern**: Multi-Tenant RAG-Enhanced AI-to-SQL Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
│    Next.js 16 (App Router) + Monaco Editor + React Flow    │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      │ tRPC / Server Actions
                      │
┌─────────────────────▼────────────────────────────────────────┐
│                   API Layer (Edge)                           │
│              Hono + tRPC + Edge Functions                   │
└──────┬──────────────┬──────────────┬────────────────────────┘
       │              │              │
       │              │              │
  ┌────▼────┐   ┌────▼─────┐   ┌───▼──────┐
  │  Auth   │   │Schema    │   │ Query    │
  │(Clerk)  │   │Analyzer  │   │Executor  │
  └─────────┘   └────┬─────┘   └───┬──────┘
                     │             │
            ┌────────▼─────────────▼────────┐
            │    AI Pipeline (LangChain)    │
            │                                │
            │  ┌──────────┐  ┌───────────┐ │
            │  │ GPT-5.5  │  │Opus 4.8   │ │
            │  └────┬─────┘  └─────┬─────┘ │
            │       │              │        │
            │  ┌────▼──────────────▼─────┐ │
            │  │   RAG Context Engine    │ │
            │  │  (Vector DB + Examples) │ │
            │  └──────────┬──────────────┘ │
            └─────────────┼─────────────────┘
                          │
          ┌───────────────▼───────────────┐
          │   Multi-DB Connection Pool   │
          │ PostgreSQL │ MySQL │ MSSQL  │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │       Redis Cache Layer       │
          │ (Query Cache + Schema Cache) │
          └───────────────────────────────┘
```

---

## 📦 Core Features & Implementation

### **1. Natural Language to SQL Translation**

**Tech Stack:**
- GPT-5.5 for query generation
- Claude Opus 4.8 for complex multi-step queries
- Vanna AI for RAG-enhanced generation
- SQLGlot for query validation and optimization

**Implementation:**

```typescript
interface TextToSQLRequest {
  question: string;
  databaseId: string;
  context?: {
    previousQueries?: string[];
    focusTables?: string[];
  };
}

interface SQLGenerationResult {
  sql: string;
  confidence: number;
  explanation: string;
  assumptions: string[];
  warnings: string[];
  estimatedRows?: number;
}

async function generateSQL(request: TextToSQLRequest): Promise<SQLGenerationResult> {
  // Step 1: Fetch database schema
  const schema = await getSchemaContext(request.databaseId);
  
  // Step 2: Retrieve similar queries from RAG (vector similarity)
  const similarQueries = await retrieveSimilarQueries(
    request.question,
    request.databaseId
  );
  
  // Step 3: Build AI prompt with schema + examples
  const prompt = buildPrompt({
    question: request.question,
    schema,
    examples: similarQueries,
    dialect: schema.dialect, // postgres, mysql, mssql, etc.
  });
  
  // Step 4: Generate SQL with GPT-5.5
  const response = await openai.chat.completions.create({
    model: 'gpt-5.5',
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: prompt }
    ],
    temperature: 0.1, // Low temperature for deterministic queries
    response_format: { type: 'json_object' },
  });
  
  const result = JSON.parse(response.choices[0].message.content);
  
  // Step 5: Validate and optimize SQL
  const validated = await validateSQL(result.sql, schema);
  const optimized = await optimizeQuery(validated.sql);
  
  // Step 6: Estimate query cost/rows
  const estimate = await explainQuery(optimized, request.databaseId);
  
  return {
    sql: optimized,
    confidence: result.confidence,
    explanation: result.explanation,
    assumptions: result.assumptions,
    warnings: validated.warnings,
    estimatedRows: estimate.rows,
  };
}
```

**AI System Prompt:**

```typescript
const SYSTEM_PROMPT = `
You are an expert SQL query generator. Your task is to convert natural language questions into accurate, optimized SQL queries.

Rules:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE unless explicitly requested)
2. Always use proper table/column names from the provided schema
3. Use appropriate JOINs, WHERE clauses, and aggregations
4. Optimize for readability and performance
5. Include CTEs for complex logic
6. Add LIMIT clauses for large result sets
7. Use proper date/time functions for temporal queries
8. Handle NULL values appropriately
9. Return JSON with: sql, confidence (0-1), explanation, assumptions, warnings

Response format:
{
  "sql": "SELECT ...",
  "confidence": 0.95,
  "explanation": "This query joins orders with customers...",
  "assumptions": ["Assuming 'total' means sum of all items"],
  "warnings": ["Query may be slow on large datasets"]
}
`;
```

---

### **2. Schema Understanding & Context**

**Tech Stack:**
- Prisma for schema introspection
- React Flow for visual ER diagrams
- Redis for schema caching

**Schema Extraction:**

```typescript
interface DatabaseSchema {
  tables: TableSchema[];
  relationships: Relationship[];
  indexes: Index[];
  views: View[];
  dialect: 'postgres' | 'mysql' | 'mssql' | 'sqlite';
}

interface TableSchema {
  name: string;
  schema?: string;
  columns: Column[];
  primaryKey: string[];
  foreignKeys: ForeignKey[];
  indexes: Index[];
  rowCount?: number;
  description?: string;
}

interface Column {
  name: string;
  type: string;
  nullable: boolean;
  defaultValue?: any;
  description?: string;
  isUnique: boolean;
  isAutoIncrement: boolean;
}

async function extractSchema(connectionId: string): Promise<DatabaseSchema> {
  const connection = await getConnection(connectionId);
  
  // Use Prisma to introspect the database
  const schema = await prisma.$queryRaw`
    SELECT 
      table_name,
      column_name,
      data_type,
      is_nullable,
      column_default
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position
  `;
  
  // Get relationships
  const relationships = await prisma.$queryRaw`
    SELECT 
      tc.table_name, 
      kcu.column_name,
      ccu.table_name AS foreign_table_name,
      ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
  `;
  
  // Cache the schema in Redis with TTL
  await redis.setex(
    `schema:${connectionId}`,
    3600, // 1 hour TTL
    JSON.stringify({ tables: schema, relationships })
  );
  
  return transformSchema(schema, relationships);
}
```

**Schema Visualization (React Flow):**

```typescript
import ReactFlow, { Node, Edge } from 'reactflow';

function SchemaVisualization({ schema }: { schema: DatabaseSchema }) {
  const nodes: Node[] = schema.tables.map((table, index) => ({
    id: table.name,
    type: 'tableNode',
    position: calculatePosition(index, schema.tables.length),
    data: {
      label: table.name,
      columns: table.columns,
      primaryKey: table.primaryKey,
    },
  }));
  
  const edges: Edge[] = schema.relationships.map((rel) => ({
    id: `${rel.fromTable}-${rel.toTable}`,
    source: rel.fromTable,
    target: rel.toTable,
    label: `${rel.fromColumn} → ${rel.toColumn}`,
    type: 'smoothstep',
  }));
  
  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

---

### **3. RAG-Enhanced Query Generation**

**Tech Stack:**
- Upstash Vector for vector database
- OpenAI text-embedding-3-large for embeddings
- Vanna AI framework integration

**Implementation:**

```typescript
import { Index } from '@upstash/vector';

const vectorIndex = new Index({
  url: process.env.UPSTASH_VECTOR_URL!,
  token: process.env.UPSTASH_VECTOR_TOKEN!,
});

interface QueryExample {
  id: string;
  question: string;
  sql: string;
  databaseId: string;
  rating?: number;
  usageCount: number;
  createdAt: Date;
}

// Store successful queries for future reference
async function storeQueryExample(example: QueryExample) {
  // Generate embedding for the question
  const embedding = await openai.embeddings.create({
    model: 'text-embedding-3-large',
    input: example.question,
  });
  
  // Store in vector database
  await vectorIndex.upsert({
    id: example.id,
    vector: embedding.data[0].embedding,
    metadata: {
      question: example.question,
      sql: example.sql,
      databaseId: example.databaseId,
      rating: example.rating || 0,
    },
  });
  
  // Also store in PostgreSQL for full query history
  await prisma.queryExample.create({
    data: example,
  });
}

// Retrieve similar queries using vector search
async function retrieveSimilarQueries(
  question: string,
  databaseId: string,
  topK: number = 5
): Promise<QueryExample[]> {
  // Generate embedding for the input question
  const embedding = await openai.embeddings.create({
    model: 'text-embedding-3-large',
    input: question,
  });
  
  // Search vector database
  const results = await vectorIndex.query({
    vector: embedding.data[0].embedding,
    topK,
    filter: `databaseId = '${databaseId}'`,
    includeMetadata: true,
  });
  
  return results.map((result) => ({
    id: result.id,
    question: result.metadata.question,
    sql: result.metadata.sql,
    databaseId: result.metadata.databaseId,
    rating: result.metadata.rating,
    similarity: result.score,
  }));
}
```

---

### **4. Query Validation & Safety**

**Security Layers:**

```typescript
interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  sanitizedSQL?: string;
}

async function validateSQL(
  sql: string,
  schema: DatabaseSchema
): Promise<ValidationResult> {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // 1. Parse SQL using SQLGlot
  let parsed;
  try {
    parsed = sqlglot.parse(sql, schema.dialect);
  } catch (error) {
    errors.push(`Syntax error: ${error.message}`);
    return { isValid: false, errors, warnings };
  }
  
  // 2. Check for dangerous operations
  const dangerousKeywords = [
    'DROP', 'TRUNCATE', 'DELETE', 'UPDATE', 'INSERT', 
    'ALTER', 'GRANT', 'REVOKE', 'EXECUTE'
  ];
  
  for (const keyword of dangerousKeywords) {
    if (sql.toUpperCase().includes(keyword)) {
      errors.push(`Forbidden operation: ${keyword}`);
    }
  }
  
  // 3. Validate table/column names against schema
  const tables = extractTablesFromSQL(parsed);
  for (const table of tables) {
    if (!schema.tables.find(t => t.name === table)) {
      errors.push(`Table '${table}' does not exist`);
    }
  }
  
  // 4. Check for missing LIMIT clause on potentially large queries
  if (!sql.toUpperCase().includes('LIMIT') && 
      !sql.toUpperCase().includes('TOP')) {
    warnings.push('Query has no LIMIT clause - may return large result set');
  }
  
  // 5. Check for Cartesian products (missing JOIN conditions)
  const joins = extractJoins(parsed);
  if (joins.length > 0 && !hasJoinConditions(parsed)) {
    warnings.push('Potential Cartesian product detected');
  }
  
  // 6. Sanitize SQL (parameterize if needed)
  const sanitized = sanitizeSQL(sql);
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    sanitizedSQL: sanitized,
  };
}

// Query execution with timeout and row limit
async function executeQuery(
  sql: string,
  connectionId: string,
  options: {
    timeout?: number;
    maxRows?: number;
  } = {}
): Promise<QueryResult> {
  const { timeout = 30000, maxRows = 1000 } = options;
  
  const connection = await getConnection(connectionId);
  
  // Add LIMIT clause if not present
  let finalSQL = sql;
  if (!sql.toUpperCase().includes('LIMIT')) {
    finalSQL = `${sql} LIMIT ${maxRows}`;
  }
  
  // Execute with timeout
  const result = await Promise.race([
    connection.query(finalSQL),
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Query timeout')), timeout)
    ),
  ]);
  
  return {
    rows: result.rows,
    rowCount: result.rowCount,
    executionTime: result.duration,
    columns: result.fields.map(f => f.name),
  };
}
```

---

### **5. Interactive Query Editor**

**Tech Stack:**
- Monaco Editor (VS Code editor)
- SQL syntax highlighting
- Auto-completion for tables/columns

**Implementation:**

```typescript
import Editor from '@monaco-editor/react';

function SQLQueryEditor({ schema, onExecute }: Props) {
  const [sql, setSQL] = useState('');
  
  // Configure Monaco with SQL language support
  const handleEditorWillMount = (monaco: Monaco) => {
    // Register SQL completion provider
    monaco.languages.registerCompletionItemProvider('sql', {
      provideCompletionItems: (model, position) => {
        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn,
        };
        
        // Suggest table names
        const tableSuggestions = schema.tables.map((table) => ({
          label: table.name,
          kind: monaco.languages.CompletionItemKind.Class,
          insertText: table.name,
          range,
          documentation: table.description,
        }));
        
        // Suggest column names
        const columnSuggestions = schema.tables.flatMap((table) =>
          table.columns.map((col) => ({
            label: `${table.name}.${col.name}`,
            kind: monaco.languages.CompletionItemKind.Field,
            insertText: `${table.name}.${col.name}`,
            range,
            documentation: `${col.type} - ${col.description}`,
          }))
        );
        
        return {
          suggestions: [...tableSuggestions, ...columnSuggestions],
        };
      },
    });
  };
  
  return (
    <Editor
      height="400px"
      language="sql"
      theme="vs-dark"
      value={sql}
      onChange={(value) => setSQL(value || '')}
      beforeMount={handleEditorWillMount}
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        formatOnPaste: true,
        formatOnType: true,
      }}
    />
  );
}
```

---

### **6. Data Visualization**

**Tech Stack:**
- Recharts for charts
- AG Grid for data tables
- Export to CSV/Excel

**Implementation:**

```typescript
interface QueryResult {
  rows: any[];
  columns: string[];
  rowCount: number;
  executionTime: number;
}

function ResultsVisualization({ result }: { result: QueryResult }) {
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');
  
  // Auto-detect chart type based on data
  const suggestedChartType = detectChartType(result);
  
  if (viewMode === 'table') {
    return (
      <AGGridReact
        rowData={result.rows}
        columnDefs={result.columns.map(col => ({
          field: col,
          sortable: true,
          filter: true,
          resizable: true,
        }))}
        pagination
        paginationPageSize={50}
      />
    );
  }
