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
  
  // Render chart based on detected type
  return (
    <ResponsiveContainer width="100%" height={400}>
      {suggestedChartType === 'bar' && (
        <BarChart data={result.rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={result.columns[0]} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={result.columns[1]} fill="#8884d8" />
        </BarChart>
      )}
      {suggestedChartType === 'line' && (
        <LineChart data={result.rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={result.columns[0]} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey={result.columns[1]} stroke="#8884d8" />
        </LineChart>
      )}
    </ResponsiveContainer>
  );
}

// Export functionality
async function exportResults(result: QueryResult, format: 'csv' | 'excel') {
  if (format === 'csv') {
    const csv = Papa.unparse(result.rows);
    downloadFile(csv, 'query-results.csv', 'text/csv');
  } else {
    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.json_to_sheet(result.rows);
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Results');
    XLSX.writeFile(workbook, 'query-results.xlsx');
  }
}
```

---

## 🗄️ Database Schema (Prisma)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id                String              @id @default(cuid())
  clerkId           String              @unique
  email             String              @unique
  name              String?
  role              UserRole            @default(USER)
  createdAt         DateTime            @default(now())
  updatedAt         DateTime            @updatedAt
  
  connections       DatabaseConnection[]
  queries           Query[]
  queryHistory      QueryHistory[]
  savedQueries      SavedQuery[]
  apiKeys           ApiKey[]
  
  @@index([email])
  @@index([clerkId])
}

enum UserRole {
  USER
  ADMIN
  ANALYST
  VIEWER
}

model DatabaseConnection {
  id                String              @id @default(cuid())
  userId            String
  user              User                @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  name              String
  type              DatabaseType
  host              String
  port              Int
  database          String
  username          String
  password          String              // Encrypted at rest
  sslEnabled        Boolean             @default(true)
  
  schemaCache       Json?               // Cached schema structure
  schemaCachedAt    DateTime?
  
  isActive          Boolean             @default(true)
  lastConnectedAt   DateTime?
  
  createdAt         DateTime            @default(now())
  updatedAt         DateTime            @updatedAt
  
  queries           Query[]
  queryExamples     QueryExample[]
  
  @@index([userId])
  @@index([type])
}

enum DatabaseType {
  POSTGRES
  MYSQL
  MSSQL
  SQLITE
  MONGODB
  SNOWFLAKE
  BIGQUERY
  REDSHIFT
}

model Query {
  id                String              @id @default(cuid())
  userId            String
  user              User                @relation(fields: [userId], references: [id], onDelete: Cascade)
  connectionId      String
  connection        DatabaseConnection  @relation(fields: [connectionId], references: [id], onDelete: Cascade)
  
  naturalLanguage   String              @db.Text
  generatedSQL      String              @db.Text
  executedSQL       String?             @db.Text
  
  status            QueryStatus         @default(PENDING)
  confidence        Float?
  
  resultRows        Int?
  executionTime     Int?                // Milliseconds
  
  error             String?             @db.Text
  
  createdAt         DateTime            @default(now())
  
  history           QueryHistory[]
  
  @@index([userId])
  @@index([connectionId])
  @@index([status])
  @@index([createdAt])
}

enum QueryStatus {
  PENDING
  GENERATING
  VALIDATING
  EXECUTING
  COMPLETED
  FAILED
}

model QueryHistory {
  id                String              @id @default(cuid())
  queryId           String
  query             Query               @relation(fields: [queryId], references: [id], onDelete: Cascade)
  userId            String
  user              User                @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  sql               String              @db.Text
  results           Json?               // Cached results
  executionTime     Int
  rowsReturned      Int
  
  executedAt        DateTime            @default(now())
  
  @@index([queryId])
  @@index([userId])
  @@index([executedAt])
}

model SavedQuery {
  id                String              @id @default(cuid())
  userId            String
  user              User                @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  name              String
  description       String?             @db.Text
  naturalLanguage   String              @db.Text
  sql               String              @db.Text
  
  tags              String[]
  isPublic          Boolean             @default(false)
  usageCount        Int                 @default(0)
  
  createdAt         DateTime            @default(now())
  updatedAt         DateTime            @updatedAt
  
  @@index([userId])
  @@index([isPublic])
}

model QueryExample {
  id                String              @id @default(cuid())
  connectionId      String
  connection        DatabaseConnection  @relation(fields: [connectionId], references: [id], onDelete: Cascade)
  
  question          String              @db.Text
  sql               String              @db.Text
  embedding         Bytes?              // Vector embedding for similarity search
  
  rating            Int                 @default(0)
  usageCount        Int                 @default(0)
  
  createdAt         DateTime            @default(now())
  
  @@index([connectionId])
  @@index([rating])
}

model ApiKey {
  id                String              @id @default(cuid())
  userId            String
  user              User                @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  name              String
  key               String              @unique
  
  permissions       String[]            // ["read", "write", "execute"]
  rateLimit         Int                 @default(100) // Requests per minute
  
  lastUsedAt        DateTime?
  expiresAt         DateTime?
  
  isActive          Boolean             @default(true)
  
  createdAt         DateTime            @default(now())
  
  @@index([userId])
  @@index([key])
}
```

---

## 🔐 Security Architecture

### **Multi-Layer Security Approach**

#### **1. Authentication & Authorization**
- **Clerk** for user authentication with MFA
- **RBAC** (Role-Based Access Control)
  - Admin: Full access, user management
  - Analyst: Create/execute queries, manage connections
  - Viewer: Read-only access to saved queries
  - API: Programmatic access with API keys

#### **2. Database Connection Security**
- Credentials encrypted at rest (AES-256)
- SSL/TLS enforced for all database connections
- Connection pooling with read-only replicas for queries
- IP whitelisting for production databases
- Vault integration for secret management (HashiCorp Vault)

```golang
// Golang: Secure connection handler
package database

import (
    "crypto/tls"
    "database/sql"
    "github.com/jackc/pgx/v5/pgxpool"
)

type SecureConnection struct {
    pool     *pgxpool.Pool
    readOnly bool
}

func NewSecureConnection(config ConnectionConfig) (*SecureConnection, error) {
    // Decrypt credentials from vault
    decryptedPassword, err := vault.DecryptSecret(config.EncryptedPassword)
    if err != nil {
        return nil, err
    }
    
    // Configure TLS
    tlsConfig := &tls.Config{
        MinVersion: tls.VersionTLS13,
        ServerName: config.Host,
    }
    
    // Create connection pool
    poolConfig, err := pgxpool.ParseConfig(fmt.Sprintf(
        "postgres://%s:%s@%s:%d/%s?sslmode=require",
        config.Username,
        decryptedPassword,
        config.Host,
        config.Port,
        config.Database,
    ))
    
    poolConfig.ConnConfig.TLSConfig = tlsConfig
    poolConfig.MaxConns = 10
    poolConfig.MinConns = 2
    
    // Set read-only mode for query execution
    if config.ReadOnly {
        poolConfig.AfterConnect = func(ctx context.Context, conn *pgx.Conn) error {
            _, err := conn.Exec(ctx, "SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
            return err
        }
    }
    
    pool, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
    if err != nil {
        return nil, err
    }
    
    return &SecureConnection{pool: pool, readOnly: config.ReadOnly}, nil
}
```

#### **3. SQL Injection Prevention**
- All queries validated before execution
- Parameterized queries only
- SQL parsing and AST analysis
- Blacklist of dangerous keywords
- Query complexity analysis

```python
# Python: SQL validation service
from sqlglot import parse, exp
from typing import List, Dict

class SQLValidator:
    FORBIDDEN_OPERATIONS = [
        'DROP', 'TRUNCATE', 'DELETE', 'UPDATE', 'INSERT',
        'ALTER', 'CREATE', 'GRANT', 'REVOKE', 'EXECUTE'
    ]
    
    def validate(self, sql: str, schema: Dict) -> ValidationResult:
        """Validate SQL query for security and correctness"""
        errors = []
        warnings = []
        
        # Parse SQL
        try:
            parsed = parse(sql, dialect='postgres')
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error: {str(e)}"]
            )
        
        # Check for forbidden operations
        for statement in parsed:
            for node in statement.walk():
                if isinstance(node, (exp.Drop, exp.Delete, exp.Update, exp.Insert)):
                    errors.append(f"Forbidden operation: {node.__class__.__name__}")
        
        # Validate table/column names against schema
        tables = self._extract_tables(parsed[0])
        for table in tables:
            if table not in schema['tables']:
                errors.append(f"Table '{table}' does not exist")
        
        # Check for Cartesian products
        if self._has_cartesian_product(parsed[0]):
            warnings.append("Potential Cartesian product detected")
        
        # Check for missing LIMIT
        if not self._has_limit(parsed[0]):
            warnings.append("Query has no LIMIT clause")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

#### **4. Rate Limiting & Quotas**
- Per-user query limits (100 queries/hour for free tier)
- API key-based rate limiting (Unkey)
- Connection pool limits
- Query timeout enforcement (30s default)
- Result set size limits (10,000 rows max)

#### **5. Audit Logging**
- All queries logged with user, timestamp, SQL
- Connection attempts tracked
- Failed authentication logged
- Admin actions audited
- Compliance with SOC2, GDPR, HIPAA

---

## 🧪 Test-Driven Development Strategy

### **Testing Philosophy**
We follow strict TDD principles: **Write Tests First, Code Second**

### **Test Pyramid**

```
           ┌──────────────┐
           │   E2E Tests  │  10% - Full user workflows
           │   (Playwright)│
           ├──────────────┤
          ┌┴──────────────┴┐
          │ Integration Tests│ 20% - API + DB interactions
          │    (Vitest)     │
          ├─────────────────┤
        ┌─┴─────────────────┴─┐
        │    Unit Tests        │ 70% - Pure logic
        │  (Vitest + PyTest)   │
        └──────────────────────┘
```

### **1. Unit Tests (70% Coverage)**

**Golang Unit Tests:**
```golang
// database/validator_test.go
package database

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestSQLValidator_ValidateQuery(t *testing.T) {
    tests := []struct {
        name      string
        sql       string
        wantValid bool
        wantError string
    }{
        {
            name:      "valid SELECT query",
            sql:       "SELECT * FROM users WHERE id = 1",
            wantValid: true,
        },
        {
            name:      "forbidden DELETE operation",
            sql:       "DELETE FROM users WHERE id = 1",
            wantValid: false,
            wantError: "Forbidden operation: DELETE",
        },
        {
            name:      "SQL injection attempt",
            sql:       "SELECT * FROM users WHERE id = '1' OR '1'='1'",
            wantValid: false,
            wantError: "Potential SQL injection detected",
        },
        {
            name:      "non-existent table",
            sql:       "SELECT * FROM fake_table",
            wantValid: false,
            wantError: "Table 'fake_table' does not exist",
        },
    }
    
    validator := NewSQLValidator(testSchema)
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := validator.Validate(tt.sql)
            assert.Equal(t, tt.wantValid, result.IsValid)
            if !tt.wantValid {
                assert.Contains(t, result.Errors[0], tt.wantError)
            }
        })
    }
}

func TestQueryExecutor_ExecuteWithTimeout(t *testing.T) {
    executor := NewQueryExecutor(testConnection)
    
    t.Run("query completes within timeout", func(t *testing.T) {
        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()
        
        result, err := executor.Execute(ctx, "SELECT 1")
        assert.NoError(t, err)
        assert.NotNil(t, result)
    })
    
    t.Run("query exceeds timeout", func(t *testing.T) {
        ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
        defer cancel()
        
        result, err := executor.Execute(ctx, "SELECT pg_sleep(10)")
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "context deadline exceeded")
    })
}
```

**Python Unit Tests:**
```python
# tests/test_sql_generator.py
import pytest
from sql_generator import SQLGenerator, GenerationResult

class TestSQLGenerator:
    @pytest.fixture
    def generator(self):
        return SQLGenerator(model="gpt-5.5")
    
    @pytest.fixture
    def mock_schema(self):
        return {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer"},
                        {"name": "email", "type": "varchar"},
                        {"name": "created_at", "type": "timestamp"}
                    ]
                }
            ]
        }
    
    def test_simple_query_generation(self, generator, mock_schema):
        """Test: Generate SQL for simple question"""
        result = generator.generate(
            question="Show me all users",
            schema=mock_schema
        )
        
        assert result.is_valid
        assert "SELECT" in result.sql.upper()
        assert "FROM users" in result.sql.lower()
        assert result.confidence > 0.8
    
    def test_aggregation_query(self, generator, mock_schema):
        """Test: Generate SQL with aggregation"""
        result = generator.generate(
            question="How many users do we have?",
            schema=mock_schema
        )
        
        assert result.is_valid
        assert "COUNT" in result.sql.upper()
        assert "FROM users" in result.sql.lower()
    
    def test_invalid_table_reference(self, generator, mock_schema):
        """Test: Handle reference to non-existent table"""
        result = generator.generate(
            question="Show me all orders",
            schema=mock_schema
        )
        
        # Should either fail validation or use closest match
        assert result.confidence < 0.5 or not result.is_valid
    
    def test_rag_context_improves_results(self, generator, mock_schema):
        """Test: RAG examples improve query quality"""
        examples = [
            {"question": "Show all active users", "sql": "SELECT * FROM users WHERE status = 'active'"}
        ]
        
        result_with_rag = generator.generate(
            question="Show all active users",
            schema=mock_schema,
            examples=examples
        )
        
        result_without_rag = generator.generate(
            question="Show all active users",
            schema=mock_schema,
            examples=[]
        )
        
        assert result_with_rag.confidence >= result_without_rag.confidence
```

### **2. Integration Tests (20% Coverage)**

```typescript
// tests/integration/api.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { createTestDatabase, cleanupTestDatabase } from './helpers';
import { trpc } from '@/lib/trpc';

describe('Query Generation API', () => {
  let testDb: TestDatabase;
  
  beforeAll(async () => {
    testDb = await createTestDatabase();
  });
  
  afterAll(async () => {
    await cleanupTestDatabase(testDb);
  });
  
  it('should generate SQL from natural language', async () => {
    const result = await trpc.query.generate.mutate({
      question: 'Show me all users created today',
      databaseId: testDb.id,
    });
    
    expect(result.sql).toContain('SELECT');
    expect(result.sql).toContain('users');
    expect(result.sql).toContain('created_at');
    expect(result.confidence).toBeGreaterThan(0.7);
  });
  
  it('should execute generated query and return results', async () => {
    // Insert test data
    await testDb.query('INSERT INTO users (email) VALUES ($1)', ['test@example.com']);
    
    const result = await trpc.query.execute.mutate({
      question: 'How many users do we have?',
      databaseId: testDb.id,
    });
    
    expect(result.rows).toHaveLength(1);
    expect(result.rows[0].count).toBe(1);
  });
  
  it('should reject dangerous queries', async () => {
    await expect(
      trpc.query.generate.mutate({
        question: 'Delete all users',
        databaseId: testDb.id,
      })
    ).rejects.toThrow('Forbidden operation');
  });
});
```

### **3. End-to-End Tests (10% Coverage)**

```typescript
// e2e/query-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Text-to-SQL Workflow', () => {
  test('complete query generation and execution flow', async ({ page }) => {
    // 1. Login
    await page.goto('/');
    await page.click('text=Sign In');
    await page.fill('[name=email]', 'test@example.com');
    await page.fill('[name=password]', 'password123');
    await page.click('button[type=submit]');
    
    // 2. Navigate to query page
    await page.waitForURL('/dashboard');
    await page.click('text=New Query');
    
    // 3. Select database connection
    await page.selectOption('[name=database]', { label: 'Production DB' });
    
    // 4. Enter natural language question
    await page.fill('[placeholder="Ask a question about your data"]', 
      'Show me all orders from last week');
    
    // 5. Generate SQL
    await page.click('text=Generate SQL');
    
    // Wait for AI to generate SQL
    await page.waitForSelector('.sql-editor', { timeout: 10000 });
    
    // 6. Verify SQL was generated
    const sqlContent = await page.textContent('.sql-editor');
    expect(sqlContent).toContain('SELECT');
    expect(sqlContent).toContain('orders');
    
    // 7. Execute query
    await page.click('text=Run Query');
    
    // 8. Verify results displayed
    await page.waitForSelector('.results-table');
    const resultsTable = await page.locator('.results-table');
    await expect(resultsTable).toBeVisible();
    
    // 9. Export results
    await page.click('text=Export');
    await page.click('text=Download CSV');
    
    // 10. Save query
    await page.click('text=Save Query');
    await page.fill('[name=queryName]', 'Weekly Orders Report');
    await page.click('button:has-text("Save")');
    
    await expect(page.locator('text=Query saved successfully')).toBeVisible();
  });
  
  test('should show validation errors for invalid queries', async ({ page }) => {
    await page.goto('/dashboard/query');
    
    await page.fill('[placeholder="Ask a question"]', 'DROP TABLE users');
    await page.click('text=Generate SQL');
    
    await expect(page.locator('.error-message')).toContainText(
      'Forbidden operation: DROP'
    );
  });
});
```

### **4. Property-Based Testing**

```python
# tests/property/test_sql_correctness.py
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule
import sqlglot

class SQLGenerationStateMachine(RuleBasedStateMachine):
    """Property-based tests for SQL generation correctness"""
    
    def __init__(self):
        super().__init__()
        self.generator = SQLGenerator()
        self.schema = load_test_schema()
    
    @rule(question=st.text(min_size=10, max_size=200))
    def test_generated_sql_is_parseable(self, question):
        """Property: All generated SQL must be syntactically valid"""
        result = self.generator.generate(question, self.schema)
        
        if result.is_valid:
            # Should parse without errors
            parsed = sqlglot.parse(result.sql, dialect='postgres')
            assert len(parsed) > 0
    
    @rule(question=st.text(min_size=10, max_size=200))
    def test_generated_sql_only_references_existing_tables(self, question):
        """Property: Generated SQL must only reference tables in schema"""
        result = self.generator.generate(question, self.schema)
        
        if result.is_valid:
            tables = extract_tables_from_sql(result.sql)
            schema_tables = {t['name'] for t in self.schema['tables']}
            
            assert tables.issubset(schema_tables)
    
    @rule(question=st.text(min_size=10, max_size=200))
    def test_no_dangerous_operations_in_generated_sql(self, question):
        """Property: Generated SQL must never contain dangerous operations"""
        result = self.generator.generate(question, self.schema)
        
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 'ALTER']
        sql_upper = result.sql.upper()
        
        for keyword in dangerous:
            assert keyword not in sql_upper

TestSQLGeneration = SQLGenerationStateMachine.TestCase
```

### **5. Load & Performance Testing**

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class TextToSQLUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login once per user"""
        response = self.client.post("/api/auth/login", json={
            "email": "load-test@example.com",
            "password": "test123"
        })
        self.token = response.json()["token"]
    
    @task(3)
    def generate_simple_query(self):
        """Simulate simple query generation (70% of traffic)"""
        self.client.post(
            "/api/query/generate",
            json={
                "question": "Show me all users",
                "databaseId": "test-db-123"
            },
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/query/generate [simple]"
        )
    
    @task(2)
    def generate_complex_query(self):
        """Simulate complex query with joins (20% of traffic)"""
        self.client.post(
            "/api/query/generate",
            json={
                "question": "Show me total revenue per customer for last quarter",
                "databaseId": "test-db-123"
            },
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/query/generate [complex]"
        )
    
    @task(1)
    def execute_query(self):
        """Simulate query execution (10% of traffic)"""
        self.client.post(
            "/api/query/execute",
            json={
                "sql": "SELECT * FROM users LIMIT 100",
                "databaseId": "test-db-123"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )

# Run: locust -f locustfile.py --host=https://api.yourapp.com
# Target: 1000 concurrent users, 95th percentile < 2s
```

### **Test Coverage Requirements**

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|-----------------|
| Core SQL Generation | 85% | 95% |
| Validation Layer | 90% | 98% |
| API Endpoints | 80% | 90% |
| Database Connectors | 75% | 85% |
| Frontend Components | 70% | 80% |

---

## 📊 Performance Targets

| Metric | Target | Acceptable | Unacceptable |
|--------|--------|------------|--------------|
| SQL Generation Time | < 2s | < 5s | > 10s |
| Query Execution Time | < 5s | < 15s | > 30s |
| Schema Caching Hit Rate | > 95% | > 85% | < 70% |
| API Response Time (p95) | < 500ms | < 1s | > 2s |
| Concurrent Users | 1000+ | 500+ | < 100 |
| Database Connections | 50+ pooled | 20+ | < 10 |
| Vector Search Latency | < 100ms | < 300ms | > 500ms |
| Monthly AI API Cost | < $500 | < $1000 | > $2000 |

---

## 🚀 Production-Ready Checklist

### **Infrastructure**
- ✅ Multi-region deployment (US-East, EU-West, Asia-Pacific)
- ✅ Auto-scaling (Kubernetes HPA)
- ✅ Load balancing (ALB/NLB)
- ✅ CDN for static assets (Cloudflare)
- ✅ Database replication (read replicas)
- ✅ Redis cluster for caching
- ✅ Message queue for async jobs (RabbitMQ/SQS)

### **Monitoring & Observability**
- ✅ APM (Sentry, Datadog)
- ✅ Structured logging (Axiom)
- ✅ Distributed tracing (OpenTelemetry)
- ✅ Metrics dashboard (Grafana)
- ✅ Error tracking with alerting
- ✅ Query performance monitoring
- ✅ AI cost tracking

### **Security**
- ✅ WAF (Web Application Firewall)
- ✅ DDoS protection (Cloudflare)
- ✅ Rate limiting (Unkey)
- ✅ Secret management (Vault)
- ✅ Encryption at rest & in transit
- ✅ Regular security audits
- ✅ Penetration testing
- ✅ SOC2 compliance

### **Reliability**
- ✅ 99.9% uptime SLA
- ✅ Automated backups (hourly)
- ✅ Point-in-time recovery (PITR)
- ✅ Disaster recovery plan
- ✅ Incident response playbook
- ✅ Chaos engineering tests
- ✅ Circuit breakers for external APIs

### **CI/CD Pipeline**
```yaml
# .github/workflows/production.yml
name: Production Deployment

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Golang tests
      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      
      - name: Run Go tests
        run: |
          go test -v -race -coverprofile=coverage.out ./...
          go tool cover -func=coverage.out
      
      # Python tests
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Run Python tests
        run: |
          pip install -r requirements.txt
          pytest --cov=. --cov-report=xml
      
      # Frontend tests
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'
      
      - name: Run frontend tests
        run: |
          npm ci
          npm run test:unit
          npm run test:e2e
      
      # Security scanning
      - name: Run security scan
        run: |
          npm audit
          go run golang.org/x/vuln/cmd/govulncheck@latest ./...
      
      # Code quality
      - name: SonarQube Scan
        uses: sonarsource/sonarcloud-github-action@master
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: |
          docker build -t text-to-sql-backend:${{ github.sha }} ./backend
          docker build -t text-to-sql-frontend:${{ github.sha }} ./frontend
      
      - name: Push to registry
        run: |
          docker push text-to-sql-backend:${{ github.sha }}
          docker push text-to-sql-frontend:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend backend=text-to-sql-backend:${{ github.sha }}
          kubectl set image deployment/frontend frontend=text-to-sql-frontend:${{ github.sha }}
          kubectl rollout status deployment/backend
          kubectl rollout status deployment/frontend
      
      - name: Run smoke tests
        run: ./scripts/smoke-tests.sh
      
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
```

---

## 🔄 Future Enhancements

### **Phase 2: Advanced Features (Q3 2026)**

#### **1. Multi-Database Support Expansion**
**Priority:** High | **Effort:** Medium
- Add Snowflake, BigQuery, Redshift connectors
- Cross-database query federation
- Automatic dialect translation

#### **2. Natural Language Data Insights**
**Priority:** High | **Effort:** High
- Auto-generate insights from query results
- Trend detection and anomaly highlighting
- Executive summary generation

#### **3. Query Optimization Suggestions**
**Priority:** Medium | **Effort:** Medium
- AI-powered index recommendations
- Query rewrite suggestions for performance
- Cost estimation for cloud databases

#### **4. Collaborative Features**
**Priority:** Medium | **Effort:** Medium
- Shared query workspaces
- Real-time collaborative editing
- Query review and approval workflows
- Team query library

#### **5. Scheduled Queries & Alerts**
**Priority:** High | **Effort:** Medium
- Cron-based query scheduling
- Email/Slack alerts on threshold breach
- Automated report generation
- Data export to external systems

#### **6. Voice-to-SQL**
**Priority:** Low | **Effort:** High
- Speech-to-text integration (Deepgram)
- Voice command query execution
- Multi-language voice support

#### **7. Mobile Apps**
**Priority:** Low | **Effort:** Very High
- iOS/Android apps (React Native)
- Offline query history
- Push notifications for query completion

---

## 📚 Technology Stack Summary

### **Backend Services**

| Service | Language | Framework | Purpose |
|---------|----------|-----------|---------|
| API Gateway | Golang | Hono | Request routing, auth |
| SQL Generator | Python | FastAPI | AI query generation |
| Query Executor | Golang | pgx | Database operations |
| Schema Analyzer | Golang | database/sql | Schema introspection |
| Cache Layer | Golang | go-redis | Redis management |
| Background Jobs | Golang | Asynq | Async task processing |

### **Frontend**
- **Framework:** Next.js 16 (App Router)
- **UI Library:** React 19.2.7
- **Styling:** Tailwind CSS 4.x
- **Components:** shadcn/ui
- **Editor:** Monaco Editor
- **Visualizations:** Recharts, AG Grid, React Flow

### **AI/ML**
- **Primary LLM:** GPT-5.5 (OpenAI)
- **Secondary LLM:** Claude Opus 4.8 (Anthropic)
- **Orchestration:** LangChain
- **Vector DB:** Upstash Vector
- **Embeddings:** text-embedding-3-large

### **Infrastructure**
- **Container:** Docker
- **Orchestration:** Kubernetes
- **Cloud:** AWS/GCP (multi-cloud)
- **CDN:** Cloudflare
- **Monitoring:** Sentry, Axiom, Datadog
- **Secrets:** HashiCorp Vault

---

## 💰 Pricing Model (Suggested)

### **Free Tier**
- 100 queries per month
- 1 database connection
- Basic query history (7 days)
- Community support

### **Pro Tier** ($29/month)
- 1,000 queries per month
- 5 database connections
- Advanced query history (90 days)
- Priority support
- Query optimization suggestions
- Export to CSV/Excel

### **Team Tier** ($99/month)
- 5,000 queries per month
- Unlimited database connections
- Unlimited query history
- Collaborative workspaces
- SSO integration
- API access
- Custom query templates

### **Enterprise** (Custom)
- Unlimited queries
- On-premise deployment
- Custom AI model fine-tuning
- Dedicated support
- SLA guarantees
- Advanced security features
- Custom integrations

---

## 📈 Success Metrics

### **Technical KPIs**
- SQL generation accuracy: > 90%
- Query execution success rate: > 95%
- Average response time: < 3s
- System uptime: 99.9%
- Test coverage: > 85%

### **Business KPIs**
- Monthly Active Users (MAU): 10,000+
- Query volume: 100,000+ per month
- User satisfaction (NPS): > 50
- Conversion rate (free → paid): > 5%
- Monthly recurring revenue (MRR): $50,000+

---

## ✨ Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 18, 2026 | Initial document with production-ready TDD approach |

---

**Document Version:** 1.0  
**Last Updated:** June 18, 2026  
**Tech Stack:** Golang + Python + Next.js 16  
**Development Approach:** Test-Driven Development (TDD)  
**Production Status:** Enterprise-Ready Architecture  
**Next Review:** September 18, 2026

---

## 📞 Contact & Resources

- **Technical Lead:** TBD
- **Product Manager:** TBD
- **Architecture Review:** Required before implementation
- **Estimated Timeline:** 6-9 months to production
- **Team Size:** 2 Backend (Go), 1 Backend (Python), 1 Frontend, 1 DevOps, 1 QA

---

**End of Document**
