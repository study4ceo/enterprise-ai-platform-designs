# Design Document: Threat Modeling Platform

## Document Information

**Document Version:** 1.0  
**Last Updated:** June 24, 2026  
**Status:** Draft  
**Author:** AI Systems Architecture Team  
**Related Documents:** 
- Requirements: `.kiro/specs/threat-modeling-platform/requirements.md`
- Architecture: `project-designs/threat_modeling_platform/architecture.md`
- System Diagrams: `project-designs/threat_modeling_platform/system-diagrams.md`

---

## Executive Summary

### Platform Overview

The Threat Modeling Platform is an enterprise-grade, AI-powered security analysis system designed to automate threat identification, vulnerability assessment, and risk analysis for complex software systems and cloud infrastructure. The platform addresses the critical challenge of conducting comprehensive security threat modeling at scale by combining artificial intelligence, graph database technology, and industry-standard security frameworks.

**Core Value Proposition:**
- Reduce threat modeling time from weeks to hours through AI-powered automation
- Enable security-by-design through CI/CD pipeline integration
- Provide actionable, prioritized security recommendations with minimal security expertise required
- Ensure regulatory compliance through automated framework mapping (GDPR, SOC 2, ISO 27001, HIPAA)
- Track security posture evolution through versioned threat models and trend analysis

### Key Capabilities

**1. Multi-Framework Threat Analysis**
- Support for STRIDE, PASTA, VAST, and Attack Tree frameworks
- Cross-framework threat mapping and correlation
- Framework-specific analysis tailored to different stakeholder needs

**2. AI-Powered Threat Identification**
- Dual-AI analysis using GPT-4o and Claude Opus 4 for comprehensive threat coverage
- Automated identification of 20+ threats per architecture analysis
- Pattern matching against OWASP Top 10, CWE Top 25, and MITRE ATT&CK

**3. Graph-Based Threat Modeling**
- Neo4j-powered threat graph with multi-hop attack path analysis
- Complex relationship queries identifying cascading security impacts
- Temporal tracking of threat evolution and mitigation status

**4. Automated Risk Scoring**
- Likelihood and impact scoring algorithms
- CVSS integration for known vulnerabilities
- Risk-based prioritization for remediation efforts

**5. Compliance Automation**
- Automated mapping to GDPR, SOC 2, ISO 27001, HIPAA, PCI-DSS
- Compliance gap analysis and evidence generation
- Audit-ready documentation and reporting

**6. DevSecOps Integration**
- CI/CD pipeline integration with automated threat analysis
- Issue tracking system integration (Jira, GitHub, Azure DevOps)
- Policy-as-code enforcement and deployment gates

### Technical Highlights

**Performance Characteristics:**
- Sub-5-second threat identification for typical architectures (20-50 components)
- 5-minute complete analysis for enterprise architectures (500+ components)
- 100ms vector similarity search across 50,000+ threat patterns
- 2-second graph queries for 5-hop relationship traversals
- 100 concurrent users without performance degradation

**Scalability:**
- 100,000+ threat nodes in graph database
- 1,000,000+ relationship edges
- 50,000+ threat pattern embeddings in vector store
- Horizontal scaling through worker node addition
- 90% cache hit rate for repeat analyses

**Reliability:**
- 99.9% uptime SLA (43.8 minutes maximum downtime monthly)
- Geographic redundancy with 6-hour backup intervals
- 30-second automatic failover
- 2-year threat model retention
- AES-256 encryption at rest, TLS 1.3 in transit

---

## System Architecture

### High-Level Architecture


The Threat Modeling Platform follows a **layered microservices architecture** with clear separation of concerns:

**Architecture Layers:**

1. **Presentation Layer**
   - Web UI (Next.js 16.0 + React 19)
   - REST API Gateway
   - GraphQL API
   - CLI Tools

2. **Application Layer**
   - Threat Analyzer Service (AI-powered threat identification)
   - Architecture Parser Service (multi-format ingestion)
   - Risk Calculator Service (scoring and prioritization)
   - Mitigation Generator Service (recommendation engine)
   - Compliance Mapper Service (regulatory mapping)
   - Ticket Creator Service (issue tracking integration)

3. **Domain Layer**
   - Framework Engine (STRIDE, PASTA, VAST, Attack Trees)
   - Attack Surface Mapper (entry point analysis)
   - Data Flow Analyzer (sensitive data tracking)
   - Security Control Verifier (control gap analysis)
   - Threat Pattern Matcher (vector similarity search)

4. **Data Layer**
   - Neo4j 5.26 (Threat Graph Database)
   - PostgreSQL 17.2 (Structured Data, Metadata)
   - Qdrant 1.12 (Vector Store for Threat Patterns)
   - Redis 7.4 (Caching, Session Management)

5. **Integration Layer**
   - External Threat Intelligence Feeds (NVD, MITRE ATT&CK, CVE)
   - Issue Tracking Systems (Jira, GitHub, Azure DevOps)
   - CI/CD Platforms (GitHub Actions, GitLab CI, Jenkins)
   - Infrastructure-as-Code Repositories (Terraform, CloudFormation, Kubernetes)
   - Policy-as-Code Engines (Open Policy Agent, Cloud Custodian)

6. **Infrastructure Layer**
   - Kubernetes 1.32 (Container Orchestration)
   - Kafka 3.8 (Event Streaming, Async Processing)
   - Message Queue (Task Distribution)
   - Object Storage (Architecture Diagrams, Reports)
   - Monitoring & Observability Stack

**Architectural Principles:**

- **Microservices:** Each component independently deployable and scalable
- **Event-Driven:** Asynchronous processing via Kafka for long-running analyses
- **API-First:** All functionality exposed through REST/GraphQL APIs
- **Database Per Service:** Each service owns its data store
- **Eventual Consistency:** Distributed transactions via Saga pattern
- **Caching Strategy:** Multi-level caching (Redis, in-memory, CDN)
- **Security by Design:** Zero-trust architecture with mTLS between services

---

## Technology Stack

### Backend Services

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Golang** | 1.26.4 | High-performance services | Performance-critical services (API Gateway, Risk Calculator) requiring low latency and high throughput |
| **Python** | 3.13 | AI/ML services | AI orchestration, LangChain integration, ML model serving, data science workflows |
| **FastAPI** | 0.110 | Python microservices framework | High-performance async Python framework with automatic OpenAPI documentation |
| **Gin** | 1.10 | Go web framework | Fast HTTP router and middleware for Go services |
| **gRPC** | Latest | Inter-service communication | High-performance RPC for service-to-service communication |

### AI & Machine Learning

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **GPT-4o** | Latest | Primary threat identification | OpenAI's most capable model for security analysis and threat description generation |
| **Claude Opus 4** | Latest | Secondary threat validation | Anthropic's Claude for cross-validation and reducing AI hallucination |
| **LangChain** | 0.4 | AI orchestration framework | Unified framework for LLM integration, prompt management, and agent workflows |
| **LangSmith** | Latest | LLM observability | Monitoring, debugging, and optimizing LLM chains and agents |
| **Sentence Transformers** | 3.0 | Embedding generation | Creating vector embeddings for threat pattern matching |
| **scikit-learn** | 1.5 | Risk scoring ML | Likelihood and impact prediction models |


### Databases & Storage

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Neo4j** | 5.26 | Threat graph database | Native graph database for complex threat relationships, attack paths, multi-hop queries |
| **PostgreSQL** | 17.2 | Structured data | Threat models metadata, user data, audit logs, configuration |
| **Qdrant** | 1.12 | Vector database | High-performance vector similarity search for threat pattern matching |
| **Redis** | 7.4 | Caching & session store | In-memory caching, session management, rate limiting, pub/sub |
| **S3-Compatible Storage** | - | Object storage | Architecture diagrams, generated reports, backup storage |
| **TimescaleDB** | 2.18 | Time-series data | Threat evolution tracking, risk score history, metrics |

### Message Queue & Event Streaming

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Apache Kafka** | 3.8 | Event streaming | High-throughput event streaming for async threat analysis, CI/CD integration |
| **Kafka Streams** | 3.8 | Stream processing | Real-time threat intelligence feed processing |
| **Kafka Connect** | 3.8 | Data integration | Connector framework for external system integration |

### Frontend

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Next.js** | 16.0 | React framework | Server-side rendering, routing, API routes, optimal performance |
| **React** | 19 | UI library | Component-based UI development with latest concurrent features |
| **TypeScript** | 5.7 | Type safety | Static typing for large-scale frontend development |
| **TanStack Query** | 5.0 | Data fetching | Powerful async state management and caching |
| **Zustand** | 4.5 | State management | Lightweight state management for global UI state |
| **Recharts** | 2.12 | Data visualization | Risk score charts, threat trends, attack surface visualization |
| **React Flow** | 11.11 | Graph visualization | Interactive threat graph and architecture diagram rendering |
| **Tailwind CSS** | 4.0 | Styling | Utility-first CSS framework for rapid UI development |


### Infrastructure & DevOps

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Kubernetes** | 1.32 | Container orchestration | Industry-standard container orchestration for scalability and reliability |
| **Docker** | 27 | Containerization | Container runtime for all microservices |
| **Helm** | 3.15 | Kubernetes package manager | Chart-based deployment management |
| **Terraform** | 1.9 | Infrastructure-as-Code | Multi-cloud infrastructure provisioning |
| **ArgoCD** | 2.11 | GitOps CD | Declarative continuous deployment for Kubernetes |
| **Istio** | 1.22 | Service mesh | mTLS, traffic management, observability for microservices |
| **Cert-Manager** | 1.15 | Certificate management | Automated TLS certificate provisioning |
| **NGINX Ingress** | 1.11 | Ingress controller | External traffic routing into Kubernetes cluster |

### Monitoring & Observability

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Prometheus** | Latest | Metrics collection | Time-series metrics database and alerting |
| **Grafana** | Latest | Metrics visualization | Dashboards for system health, performance, business metrics |
| **Logfire** | Latest | Distributed tracing | End-to-end request tracing across microservices |
| **OpenTelemetry** | Latest | Observability framework | Unified observability instrumentation |
| **Elasticsearch** | 8.14 | Log aggregation | Centralized logging and log search |
| **Kibana** | 8.14 | Log visualization | Log analysis and visualization dashboards |
| **AlertManager** | Latest | Alert routing | Intelligent alert routing, grouping, silencing |

### Security & Compliance

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Keycloak** | 24 | Identity & access management | OAuth 2.0, OpenID Connect, SAML 2.0 authentication |
| **Vault** | 1.17 | Secrets management | Centralized secrets storage, dynamic credentials, encryption-as-a-service |
| **Open Policy Agent** | 0.64 | Policy engine | Fine-grained authorization policies as code |
| **Trivy** | Latest | Vulnerability scanning | Container and IaC security scanning |
| **Falco** | Latest | Runtime security | Kubernetes runtime threat detection |

---

## Core Components

### 1. Threat Analyzer (AI-Powered Threat Identification)

**Responsibility:** Automatically identify security threats in system architectures using dual-AI analysis.

**Architecture:**

The Threat Analyzer employs a **dual-AI validation pattern** where both GPT-4o and Claude Opus 4 independently analyze the same architecture, with results cross-validated to reduce hallucinations and improve accuracy.

**Key Design Elements:**

- **Multi-Model Analysis:** Parallel threat identification using both LLMs
- **Consensus Validation:** Threats identified by both models prioritized
- **Hallucination Reduction:** Cross-model validation filters false positives
- **Context Window Management:** Architecture chunking for large systems
- **Prompt Engineering:** Framework-specific prompts optimized for each analysis type

**Processing Pipeline:**

1. **Input Normalization:** Convert architecture to standardized internal representation
2. **Context Building:** Assemble relevant threat patterns, previous threats, compliance requirements
3. **Parallel AI Analysis:** Invoke GPT-4o and Claude simultaneously with framework-specific prompts
4. **Result Correlation:** Match threats across both AI responses
5. **Threat Enrichment:** Add CVE mappings, CWE classifications, MITRE ATT&CK TTPs
6. **Graph Integration:** Store threats and relationships in Neo4j
7. **Vector Embedding:** Generate embeddings for future similarity matching

**AI Orchestration:**

Uses LangChain chains for structured LLM interactions with:
- Retry logic with exponential backoff
- Token usage tracking and optimization
- Streaming responses for real-time UI updates
- Output parsing and validation schemas
- Prompt caching for repeated analyses

**Threat Categories Detected:**

- Authentication & Authorization (broken auth, privilege escalation, session fixation)
- Injection Attacks (SQL, NoSQL, command, LDAP, XML injection)
- Data Exposure (sensitive data leakage, PII exposure, encryption gaps)
- Cryptography (weak algorithms, improper key management, broken crypto)
- Configuration (default credentials, misconfigured CORS, insecure headers)
- Denial of Service (resource exhaustion, amplification attacks)
- Supply Chain (vulnerable dependencies, compromised components)
- API Security (missing rate limiting, broken authentication, mass assignment)


### 2. Architecture Parser

**Responsibility:** Ingest and parse system architecture descriptions in multiple formats into structured internal representation.

**Architecture:**

Multi-format parser using **plugin architecture** where each format has dedicated parser module. Parsers convert diverse inputs into unified Architecture Model.

**Supported Input Formats:**

- **Markdown:** Structured text descriptions with component lists, data flows
- **PlantUML:** UML diagrams (component, deployment, sequence diagrams)
- **Mermaid:** Flowcharts, sequence diagrams, C4 diagrams
- **JSON/YAML:** Structured architecture specifications
- **Architecture Diagrams (Images):** PNG, JPG, SVG processed via GPT-4 Vision

**Architecture Model Schema:**

Unified internal representation consisting of:
- **Components:** Services, databases, APIs, external systems with properties
- **Data Flows:** Connections between components with protocols, data types, encryption
- **Trust Boundaries:** Security perimeters, network zones, privilege levels
- **Assets:** Resources requiring protection with criticality ratings
- **Security Controls:** Existing protections (WAF, encryption, auth mechanisms)
- **Metadata:** System name, version, environment, technology stack

**Parsing Strategy:**

1. **Format Detection:** Auto-detect input format via content analysis
2. **Syntax Validation:** Verify format-specific syntax correctness
3. **Entity Extraction:** Identify components, connections, boundaries
4. **Relationship Building:** Construct data flow graph
5. **Trust Boundary Inference:** Auto-detect boundaries based on network zones, auth changes
6. **Semantic Validation:** Check logical consistency (orphaned components, circular dependencies)
7. **Model Normalization:** Convert to canonical Architecture Model

**Computer Vision Integration:**

For image-based diagrams:
- GPT-4 Vision extracts components and connections
- Heuristics identify standard diagram notations (boxes = components, arrows = flows)
- Confidence scoring for uncertain extractions
- Human review workflow for low-confidence parses

**Round-Trip Support:**

Pretty Printer component generates outputs matching input formats from Architecture Model, enabling:
- Validation of parse accuracy through round-trip testing
- Format conversion (Mermaid → PlantUML)
- Normalized representation for threat analysis


### 3. Framework Engine (STRIDE, PASTA, VAST, Attack Trees)

**Responsibility:** Apply multiple threat modeling frameworks to architecture analysis.

**Architecture:**

**Strategy Pattern implementation** where each framework is a pluggable strategy with common interface but framework-specific analysis logic.

**Framework Implementations:**

**STRIDE Framework:**
- **Spoofing:** Identity and authentication threats
- **Tampering:** Data integrity threats
- **Repudiation:** Non-auditable actions threats
- **Information Disclosure:** Data confidentiality threats
- **Denial of Service:** Availability threats
- **Elevation of Privilege:** Authorization threats

Analysis maps each component and data flow to STRIDE categories.

**PASTA Framework:**
- **Stage 1:** Define business objectives (asset criticality, business impact)
- **Stage 2:** Define technical scope (components, boundaries, tech stack)
- **Stage 3:** Application decomposition (architecture breakdown)
- **Stage 4:** Threat analysis (identify threats per component)
- **Stage 5:** Vulnerability analysis (map threats to vulnerabilities)
- **Stage 6:** Attack enumeration (identify attack vectors and TTPs)
- **Stage 7:** Risk and impact analysis (calculate risk scores)

Sequential stage execution with outputs feeding subsequent stages.

**VAST Framework:**
- **Application Threat Models:** Developer-focused, operational diagrams (process flow diagrams, threat-event tables)
- **Operational Threat Models:** Infrastructure-focused, attacker perspective (attack trees, abuse cases)

Generates two parallel models optimized for different audiences.

**Attack Trees:**
- Hierarchical tree structures with root goal (compromise system)
- AND gates: multiple conditions required
- OR gates: alternative attack paths
- Leaf nodes: atomic attack actions
- Assigns likelihood to each path

Graph-based representation in Neo4j enables attack path queries.

**Framework Correlation:**

Cross-framework mapper identifies equivalent threats:
- STRIDE Information Disclosure ↔ PASTA Data Exposure ↔ VAST Data Leakage Event
- STRIDE Elevation of Privilege ↔ PASTA Authorization Bypass ↔ VAST Privilege Escalation Attack

Unified threat identifier enables tracking across frameworks.


### 4. Threat Graph (Neo4j Graph Database)

**Responsibility:** Store threats, vulnerabilities, assets, and their complex relationships in graph structure enabling multi-hop attack path analysis.

**Architecture:**

**Graph Schema:**

**Node Types:**
- `Threat` - Security threats with description, category, framework classification
- `Vulnerability` - Exploitable weaknesses (CVE, CWE, custom)
- `Asset` - Protected resources (services, databases, data)
- `Component` - Architecture elements (microservices, APIs, databases)
- `ThreatActor` - Attacker profiles (insider, cybercriminal, nation-state)
- `AttackVector` - Attack methods and techniques
- `Mitigation` - Security controls and countermeasures
- `ComplianceRequirement` - Regulatory requirements
- `ThreatModel` - Complete analysis for system version

**Relationship Types:**
- `EXPLOITS` - Threat → Vulnerability
- `AFFECTS` - Threat → Asset/Component
- `MITIGATES` - Mitigation → Threat
- `REQUIRES` - AttackVector → Vulnerability
- `LEADS_TO` - Threat → Threat (attack chains)
- `IMPLEMENTS` - Component → Mitigation
- `SATISFIES` - Mitigation → ComplianceRequirement
- `PART_OF` - Threat → ThreatModel
- `DEPENDS_ON` - Component → Component

**Graph Queries:**

Attack Path Discovery:
```cypher
// Find all attack paths from external attacker to database
MATCH path = (actor:ThreatActor {type: 'external'})
  -[:EXECUTES]->(:AttackVector)
  -[:EXPLOITS]->(vuln:Vulnerability)
  <-[:CONTAINS]-(component:Component)
  -[:LEADS_TO*1..5]->(target:Asset {type: 'database'})
RETURN path
```

Risk Analysis:
```cypher
// Find unmitigated critical threats
MATCH (t:Threat {riskLevel: 'Critical'})
WHERE NOT EXISTS {
  (t)<-[:MITIGATES]-(:Mitigation)
}
RETURN t
```

Compliance Gaps:
```cypher
// Find compliance requirements without mitigations
MATCH (req:ComplianceRequirement)
WHERE NOT EXISTS {
  (req)<-[:SATISFIES]-(:Mitigation)
}
RETURN req.framework, req.control, req.description
```

**Temporal Tracking:**

Nodes include temporal properties:
- `createdAt` - Threat identification timestamp
- `updatedAt` - Last modification
- `resolvedAt` - Mitigation implementation date
- `riskScoreHistory` - Array of risk score changes

Enables trend analysis and security posture tracking.


### 5. Risk Calculator

**Responsibility:** Calculate threat likelihood and impact scores, combining them into overall risk scores for prioritization.

**Architecture:**

**Multi-Factor Scoring Engine** combining quantitative and qualitative factors.

**Likelihood Score Calculation (0-100):**

Factors considered:
- **Threat Actor Capability:** Nation-state (90), Organized crime (70), Skilled individual (50), Script kiddie (20)
- **Attack Complexity:** Low (80), Medium (50), High (20)
- **Required Privileges:** None (90), Low (60), High (30)
- **User Interaction:** None (90), Required (40)
- **Existing Controls Effectiveness:** None (100), Weak (70), Moderate (40), Strong (10)
- **Exploit Availability:** Public exploit (90), Proof-of-concept (60), Theoretical (30)
- **Attack Surface Exposure:** Internet-facing (90), Internal (50), Air-gapped (10)

Weighted combination:
```
Likelihood = (
  ThreatActorCapability × 0.20 +
  AttackComplexity × 0.20 +
  RequiredPrivileges × 0.15 +
  UserInteraction × 0.10 +
  ControlEffectiveness × 0.20 +
  ExploitAvailability × 0.10 +
  Exposure × 0.05
)
```

**Impact Score Calculation (0-100):**

Factors considered:
- **Asset Criticality:** Business-critical (100), Important (70), Standard (40), Low (20)
- **Data Sensitivity:** Restricted (100), Confidential (70), Internal (40), Public (10)
- **Confidentiality Impact:** High (90), Moderate (50), Low (20), None (0)
- **Integrity Impact:** High (90), Moderate (50), Low (20), None (0)
- **Availability Impact:** High (90), Moderate (50), Low (20), None (0)
- **Financial Impact:** >$1M (100), $100K-$1M (70), $10K-$100K (40), <$10K (20)
- **Compliance Impact:** Major violation (100), Minor violation (50), No impact (0)
- **Reputation Impact:** Severe (100), Moderate (60), Minor (30), None (0)

Weighted combination:
```
Impact = (
  AssetCriticality × 0.25 +
  DataSensitivity × 0.20 +
  MAX(C_Impact, I_Impact, A_Impact) × 0.20 +
  FinancialImpact × 0.15 +
  ComplianceImpact × 0.10 +
  ReputationImpact × 0.10
)
```

**Risk Score:**
```
Risk = (Likelihood × Impact) / 100
```

**Risk Levels:**
- Critical: 80-100 (immediate action required)
- High: 60-79 (prioritize remediation)
- Medium: 40-59 (schedule remediation)
- Low: 20-39 (address in backlog)
- Informational: 0-19 (monitor)


**CVSS Integration:**

For threats mapped to CVEs:
- Import CVSS base score (exploitability + impact metrics)
- Apply temporal score (exploit maturity, remediation level, report confidence)
- Apply environmental score (modified impact based on asset criticality)
- Use CVSS score when higher than calculated risk score

**Machine Learning Enhancement:**

Over time, ML models learn from:
- Historical threat outcomes (false positives, true positives)
- Mitigation effectiveness
- Organization-specific risk tolerance
- Incident correlation

Models refine likelihood and impact predictions through:
- Gradient boosting (XGBoost) for score prediction
- Logistic regression for risk level classification
- Feature importance analysis identifying key risk drivers


### 6. Mitigation Generator (AI-Powered Recommendations)

**Responsibility:** Generate actionable, context-specific mitigation recommendations for identified threats using AI.

**Architecture:**

**RAG-Enhanced Generation Pipeline:**

Uses **Retrieval-Augmented Generation** combining:
- Threat-specific context from graph database
- Similar historical mitigations from vector store
- Security best practices knowledge base
- Technology-specific implementation guides

**Generation Process:**

1. **Threat Context Assembly:**
   - Extract threat details (category, affected components, attack vectors)
   - Query graph for related vulnerabilities and existing controls
   - Retrieve system technology stack and constraints

2. **Similar Mitigation Retrieval:**
   - Generate threat embedding using Sentence Transformers
   - Query Qdrant vector store for similar threats
   - Extract mitigation strategies from similar cases
   - Rank by similarity score and effectiveness metrics

3. **Knowledge Base Consultation:**
   - Query best practices (OWASP Cheat Sheets, NIST Guidelines, CIS Benchmarks)
   - Extract technology-specific recommendations (AWS Well-Architected, Azure Security Baseline)
   - Retrieve compliance-mandated controls

4. **AI-Powered Synthesis:**
   - LangChain chain combines context + retrieved knowledge + prompts
   - GPT-4o generates 3-5 mitigation options
   - Each mitigation includes: description, implementation steps, code/config examples, effort estimate, effectiveness rating

5. **Prioritization & Validation:**
   - Rank mitigations by effectiveness/effort ratio
   - Validate against existing controls (avoid duplicates)
   - Check compliance requirement satisfaction
   - Estimate risk reduction (post-mitigation risk score)

**Mitigation Categories:**

- **Preventive Controls:** Stop attacks before they occur (input validation, encryption, authentication)
- **Detective Controls:** Identify attacks in progress (logging, monitoring, intrusion detection)
- **Corrective Controls:** Respond to attacks (incident response, backups, disaster recovery)
- **Compensating Controls:** Alternative protections when direct mitigation infeasible

**Implementation Guidance:**

Each mitigation includes:
- Technical approach description
- Recommended technologies/libraries
- Configuration templates
- Code snippets (if applicable)
- Testing recommendations
- Deployment considerations
- Operational impact analysis


### 7. Compliance Mapper

**Responsibility:** Map threats and mitigations to regulatory compliance frameworks for audit and gap analysis.

**Architecture:**

**Rule-Based Mapping Engine** with curated compliance knowledge base.

**Supported Frameworks:**

**GDPR (General Data Protection Regulation):**
- Article 25: Data protection by design and by default
- Article 32: Security of processing (encryption, pseudonymization, resilience)
- Article 33: Breach notification (72-hour requirement)
- Article 34: Data subject notification

**SOC 2 (Trust Services Criteria):**
- CC6.1-CC6.8: Security controls (logical access, authentication, encryption)
- A1.1-A1.3: Availability (backup, disaster recovery, capacity planning)
- C1.1-C1.2: Confidentiality (data classification, encryption)

**ISO 27001:2022:**
- Annex A controls: 93 controls across 4 domains
  - Organizational (5.1-5.37): Policies, risk assessment, awareness
  - People (6.1-6.8): Screening, responsibilities, discipline
  - Physical (7.1-7.14): Secure areas, equipment security
  - Technological (8.1-8.34): Encryption, access control, malware

**HIPAA Security Rule:**
- Administrative Safeguards (§164.308): Risk analysis, workforce security, contingency planning
- Physical Safeguards (§164.310): Facility access, workstation security, device controls
- Technical Safeguards (§164.312): Access controls, audit controls, integrity, transmission security

**PCI-DSS v4.0:**
- 12 requirements covering network security, cardholder data protection, access control

**Mapping Logic:**

1. **Threat → Control Mapping:**
   - Each threat type maps to required controls
   - Example: SQL Injection → OWASP Top 10 A03 → PCI-DSS 6.2 (Secure SDLC) → ISO 27001 8.28 (Secure coding)

2. **Control → Requirement Mapping:**
   - Security controls satisfy specific compliance requirements
   - Example: Encryption at rest → GDPR Article 32(1)(a) → HIPAA §164.312(a)(2)(iv) → ISO 27001 8.24

3. **Gap Analysis:**
   - Identify threats without adequate controls
   - Identify compliance requirements without implemented controls
   - Calculate compliance coverage percentage

**Compliance Report Generation:**

- Control matrix: threats × compliance requirements
- Gap analysis: missing controls per framework
- Evidence artifacts: configurations, logs, policies satisfying requirements
- Audit readiness score per framework


### 8. Attack Surface Mapper

**Responsibility:** Identify and map all entry points where attackers could interact with the system.

**Architecture:**

**Graph Traversal Analysis** starting from external-facing components and mapping inward.

**Entry Point Discovery:**

Identifies all external interfaces:
- **Public APIs:** REST, GraphQL, gRPC endpoints
- **Web Applications:** SPAs, server-rendered apps, admin panels
- **Mobile App Backends:** API gateways, push notification services
- **Third-Party Integrations:** OAuth callbacks, webhooks, API consumers
- **Network Services:** Load balancers, firewalls, VPNs, SSH endpoints
- **Message Queues:** Kafka topics, RabbitMQ exchanges (if exposed)
- **Cloud Services:** S3 buckets, Lambda functions, API Gateway

**Attack Surface Expansion Analysis:**

For each entry point:
- **Reachability Analysis:** Which internal components can be reached?
- **Data Flow Mapping:** What data can flow through this entry point?
- **Privilege Propagation:** How do privileges change across trust boundaries?
- **Lateral Movement Paths:** What other systems become accessible?

**Trust Boundary Identification:**

Automatically detects boundaries where trust changes:
- Internet → DMZ → Internal network
- Unauthenticated → Authenticated
- Standard user → Admin
- Public cloud → Private VPC
- Third-party service → Internal service

**Attack Surface Metrics:**

Calculated per system:
- Total entry point count
- Trust boundary crossing count
- Exposed sensitive data flow count
- Unauthenticated endpoint count
- Internet-facing component count
- Attack surface score (0-100, higher = more exposed)

**Reduction Recommendations:**

Suggests attack surface reduction strategies:
- Remove unnecessary endpoints
- Add authentication requirements
- Implement IP whitelisting
- Move services behind VPN
- Apply least-privilege principles
- Segment networks

**Visualization:**

Generates attack surface maps showing:
- External boundary with entry points
- Data flow paths from entry points to critical assets
- Trust boundaries crossed
- High-risk paths highlighted


### 9. Data Flow Analyzer

**Responsibility:** Track how sensitive data moves through the system, identifying data exposure risks and compliance violations.

**Architecture:**

**Taint Tracking System** following data from sources to sinks across components.

**Data Classification:**

Four sensitivity levels:
- **Restricted:** PII, PHI, payment card data, credentials, encryption keys
- **Confidential:** Internal business data, financial records, trade secrets
- **Internal:** Employee data, operational metrics, non-public information
- **Public:** Marketing content, public documentation, anonymized data

**Data Flow Graph:**

Constructs directed graph:
- **Nodes:** Components (services, databases, caches, queues)
- **Edges:** Data flows with properties:
  - Data types transmitted
  - Sensitivity level
  - Protocol (HTTP, gRPC, JDBC, etc.)
  - Encryption status (TLS version, cipher suite)
  - Trust boundary crossings

**Analysis Patterns:**

**1. Sensitive Data Exposure Detection:**
- Identify flows where Restricted/Confidential data crosses trust boundaries without encryption
- Flag data transmitted over insecure protocols (HTTP, FTP, Telnet)
- Detect sensitive data in logs, error messages, URLs

**2. Data Residency Compliance:**
- Track geographic location of data storage and processing
- Identify cross-border data flows requiring legal basis (GDPR, CCPA)
- Flag data stored outside required regions

**3. Access Control Verification:**
- Verify authentication required for sensitive data access
- Check authorization granularity (role-based, attribute-based)
- Identify overly permissive access patterns

**4. Encryption Coverage:**
- Ensure encryption at rest for Restricted/Confidential data
- Verify TLS 1.3 for data in transit
- Check key management practices

**5. Data Minimization:**
- Identify unnecessary data collection
- Flag long retention periods violating compliance
- Suggest data anonymization/pseudonymization

**Compliance Mapping:**

- **GDPR:** Article 32 (encryption), Article 44-50 (data transfers)
- **HIPAA:** §164.312(e)(1) (transmission security), §164.312(a)(2)(iv) (encryption)
- **PCI-DSS:** Requirement 3 (protect stored cardholder data), Requirement 4 (encrypt transmission)

**Data Flow Diagram Generation:**

Produces annotated DFDs showing:
- All components with data handling
- Data flow arrows with sensitivity labels
- Trust boundaries marked
- Encryption status indicators
- Compliance gaps highlighted


### 10. Ticket Creator (Issue Tracking Integration)

**Responsibility:** Automatically create security tickets in Jira, GitHub Issues, or Azure DevOps for identified threats.

**Architecture:**

**Adapter Pattern** with pluggable connectors for each issue tracking system.

**Supported Platforms:**

**Jira:**
- REST API v3
- Issue types: Security Bug, Security Task, Security Epic
- Custom fields: Risk Score, Threat Category, Affected Components, Compliance Frameworks
- Workflow integration: New → In Review → In Progress → Resolved → Closed

**GitHub Issues:**
- GraphQL API v4
- Labels: security, critical, high, medium, low, [threat-category]
- Milestones: Security Review Q2 2026
- Projects: Security Backlog board

**Azure DevOps:**
- REST API 7.0
- Work item types: Bug, Task, Epic
- Tags: security, [framework], [risk-level]
- Area paths: Security team assignments

**Ticket Generation Logic:**

**1. Deduplication:**
- Hash threat signature (threat type + affected component + system version)
- Query existing tickets for matching signature
- Skip creation if unresolved ticket exists
- Link to existing ticket in threat model

**2. Prioritization:**
- Map risk score to ticket priority:
  - Critical (80-100) → P0/Blocker
  - High (60-79) → P1/Critical
  - Medium (40-59) → P2/Major
  - Low (20-39) → P3/Minor
  - Informational (0-19) → P4/Trivial

**3. Assignment:**
- Determine owner from component ownership mapping
- Fallback to security team if owner unknown
- Support round-robin assignment for shared components

**4. Template Population:**

Ticket fields:
- **Title:** `[THREAT] {Threat Category}: {Threat Title} in {Component}`
- **Description:** Markdown with sections:
  - Threat Summary
  - Affected Components
  - Attack Scenario
  - Risk Assessment (likelihood, impact, risk score)
  - Recommended Mitigations (top 3)
  - Compliance Impact
  - References (CVE, CWE, MITRE ATT&CK)
- **Labels/Tags:** Framework, risk level, threat category, compliance frameworks
- **Links:** Related threats, blocked by dependencies

**5. Synchronization:**

Bidirectional sync:
- Platform → TMP: Ticket status updates, comments, resolution
- TMP → Platform: Risk score changes, new mitigations, threat reassessment

Webhook listeners for real-time updates:
- Ticket closed → Mark threat as mitigated in threat model
- Ticket reopened → Reactivate threat
- Comment added → Sync to threat discussion thread


---

## MCP Server Integration

The platform integrates **Model Context Protocol (MCP) servers** to extend functionality through standardized tool interfaces.

### Integrated MCP Servers

**1. Threat Intelligence MCP Server**

**Purpose:** Query external threat intelligence feeds (NVD, MITRE ATT&CK, CVE databases)

**Tools:**
- `query_cve`: Retrieve CVE details by identifier
- `search_vulnerabilities`: Search vulnerabilities by technology, vendor, version
- `get_attack_techniques`: Retrieve MITRE ATT&CK techniques for threat actor
- `check_exploit_availability`: Check if public exploits exist for CVE
- `get_threat_trends`: Retrieve trending threats from threat intelligence feeds

**Use Cases:**
- Enrich identified threats with CVE data
- Update likelihood scores based on exploit availability
- Map threats to ATT&CK techniques

**2. Code Analysis MCP Server**

**Purpose:** Static analysis of application source code for security vulnerabilities

**Tools:**
- `scan_repository`: Scan Git repository for vulnerabilities
- `analyze_dependencies`: Check for vulnerable dependencies (npm, pip, Maven)
- `detect_secrets`: Search for hardcoded credentials, API keys
- `check_security_patterns`: Verify security best practices (input validation, crypto usage)

**Use Cases:**
- Verify security controls claimed in architecture
- Identify code-level vulnerabilities complementing design threats
- Generate evidence for compliance audits

**3. Infrastructure Verification MCP Server**

**Purpose:** Verify infrastructure-as-code configurations against security policies

**Tools:**
- `scan_terraform`: Analyze Terraform configurations for misconfigurations
- `scan_kubernetes`: Check Kubernetes manifests against security policies
- `verify_cloud_config`: Validate AWS/Azure/GCP configurations
- `check_network_policies`: Verify network segmentation rules

**Use Cases:**
- Validate claimed security controls actually deployed
- Identify configuration drift from threat model
- Continuous verification in CI/CD pipelines

**4. Compliance Automation MCP Server**

**Purpose:** Automate compliance evidence collection and reporting

**Tools:**
- `generate_compliance_report`: Create framework-specific compliance reports
- `collect_evidence`: Gather evidence artifacts (configs, logs, policies)
- `map_controls`: Map security controls to compliance requirements
- `assess_compliance_posture`: Calculate compliance coverage scores

**Use Cases:**
- Automated audit preparation
- Continuous compliance monitoring
- Gap analysis reporting


**5. Policy Enforcement MCP Server**

**Purpose:** Integrate with policy-as-code engines (Open Policy Agent, Cloud Custodian)

**Tools:**
- `evaluate_policy`: Check threat model against organizational policies
- `enforce_gates`: Block deployments violating security policies
- `suggest_policy_updates`: Recommend policy changes based on threats
- `audit_policy_compliance`: Verify systems comply with policies

**Use Cases:**
- CI/CD pipeline gates based on threat analysis
- Enforce minimum security baselines
- Automated policy violation detection

---

## API Design

### REST API

**Base URL:** `https://api.threatmodeling.platform/v1`

**Authentication:** Bearer token (JWT) via OAuth 2.0

**Endpoints:**

#### Threat Model Management

**Create Threat Model:**
```
POST /threat-models
Content-Type: application/json

{
  "name": "Payment Service v2.0",
  "description": "E-commerce payment processing service",
  "architecture": {
    "format": "mermaid",
    "content": "..."
  },
  "frameworks": ["stride", "pasta"],
  "scope": {
    "components": [...],
    "dataSensitivity": "restricted"
  }
}

Response: 202 Accepted
{
  "threatModelId": "tm_abc123",
  "status": "analyzing",
  "estimatedCompletionTime": "2026-06-24T14:30:00Z"
}
```

**Get Threat Model:**
```
GET /threat-models/{threatModelId}

Response: 200 OK
{
  "id": "tm_abc123",
  "status": "completed",
  "summary": {
    "totalThreats": 24,
    "criticalThreats": 3,
    "highThreats": 8,
    "mediumThreats": 10,
    "lowThreats": 3,
    "averageRiskScore": 54.2
  },
  "threats": [...],
  "createdAt": "2026-06-24T14:00:00Z",
  "completedAt": "2026-06-24T14:04:32Z"
}
```

**List Threat Models:**
```
GET /threat-models?status=completed&sort=riskScore&limit=50

Response: 200 OK
{
  "threatModels": [...],
  "pagination": {
    "total": 127,
    "page": 1,
    "pageSize": 50
  }
}
```


#### Threat Management

**Get Threat Details:**
```
GET /threats/{threatId}

Response: 200 OK
{
  "id": "threat_xyz789",
  "title": "SQL Injection in User Search",
  "category": "injection",
  "description": "...",
  "affectedComponents": ["user-service", "database"],
  "riskScore": 85,
  "likelihoodScore": 90,
  "impactScore": 94,
  "cvss": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N",
  "cwe": ["CWE-89"],
  "mitigations": [...],
  "attackVectors": [...],
  "complianceImpact": [...]
}
```

**Update Threat Status:**
```
PATCH /threats/{threatId}
{
  "status": "mitigated",
  "resolution": "Implemented parameterized queries",
  "resolvedBy": "user_123",
  "resolvedAt": "2026-06-25T10:00:00Z"
}

Response: 200 OK
```

#### Risk Analysis

**Calculate Risk Score:**
```
POST /risk/calculate
{
  "threatId": "threat_xyz789",
  "customFactors": {
    "assetCriticality": 95,
    "existingControls": ["input-validation", "waf"]
  }
}

Response: 200 OK
{
  "riskScore": 72,
  "likelihoodScore": 76,
  "impactScore": 95,
  "breakdown": {...}
}
```

#### Mitigation Recommendations

**Generate Mitigations:**
```
POST /threats/{threatId}/mitigations/generate

Response: 200 OK
{
  "mitigations": [
    {
      "id": "mit_001",
      "title": "Implement Parameterized Queries",
      "description": "...",
      "effectiveness": 95,
      "implementationEffort": "medium",
      "estimatedRiskReduction": 78,
      "steps": [...],
      "references": [...]
    },
    ...
  ]
}
```

#### Compliance

**Get Compliance Status:**
```
GET /threat-models/{threatModelId}/compliance?framework=gdpr

Response: 200 OK
{
  "framework": "gdpr",
  "overallCoverage": 87.5,
  "requirements": [
    {
      "article": "Article 32(1)(a)",
      "description": "Pseudonymisation and encryption of personal data",
      "status": "satisfied",
      "controls": ["encryption-at-rest", "tls-1.3"],
      "gaps": []
    },
    ...
  ]
}
```


#### Reports & Export

**Generate Report:**
```
POST /threat-models/{threatModelId}/reports
{
  "format": "pdf",
  "sections": ["executive-summary", "threats", "mitigations", "compliance"],
  "includeGraphs": true
}

Response: 202 Accepted
{
  "reportId": "rpt_456",
  "status": "generating"
}
```

**Download Report:**
```
GET /reports/{reportId}/download

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="threat-model-payment-service-v2.pdf"
```

#### Integration Webhooks

**Register Webhook:**
```
POST /webhooks
{
  "url": "https://your-app.com/webhooks/threats",
  "events": ["threat.identified", "threat.critical", "analysis.completed"],
  "secret": "webhook_secret_key"
}

Response: 201 Created
{
  "webhookId": "wh_789",
  "status": "active"
}
```

### GraphQL API

**Endpoint:** `https://api.threatmodeling.platform/graphql`

**Schema Highlights:**

```graphql
type Query {
  threatModel(id: ID!): ThreatModel
  threatModels(filters: ThreatModelFilters): [ThreatModel!]!
  threat(id: ID!): Threat
  threats(filters: ThreatFilters): [Threat!]!
  attackPaths(from: ComponentInput!, to: ComponentInput!): [AttackPath!]!
  complianceStatus(threatModelId: ID!, framework: ComplianceFramework!): ComplianceStatus!
}

type Mutation {
  createThreatModel(input: ThreatModelInput!): ThreatModel!
  updateThreat(id: ID!, input: ThreatUpdate!): Threat!
  generateMitigations(threatId: ID!): [Mitigation!]!
  createTickets(threatModelId: ID!, platform: TicketPlatform!): [Ticket!]!
}

type ThreatModel {
  id: ID!
  name: String!
  status: ThreatModelStatus!
  threats: [Threat!]!
  riskMetrics: RiskMetrics!
  compliance: [ComplianceStatus!]!
  graph: ThreatGraph!
}

type Threat {
  id: ID!
  title: String!
  category: ThreatCategory!
  riskScore: Float!
  affectedComponents: [Component!]!
  mitigations: [Mitigation!]!
  attackVectors: [AttackVector!]!
}
```

---

## Security Architecture

### Authentication & Authorization

**Identity Provider:** Keycloak 24

**Authentication Mechanisms:**

1. **OAuth 2.0 / OpenID Connect:**
   - Authorization Code Flow for web applications
   - Client Credentials Flow for service-to-service
   - Device Authorization Flow for CLI tools
   - Refresh token rotation for enhanced security

2. **SAML 2.0:**
   - Enterprise SSO integration
   - Support for Okta, Azure AD, Google Workspace

3. **API Keys:**
   - Long-lived tokens for CI/CD pipelines
   - Scoped permissions per key
   - Rate limiting per key

**Authorization Model:**

**Role-Based Access Control (RBAC):**

- **Security Architect:** Full access, create/edit/delete threat models, configure frameworks
- **Security Analyst:** Read threat models, add comments, update threat status
- **Developer:** Read-only access to assigned threat models
- **Auditor:** Read-only access to all threat models, compliance reports
- **Service Account:** API access for automation, scoped to specific threat models

**Attribute-Based Access Control (ABAC):**

Fine-grained permissions based on:
- Threat model ownership (creator, team assignment)
- Component ownership (service owner access to threats affecting their services)
- Data sensitivity (access to threat models with PII requires data privacy clearance)
- Compliance scope (auditors access only threat models in their compliance scope)

**Policy Enforcement:**

Open Policy Agent (OPA) policies enforce:
- Minimum role requirements for actions
- Data access restrictions based on sensitivity
- Approval workflows for high-risk operations
- Compliance-mandated segregation of duties

### Data Encryption

**At Rest:**

- **Database Encryption:** AES-256-GCM
  - PostgreSQL: Transparent Data Encryption (TDE)
  - Neo4j: Full database encryption
  - Redis: RDB and AOF file encryption
- **Object Storage:** S3 server-side encryption (SSE-KMS)
- **Secrets:** HashiCorp Vault with encryption-as-a-service
- **Backups:** Encrypted with unique per-backup keys

**In Transit:**

- **External Communication:** TLS 1.3 only, strong cipher suites
  - Minimum: TLS_AES_128_GCM_SHA256
  - Preferred: TLS_AES_256_GCM_SHA384
- **Internal Communication:** mTLS via Istio service mesh
  - Automatic certificate rotation (24-hour validity)
  - Certificate management via cert-manager
- **Database Connections:** TLS-encrypted connections enforced


### Secrets Management

**HashiCorp Vault Integration:**

- **Dynamic Secrets:** Short-lived database credentials generated on-demand
- **Encryption as a Service:** Application-level encryption keys
- **PKI:** Internal certificate authority for mTLS
- **Secret Rotation:** Automatic rotation of API keys, database passwords
- **Audit Logging:** All secret access logged to immutable audit log

**Secret Types:**

- Database credentials (PostgreSQL, Neo4j, Redis)
- External API keys (OpenAI, Anthropic, threat intelligence feeds)
- Encryption keys (data encryption, JWT signing)
- Service account tokens (Kubernetes, cloud providers)
- Integration credentials (Jira, GitHub, Azure DevOps)

### Network Security

**Segmentation:**

- **DMZ:** Load balancers, API gateways, WAF
- **Application Tier:** Microservices, no direct internet access
- **Data Tier:** Databases, message queues, isolated VPC
- **Management Tier:** Monitoring, logging, separate network

**Firewall Rules:**

- Default deny all traffic
- Explicit allow rules per service
- Egress filtering (whitelist external destinations)
- No direct database access from application tier (connection pooling service)

**DDoS Protection:**

- CloudFlare or AWS Shield
- Rate limiting at multiple layers (API gateway, application, database)
- Adaptive rate limiting based on user behavior

### Audit Logging

**Logged Events:**

- Authentication (login, logout, failed attempts)
- Authorization (permission checks, access denials)
- Threat model operations (create, update, delete, export)
- Risk score changes (recalculation triggers, manual overrides)
- Mitigation updates (status changes, implementations)
- Configuration changes (framework settings, integration configs)
- API access (endpoint, user, timestamp, response time)
- Admin operations (user management, permission changes)

**Log Format:**

Structured JSON logs with:
- Timestamp (ISO 8601, UTC)
- User identity (user ID, session ID)
- Action (operation performed)
- Resource (threat model ID, threat ID, etc.)
- Result (success, failure, error message)
- IP address and user agent
- Trace ID (distributed tracing correlation)

**Log Storage:**

- Immutable append-only storage
- 2-year retention for compliance
- Encrypted at rest and in transit
- Backed up to geographically redundant storage
- Real-time streaming to SIEM (Elasticsearch)

**Compliance:**

Satisfies audit requirements for:
- SOC 2 CC7.2 (system monitoring)
- GDPR Article 30 (records of processing activities)
- HIPAA §164.312(b) (audit controls)

---

## Deployment Architecture

### Kubernetes Architecture

**Cluster Configuration:**

- **Multi-Zone Deployment:** 3 availability zones for high availability
- **Node Pools:**
  - **API Nodes:** 4-16 vCPU, optimized for latency
  - **Worker Nodes:** 8-32 vCPU, optimized for throughput (threat analysis)
  - **Data Nodes:** Memory-optimized for databases and caching
  - **GPU Nodes:** For ML model inference (optional)

**Namespaces:**

- `production`: Production services
- `staging`: Pre-production testing
- `monitoring`: Observability stack
- `security`: Security tools (Vault, Falco, Trivy)
- `data`: Databases and message queues

**Resource Management:**

- **Resource Requests:** Guaranteed minimum (CPU, memory)
- **Resource Limits:** Maximum allowed to prevent noisy neighbors
- **Horizontal Pod Autoscaling (HPA):** Scale based on CPU, memory, custom metrics
- **Vertical Pod Autoscaling (VPA):** Right-size resource requests
- **Cluster Autoscaling:** Add/remove nodes based on demand

### Service Deployment Patterns

**Stateless Services:**

- API Gateway, Threat Analyzer, Risk Calculator, Mitigation Generator
- Deployment strategy: Rolling update (zero downtime)
- Replica count: Minimum 3 for high availability
- Pod Disruption Budgets: Ensure minimum replicas during maintenance

**Stateful Services:**

- PostgreSQL: StatefulSet with persistent volumes
- Neo4j: Causal cluster (3 core members, N read replicas)
- Redis: Sentinel configuration (1 primary, 2 replicas)
- Kafka: 3-broker cluster with replication factor 3

**Background Workers:**

- Threat analysis workers: Kubernetes Jobs for long-running analyses
- Report generators: CronJobs for scheduled report generation
- Threat intelligence sync: CronJobs for periodic feed updates

### Service Mesh (Istio)

**Traffic Management:**

- **Load Balancing:** Round-robin, least connection, consistent hashing
- **Circuit Breaking:** Prevent cascading failures
- **Retries:** Automatic retry with exponential backoff
- **Timeouts:** Per-service timeout configuration
- **Fault Injection:** Testing resilience in staging

**Security:**

- **mTLS:** Automatic mutual TLS between services
- **Authorization Policies:** Fine-grained access control
- **Rate Limiting:** Protect services from overload
- **JWT Validation:** Verify authentication tokens

**Observability:**

- **Distributed Tracing:** Automatic trace propagation
- **Metrics:** Golden signals (latency, traffic, errors, saturation)
- **Access Logs:** Service-to-service communication logs


### Database Deployment

**PostgreSQL (Primary Data Store):**

- **Configuration:** Primary-replica setup with streaming replication
- **High Availability:** Patroni for automatic failover (<30 seconds)
- **Connection Pooling:** PgBouncer (1000+ connections → 50 database connections)
- **Backup Strategy:** 
  - Continuous WAL archiving to S3
  - Daily full backups with 30-day retention
  - Point-in-time recovery capability
- **Performance:** 
  - Read replicas for analytics queries
  - Partitioning for large tables (threat_models, audit_logs)

**Neo4j (Threat Graph):**

- **Configuration:** Causal cluster (3 core, 5 read replicas)
- **Routing:** Bolt driver with automatic read/write routing
- **Backup Strategy:**
  - Daily full backups
  - Incremental backups every 6 hours
  - Geographic replication
- **Performance:**
  - Bloom indexes for fast lookups
  - Native graph algorithms for path finding
  - Query caching for frequent patterns

**Qdrant (Vector Store):**

- **Configuration:** Distributed mode with sharding
- **Replication:** 3x replication for fault tolerance
- **Collections:** 
  - `threat_patterns` (50,000+ vectors, 768 dimensions)
  - `mitigation_templates` (10,000+ vectors)
  - `architecture_embeddings` (for similarity search)
- **Performance:**
  - HNSW indexes for sub-100ms similarity search
  - Quantization for memory efficiency
  - Pre-filtering for metadata constraints

**Redis (Cache & Sessions):**

- **Configuration:** Sentinel (1 primary, 2 replicas)
- **Persistence:** RDB snapshots + AOF for durability
- **Eviction Policy:** LRU (Least Recently Used)
- **Use Cases:**
  - Session storage (JWT tokens, user sessions)
  - Query result caching (threat model summaries)
  - Rate limiting counters
  - Pub/Sub for real-time updates

### Kafka Deployment

**Cluster Configuration:**

- 3 brokers across availability zones
- Replication factor: 3 for critical topics, 2 for non-critical
- Min in-sync replicas: 2 for critical topics

**Topics:**

- `threat.analysis.requests`: Async threat analysis jobs
- `threat.analysis.results`: Completed analyses
- `threat.intelligence.updates`: External feed updates
- `audit.events`: Audit log streaming
- `notifications`: User notifications (email, Slack, Teams)

**Consumer Groups:**

- Threat analyzers: Parallel processing with partition assignment
- Report generators: Sequential processing for ordering
- Notification handlers: At-least-once delivery with idempotency

### Multi-Region Deployment

**Primary Region:** US-East (Production workloads)

**Secondary Region:** EU-West (Compliance, disaster recovery)

**Replication Strategy:**

- **Active-Active:** Web UI, API Gateway (geo-routed by Cloudflare)
- **Active-Passive:** Databases (async replication, manual failover)
- **Global:** CDN for static assets, object storage replication

**Data Residency:**

- EU customer data stored exclusively in EU-West
- Cross-region access controls enforced
- GDPR compliance through data localization

---

## Performance Optimization

### Caching Strategy

**Multi-Level Caching:**

**L1 - Application Cache (In-Memory):**
- Threat patterns (frequently accessed)
- Framework definitions (STRIDE, PASTA, VAST rules)
- User permissions and roles
- Configuration settings
- TTL: 5-15 minutes
- Invalidation: Event-driven via Kafka

**L2 - Distributed Cache (Redis):**
- Threat model summaries
- Risk calculation results
- Compliance mappings
- Query results (graph traversals)
- TTL: 1-24 hours based on data volatility
- Invalidation: Explicit on data updates

**L3 - CDN Cache:**
- Static assets (JS, CSS, images)
- Generated reports (PDFs, HTML)
- Architecture diagrams
- TTL: 7-30 days
- Invalidation: Version-based cache busting

**Cache Warming:**

On system startup or deployment:
- Pre-load threat patterns from vector store
- Cache framework definitions
- Warm frequently accessed threat models (last 7 days)

**Cache Coherence:**

- Write-through caching for critical data
- Event-driven invalidation via Kafka topics
- Distributed cache invalidation using Redis pub/sub
- Cache versioning to prevent stale reads

### Query Optimization

**Database Optimization:**

**PostgreSQL:**
- Indexes on foreign keys, frequently queried columns
- Covering indexes for common queries
- Partial indexes for filtered queries (e.g., active threats)
- Materialized views for complex aggregations (risk metrics by category)
- Query planning analysis and optimization

**Neo4j:**
- Bloom indexes for exact match lookups
- Full-text indexes for threat description search
- Query profiling with `PROFILE` and `EXPLAIN`
- Periodic graph statistics updates
- Cypher query optimization (path length limits, relationship filtering)

**Query Patterns:**

- Avoid N+1 queries using DataLoader pattern
- Batch database operations
- Connection pooling (PgBouncer, Neo4j connection pool)
- Read replica routing for analytics queries
- Prepared statements for parameterized queries


### Asynchronous Processing

**Event-Driven Architecture:**

Long-running operations handled asynchronously:

**Threat Analysis Workflow:**

1. User submits threat model → API Gateway returns 202 Accepted with job ID
2. API Gateway publishes to Kafka `threat.analysis.requests` topic
3. Worker pool consumes from topic (10-50 workers based on load)
4. Worker performs AI analysis, graph updates, risk calculation
5. Worker publishes results to `threat.analysis.results` topic
6. Notification service sends completion notification
7. User polls `/threat-models/{id}` or receives WebSocket update

**Benefits:**

- Non-blocking API responses (<100ms)
- Horizontal scaling of workers
- Retry logic with dead-letter queues
- Backpressure handling through Kafka partitioning
- Priority queuing (critical threats processed first)

**Background Jobs:**

- Report generation (PDF, HTML, Markdown)
- Threat intelligence feed synchronization
- Compliance report generation
- Security control verification
- Threat model versioning and archival

### API Performance

**Rate Limiting:**

- **User Tier-Based:**
  - Free: 100 requests/minute
  - Pro: 1,000 requests/minute
  - Enterprise: 10,000 requests/minute
- **Endpoint-Specific:**
  - Analysis endpoints: Lower limits due to AI cost
  - Query endpoints: Higher limits for read operations
- **Implementation:** Redis-based token bucket algorithm

**Response Optimization:**

- **Pagination:** Limit result sets (default 50, max 200)
- **Field Selection:** GraphQL-style field projection in REST API
- **Compression:** Gzip/Brotli for responses >1KB
- **Partial Responses:** Support `fields` parameter for selective data
- **HTTP/2:** Multiplexing, header compression, server push

**Connection Management:**

- Keep-alive connections (reuse TCP connections)
- Connection pooling at application level
- Load balancer connection draining (graceful shutdown)

### AI Model Optimization

**Prompt Caching:**

- Cache LLM responses for identical architecture + framework combinations
- Cache key: Hash of (architecture, framework, threat category)
- Hit rate: ~40% for similar architectures
- Reduces AI API costs by 40%

**Batch Processing:**

- Batch multiple threat analyses in single LLM call
- Process multiple components in parallel
- Reduces API round-trips

**Model Selection:**

- **GPT-4o:** Complex architectures, high accuracy required
- **GPT-4o-mini:** Simple architectures, cost optimization
- **Claude Opus 4:** Cross-validation, reasoning-heavy tasks
- Dynamic model selection based on architecture complexity

**Token Optimization:**

- Prompt compression (remove unnecessary context)
- Streaming responses for real-time UI updates
- Context window management (chunking large architectures)
- Few-shot learning with curated examples

---

## Error Handling

### Error Classification

**Client Errors (4xx):**

- **400 Bad Request:** Invalid architecture format, missing required fields
- **401 Unauthorized:** Missing or invalid authentication token
- **403 Forbidden:** Insufficient permissions for operation
- **404 Not Found:** Threat model, threat, or resource not found
- **409 Conflict:** Version conflict, concurrent modification detected
- **422 Unprocessable Entity:** Valid format but semantic errors (e.g., circular dependencies)
- **429 Too Many Requests:** Rate limit exceeded

**Server Errors (5xx):**

- **500 Internal Server Error:** Unexpected application error
- **502 Bad Gateway:** Upstream service failure (database, AI API)
- **503 Service Unavailable:** Service temporarily unavailable (maintenance, overload)
- **504 Gateway Timeout:** Upstream service timeout

### Error Response Format

Consistent JSON error format:

```json
{
  "error": {
    "code": "THREAT_MODEL_NOT_FOUND",
    "message": "Threat model with ID 'tm_abc123' not found",
    "details": {
      "threatModelId": "tm_abc123",
      "requestId": "req_xyz789"
    },
    "timestamp": "2026-06-24T14:30:00Z",
    "path": "/threat-models/tm_abc123"
  }
}
```

### Retry Logic

**Exponential Backoff:**

- Initial delay: 1 second
- Max delay: 32 seconds
- Max retries: 5
- Jitter: Random 0-500ms to prevent thundering herd

**Retryable Operations:**

- Transient database connection failures
- AI API rate limits (429) or temporary errors (503)
- Message queue publish failures
- External API timeouts

**Non-Retryable:**

- Authentication failures (401)
- Authorization failures (403)
- Invalid input (400, 422)
- Resource not found (404)

### Circuit Breaker Pattern

**Implementation:**

- Open circuit after 5 consecutive failures
- Half-open after 30 seconds (test with single request)
- Close circuit after 3 successful requests
- Fail fast when circuit open (return cached data or error)

**Applied To:**

- External AI APIs (GPT, Claude)
- Threat intelligence feeds
- Issue tracking integrations (Jira, GitHub)
- Email/notification services

### Graceful Degradation

**Fallback Strategies:**

**AI API Failures:**
- Fall back to cached threat patterns
- Use rule-based threat identification
- Return partial results with warning

**Database Failures:**
- Serve from read replicas
- Return cached query results
- Queue write operations for later processing

**External Service Failures:**
- Skip optional enrichment (CVE lookups, ATT&CK mapping)
- Proceed with core analysis
- Log failures for manual review

---

## Testing Strategy

### Testing Philosophy

The Threat Modeling Platform employs a **comprehensive testing pyramid** with emphasis on automated testing at all levels.

### Unit Testing

**Coverage Target:** 80%+ code coverage for core business logic

**Focus Areas:**

- Risk calculation algorithms (likelihood, impact, risk score)
- Architecture parsing logic (format detection, entity extraction)
- Framework engines (STRIDE, PASTA, VAST rule application)
- Data flow analysis (sensitivity classification, trust boundary detection)
- Compliance mapping rules
- Utility functions and helper libraries

**Testing Approach:**

- Table-driven tests for algorithms with multiple input scenarios
- Property-based testing for parsers (round-trip properties)
- Mock external dependencies (AI APIs, databases)
- Parameterized tests for different frameworks and configurations

**Tools:**

- **Go:** `testing` package, `testify` for assertions, `gomock` for mocking
- **Python:** `pytest`, `unittest.mock`, `hypothesis` for property-based testing

### Integration Testing

**Coverage Target:** All API endpoints, database interactions, external integrations

**Focus Areas:**

- REST API endpoints (request/response validation)
- GraphQL queries and mutations
- Database operations (PostgreSQL, Neo4j, Qdrant, Redis)
- Message queue producers and consumers (Kafka)
- External API integrations (mocked AI APIs, threat intelligence feeds)
- Issue tracking integration (mocked Jira, GitHub, Azure DevOps)

**Testing Approach:**

- Test containers (Testcontainers) for real database instances
- Mock external APIs with realistic response data
- End-to-end workflow testing (create threat model → analyze → generate mitigations → create tickets)
- Contract testing for API stability

**Tools:**

- **Testcontainers:** Ephemeral database containers
- **WireMock:** HTTP mock server for external APIs
- **Postman/Newman:** API testing and automation

### End-to-End Testing

**Coverage Target:** Critical user journeys and workflows

**Test Scenarios:**

1. **Complete Threat Modeling Flow:**
   - Upload architecture diagram
   - Select frameworks (STRIDE, PASTA)
   - AI analysis completes
   - Review identified threats
   - Generate mitigations
   - Create Jira tickets
   - Export PDF report

2. **Compliance Workflow:**
   - Create threat model
   - Map to GDPR requirements
   - Identify compliance gaps
   - Implement recommended controls
   - Verify compliance status improved

3. **CI/CD Integration:**
   - Architecture change committed
   - Webhook triggers analysis
   - New threats identified
   - Pipeline gate blocks deployment (critical threats)
   - Threats mitigated
   - Pipeline succeeds

**Tools:**

- **Playwright:** Browser automation for UI testing
- **Cypress:** Alternative end-to-end testing framework
- **k6:** Load testing for performance validation


### Performance Testing

**Load Testing:**

- Simulate 100 concurrent users
- Sustained load for 30 minutes
- Measure response times (p50, p95, p99)
- Identify bottlenecks (CPU, memory, database connections)

**Stress Testing:**

- Gradually increase load until system breaks
- Identify breaking point
- Test auto-scaling behavior
- Verify graceful degradation

**Spike Testing:**

- Sudden traffic surge (10x normal load)
- Test circuit breakers
- Verify rate limiting effectiveness
- Check recovery time

**Soak Testing:**

- Run at 80% capacity for 24-48 hours
- Detect memory leaks
- Monitor resource exhaustion
- Verify log rotation and cleanup

**Tools:**

- **k6:** Modern load testing tool with JavaScript DSL
- **Gatling:** High-performance load testing
- **JMeter:** Comprehensive performance testing

### Security Testing

**Static Application Security Testing (SAST):**

- **SonarQube:** Code quality and security vulnerability detection
- **Semgrep:** Lightweight static analysis
- **gosec:** Go security checker
- **Bandit:** Python security linter

**Dynamic Application Security Testing (DAST):**

- **OWASP ZAP:** Automated security scanning
- **Burp Suite:** Manual penetration testing
- **Nuclei:** Vulnerability scanner

**Container Security:**

- **Trivy:** Container image vulnerability scanning
- **Snyk:** Dependency vulnerability scanning
- **Grype:** Container and filesystem vulnerability scanning

**Infrastructure Security:**

- **Checkov:** IaC security scanning (Terraform, Kubernetes)
- **tfsec:** Terraform security scanner
- **kube-bench:** Kubernetes CIS benchmark testing

**Penetration Testing:**

- Annual third-party penetration testing
- Bug bounty program for responsible disclosure
- Red team exercises simulating advanced persistent threats

### Chaos Engineering

**Failure Scenarios:**

- Random pod termination (kill services, test recovery)
- Network latency injection (test timeout handling)
- Database failover simulation (test high availability)
- Region failure (test multi-region failover)
- Resource exhaustion (CPU, memory limits)

**Tools:**

- **Chaos Mesh:** Kubernetes native chaos engineering
- **Litmus:** Cloud-native chaos engineering framework
- **Toxiproxy:** Network condition simulation

---

## Monitoring & Observability

### Metrics Collection

**System Metrics:**

- **Infrastructure:** CPU, memory, disk I/O, network throughput
- **Kubernetes:** Pod status, container restarts, resource utilization
- **Application:** Request rate, response time, error rate, active connections

**Business Metrics:**

- Threat models created (per day, week, month)
- Threats identified (by severity, category, framework)
- Risk score distribution
- Mitigation completion rate
- Compliance coverage percentage
- User engagement (active users, analyses performed)

**AI Metrics:**

- LLM API latency (GPT-4o, Claude)
- Token usage and cost
- AI analysis duration
- Threat identification accuracy (false positive rate)
- Model cache hit rate

**Database Metrics:**

- Query latency (p50, p95, p99)
- Connection pool utilization
- Cache hit ratio
- Replication lag
- Transaction throughput

**Collection & Storage:**

- **Prometheus:** Time-series metrics collection (15-second scrape interval)
- **Grafana:** Visualization and dashboards
- **Retention:** 15 days high-resolution, 1 year downsampled

### Distributed Tracing

**Trace Propagation:**

- OpenTelemetry instrumentation across all services
- Trace context propagated via HTTP headers (W3C Trace Context)
- Correlation IDs in logs linked to traces

**Traced Operations:**

- API request end-to-end (gateway → services → databases)
- Threat analysis workflow (parse → AI analysis → graph update → risk calc)
- Background jobs (report generation, intelligence sync)
- External API calls (AI APIs, threat feeds, integrations)

**Trace Storage:**

- **Logfire:** Distributed tracing backend
- **Retention:** 7 days full traces, 30 days sampled
- **Sampling:** 100% for errors, 10% for successful requests

**Trace Analysis:**

- Identify slow services and database queries
- Detect cascading failures
- Optimize critical paths
- Debug production issues

### Logging

**Log Levels:**

- **ERROR:** Application errors, exceptions, failed operations
- **WARN:** Degraded functionality, retry attempts, deprecated API usage
- **INFO:** Normal operations, successful completions, state changes
- **DEBUG:** Detailed diagnostic information (disabled in production by default)

**Log Structure:**

Structured JSON logs with:
- Timestamp (ISO 8601, UTC)
- Level (ERROR, WARN, INFO, DEBUG)
- Message (human-readable)
- Service name and version
- Trace ID and span ID
- Request ID
- User ID (if applicable)
- Context (additional structured data)

**Log Aggregation:**

- **Elasticsearch:** Centralized log storage
- **Kibana:** Log search and visualization
- **Logstash/Fluentd:** Log collection and forwarding
- **Retention:** 30 days hot storage, 1 year cold storage


### Alerting

**Alert Rules:**

**Critical Alerts (Page On-Call):**

- Service down (all replicas unhealthy)
- Database unavailable (primary and replicas)
- Error rate >5% sustained for 5 minutes
- Response time p95 >10 seconds for 5 minutes
- Disk usage >90%
- Certificate expiration within 7 days

**Warning Alerts (Notify Team Channel):**

- High error rate (>1% for 10 minutes)
- Slow response times (p95 >3 seconds for 10 minutes)
- High CPU/memory utilization (>80% for 15 minutes)
- Backup failure
- Replication lag >60 seconds
- Cache hit rate <70%

**Informational Alerts:**

- Deployment completed
- Threat model analysis spike (>2x normal volume)
- AI API cost spike
- New threat intelligence available

**Alert Routing:**

- **Slack:** Team channels for warnings and informational
- **PagerDuty:** On-call engineers for critical alerts
- **Email:** Escalation and daily summaries
- **Webhooks:** Custom integrations (SIEM, ticketing)

**Alert Management:**

- De-duplication (suppress duplicate alerts)
- Grouping (batch related alerts)
- Silencing (maintenance windows)
- Escalation policies (auto-escalate if not acknowledged)

### Dashboards

**System Health Dashboard:**

- Service status (green/yellow/red indicators)
- Request rate and response time trends
- Error rate by service
- Infrastructure resource utilization
- Database performance metrics

**Business Metrics Dashboard:**

- Threat models created (daily, weekly trends)
- Threats by severity (pie chart)
- Risk score distribution (histogram)
- Top threat categories (bar chart)
- Compliance coverage by framework (gauge)

**AI Operations Dashboard:**

- LLM API latency and cost
- Token usage trends
- Analysis duration distribution
- Cache hit rates
- Model selection breakdown

**Security Dashboard:**

- Failed authentication attempts
- Authorization denials
- Suspicious activity patterns
- API rate limit violations
- Certificate expiration calendar

---

## Disaster Recovery & Business Continuity

### Backup Strategy

**Database Backups:**

**PostgreSQL:**
- **Full Backups:** Daily at 02:00 UTC
- **Incremental Backups:** Continuous WAL archiving
- **Retention:** 30 daily, 12 weekly, 12 monthly
- **Storage:** S3 with cross-region replication
- **Encryption:** AES-256, separate encryption keys per backup
- **Testing:** Monthly restore test to verify integrity

**Neo4j:**
- **Full Backups:** Daily at 03:00 UTC
- **Retention:** 30 days full backups
- **Storage:** S3 with cross-region replication
- **Testing:** Quarterly restore to staging environment

**Configuration & Secrets:**
- **Kubernetes Configs:** Git repository (GitOps)
- **Vault Secrets:** Automated snapshots every 6 hours
- **Retention:** 90 days

### Recovery Time Objective (RTO) & Recovery Point Objective (RPO)

**Tier 1 Services (Critical):**
- **RTO:** 1 hour (maximum downtime)
- **RPO:** 5 minutes (maximum data loss)
- **Services:** API Gateway, Threat Analyzer, PostgreSQL, Neo4j

**Tier 2 Services (Important):**
- **RTO:** 4 hours
- **RPO:** 1 hour
- **Services:** Mitigation Generator, Compliance Mapper, Report Generator

**Tier 3 Services (Standard):**
- **RTO:** 24 hours
- **RPO:** 24 hours
- **Services:** Analytics, Historical reporting

### Disaster Scenarios

**Scenario 1: Single Service Failure**

- **Detection:** Health check failure, alerts triggered
- **Automatic Response:** Kubernetes restarts pod, traffic routed to healthy replicas
- **Recovery Time:** 30-60 seconds
- **Data Loss:** None (stateless services)

**Scenario 2: Database Primary Failure**

- **Detection:** Connection failures, replication lag spike
- **Automatic Response:** Patroni promotes replica to primary, update DNS
- **Recovery Time:** <30 seconds
- **Data Loss:** None (synchronous replication)

**Scenario 3: Availability Zone Failure**

- **Detection:** Multiple service failures in same AZ
- **Automatic Response:** Traffic routed to remaining AZs, pods rescheduled
- **Recovery Time:** 5-10 minutes
- **Data Loss:** None (multi-AZ data replication)

**Scenario 4: Region Failure**

- **Detection:** Complete region unavailable
- **Manual Response:** Promote secondary region, update global DNS
- **Recovery Time:** 2-4 hours
- **Data Loss:** Up to 15 minutes (async replication lag)

### Runbooks

Documented procedures for common failure scenarios:

1. **Database Failover Procedure**
2. **Complete System Restore from Backup**
3. **Region Failover Procedure**
4. **Data Corruption Recovery**
5. **Security Incident Response**
6. **AI API Outage Mitigation**
7. **Certificate Expiration Emergency Renewal**

---

## Data Models

### Core Entities

**Threat Model:**

```yaml
ThreatModel:
  id: UUID
  name: string
  description: text
  version: semver
  status: enum [draft, analyzing, completed, archived]
  createdBy: userId
  createdAt: timestamp
  updatedAt: timestamp
  completedAt: timestamp
  architecture:
    format: enum [markdown, plantuml, mermaid, json, image]
    content: text
    components: Component[]
    dataFlows: DataFlow[]
    trustBoundaries: TrustBoundary[]
  frameworks: string[] [stride, pasta, vast, attack-tree]
  metadata:
    systemName: string
    environment: enum [development, staging, production]
    technologyStack: string[]
    externalDependencies: string[]
  riskMetrics:
    totalThreats: integer
    criticalCount: integer
    highCount: integer
    mediumCount: integer
    lowCount: integer
    averageRiskScore: float
  complianceCoverage:
    gdpr: float
    soc2: float
    iso27001: float
    hipaa: float
```

**Threat:**

```yaml
Threat:
  id: UUID
  threatModelId: UUID
  title: string
  description: text
  category: enum [authentication, authorization, injection, data-exposure, ...]
  frameworks:
    stride: enum [spoofing, tampering, repudiation, ...]
    pasta: string
    vast: enum [application, operational]
  affectedComponents: UUID[]
  affectedAssets: UUID[]
  attackVectors: AttackVector[]
  threatActors: ThreatActor[]
  riskAssessment:
    likelihoodScore: float [0-100]
    impactScore: float [0-100]
    riskScore: float [0-100]
    riskLevel: enum [critical, high, medium, low, informational]
    cvss: string (CVSS v3.1 vector)
  classification:
    cwe: string[]
    cve: string[]
    mitreAttack: string[]
  status: enum [new, under-review, accepted, mitigated, risk-accepted, false-positive]
  mitigations: Mitigation[]
  complianceImpact: ComplianceMapping[]
  createdAt: timestamp
  updatedAt: timestamp
  resolvedAt: timestamp
  resolvedBy: userId
```

**Mitigation:**

```yaml
Mitigation:
  id: UUID
  threatId: UUID
  title: string
  description: text
  type: enum [preventive, detective, corrective, compensating]
  effectiveness: float [0-100]
  implementationEffort: enum [low, medium, high]
  priority: integer
  steps: string[]
  references: string[]
  estimatedRiskReduction: float
  status: enum [proposed, approved, in-progress, implemented, verified]
  implementedBy: userId
  implementedAt: timestamp
  verificationMethod: text
  complianceSatisfied: string[]
```


**Component:**

```yaml
Component:
  id: UUID
  name: string
  type: enum [service, database, api, queue, cache, external-service, ...]
  description: text
  technologyStack: string[]
  deployment:
    environment: string
    networkZone: string
    publiclyAccessible: boolean
  securityControls: SecurityControl[]
  owner: userId
  criticality: enum [critical, high, medium, low]
  dataHandled: string[]
  connections: Connection[]
```

**Data Flow:**

```yaml
DataFlow:
  id: UUID
  sourceComponent: UUID
  targetComponent: UUID
  dataTypes: string[]
  sensitivityLevel: enum [restricted, confidential, internal, public]
  protocol: string
  encryption:
    inTransit: boolean
    tlsVersion: string
    cipherSuite: string
  authentication: boolean
  authorization: boolean
  crossesTrustBoundary: boolean
  geographicFlow:
    sourceRegion: string
    targetRegion: string
```

**Attack Vector:**

```yaml
AttackVector:
  id: UUID
  name: string
  description: text
  attackComplexity: enum [low, medium, high]
  requiredPrivileges: enum [none, low, high]
  userInteraction: enum [none, required]
  exploitAvailability: enum [public, poc, theoretical]
  mitreAttackTechniques: string[]
  steps: string[]
```

**Compliance Mapping:**

```yaml
ComplianceMapping:
  id: UUID
  framework: enum [gdpr, soc2, iso27001, hipaa, pci-dss]
  requirement: string
  description: text
  satisfiedBy: UUID[] (Mitigation IDs)
  status: enum [satisfied, partial, not-satisfied]
  evidenceArtifacts: string[]
  gaps: string[]
```

---

## CI/CD Integration Patterns

### GitHub Actions Integration

**Workflow Trigger:**

Architecture changes in pull requests automatically trigger threat analysis:

```yaml
name: Threat Modeling Analysis
on:
  pull_request:
    paths:
      - 'architecture/**'
      - 'docs/architecture.md'
      - 'infrastructure/**'

jobs:
  threat-analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Run Threat Analysis
        env:
          TMP_API_KEY: ${{ secrets.THREAT_MODELING_API_KEY }}
        run: |
          tmp-cli analyze \
            --architecture-file architecture/system-design.mermaid \
            --frameworks stride,pasta \
            --output threat-report.json
      
      - name: Check for Critical Threats
        run: |
          critical_count=$(jq '.summary.criticalThreats' threat-report.json)
          if [ $critical_count -gt 0 ]; then
            echo "Critical threats detected. Blocking merge."
            exit 1
          fi
      
      - name: Post Comment to PR
        uses: actions/github-script@v6
        with:
          script: |
            const report = require('./threat-report.json');
            const comment = `
            ## 🔒 Threat Modeling Analysis
            
            **Risk Summary:**
            - Critical: ${report.summary.criticalThreats}
            - High: ${report.summary.highThreats}
            - Medium: ${report.summary.mediumThreats}
            
            [View Full Report](${report.reportUrl})
            `;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### GitLab CI Integration

```yaml
threat-modeling:
  stage: security
  image: threatmodeling/cli:latest
  script:
    - tmp-cli analyze --architecture-file architecture.yaml --frameworks stride,vast
    - tmp-cli check-policy --policy-file .threat-policy.yaml
  artifacts:
    reports:
      security: threat-report.json
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      changes:
        - architecture/**/*
        - infrastructure/**/*
```

### Jenkins Pipeline

```groovy
pipeline {
  agent any
  stages {
    stage('Threat Analysis') {
      when {
        changeset "architecture/**"
      }
      steps {
        sh 'tmp-cli analyze --config threat-modeling.yaml'
        script {
          def report = readJSON file: 'threat-report.json'
          if (report.summary.criticalThreats > 0) {
            error("Critical threats detected")
          }
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'threat-report.*', fingerprint: true
    }
  }
}
```

### Policy-as-Code Enforcement

**Example Policy (Open Policy Agent):**

```rego
package threatmodeling

deny[msg] {
  input.summary.criticalThreats > 0
  msg := "Critical threats must be mitigated before deployment"
}

deny[msg] {
  input.complianceCoverage.gdpr < 90
  msg := "GDPR compliance coverage must be at least 90%"
}

warn[msg] {
  input.summary.highThreats > 5
  msg := sprintf("High threat count (%d) exceeds recommended threshold", 
    [input.summary.highThreats])
}
```

---

## Scaling Strategy

### Horizontal Scaling

**Stateless Services:**

- API Gateway: Scale based on request rate (target: 70% CPU utilization)
- Threat Analyzer: Scale based on queue depth (Kafka lag)
- Risk Calculator: Scale based on CPU and memory
- Mitigation Generator: Scale based on AI API response time
- All services support unlimited replicas (no coordination required)

**HPA Configuration:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: threat-analyzer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: threat-analyzer
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: External
    external:
      metric:
        name: kafka_consumer_lag
      target:
        type: AverageValue
        averageValue: "100"
```

**Database Scaling:**

**PostgreSQL:**
- Primary for writes (vertical scaling: 8-64 vCPU)
- Read replicas for analytics (horizontal scaling: 1-10 replicas)
- Connection pooling (PgBouncer) to handle 1000+ connections

**Neo4j:**
- Causal cluster: 3 core members (consensus), N read replicas
- Write scaling: Shard graph by threat model ID (future enhancement)
- Read scaling: Add read replicas (linear scaling)

**Redis:**
- Cluster mode for horizontal scaling (16 shards)
- Each shard: 1 primary + 2 replicas
- Linear scaling to 1000+ nodes if needed

**Qdrant:**
- Distributed deployment with sharding
- Scale by adding nodes (automatic shard rebalancing)
- Replication factor: 3 for fault tolerance

### Vertical Scaling

**When to Use:**

- Initial deployment (cost-effective for low traffic)
- Databases requiring single-node performance
- Services with high memory requirements (graph algorithms)

**Scaling Triggers:**

- CPU sustained >80% for 15 minutes
- Memory sustained >85% for 15 minutes
- Disk I/O saturation (>80% utilization)

### Geographic Scaling

**Multi-Region Deployment:**

- **US-East:** Primary region (US customers)
- **EU-West:** Secondary region (EU customers, GDPR compliance)
- **AP-Southeast:** Future expansion (APAC customers)

**Request Routing:**

- Cloudflare geo-routing based on client location
- API Gateway in each region
- Data residency enforcement (EU data stays in EU)

**Cross-Region Communication:**

- Asynchronous replication (eventual consistency)
- Conflict resolution via last-write-wins with vector clocks
- Critical data: Synchronous replication (higher latency)

---

## Migration & Upgrade Strategy

### Zero-Downtime Deployments

**Rolling Update Strategy:**

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
```

- Deploy new version alongside old version
- Health checks validate new version
- Gradually shift traffic to new version
- Rollback if error rate increases

**Blue-Green Deployments:**

For major versions or risky changes:
- Deploy new version ("green") in parallel to current ("blue")
- Test green environment with synthetic traffic
- Switch traffic to green (DNS/load balancer update)
- Keep blue environment running for quick rollback
- Decommission blue after validation period

**Database Migrations:**

**Backward-Compatible Migrations:**

1. Deploy schema changes compatible with both versions
2. Deploy new application version
3. Backfill data (if needed)
4. Deploy cleanup migration removing old schema

**Example: Adding Column**

- V1: Add column as nullable
- Deploy application using new column
- Backfill historical data
- V2: Make column non-nullable (after validation)

**Breaking Changes:**

- Use database migration tools (Flyway, Liquibase)
- Version migrations (V001, V002, ...)
- Test migrations on production-like data
- Measure migration duration
- Schedule during maintenance window if long-running

### API Versioning

**Strategy:** URL-based versioning

- `/v1/threat-models` (current stable)
- `/v2/threat-models` (new version)
- Maintain v1 for 12 months after v2 release
- Deprecation warnings in v1 responses
- Clear migration guide for v1 → v2

**Backward Compatibility:**

- Additive changes (new fields) don't require version bump
- Breaking changes (removed/renamed fields, changed behavior) require new version
- Default values for new required fields

### Data Migration

**Graph Database Evolution:**

Neo4j schema changes:
- Add node labels and relationship types (non-breaking)
- Use Cypher migrations for data transformations
- Parallel run old and new queries during transition
- Verify data consistency before deprecating old schema

**Vector Store Updates:**

When changing embedding model or dimensions:
- Create new Qdrant collection
- Re-embed all threat patterns in background
- A/B test old vs new embeddings
- Switch traffic to new collection
- Archive old collection

---

## Cost Optimization

### Infrastructure Costs

**Compute:**

- **Kubernetes Nodes:** Right-size based on actual usage
  - Use node auto-scaling (scale down during off-peak hours)
  - Spot instances for non-critical workloads (60-70% cost savings)
  - Reserved instances for baseline capacity (30-40% savings)
  
**Databases:**

- **PostgreSQL:** Use managed service (RDS, Cloud SQL)
  - Right-size instance type (monitor CPU, memory, IOPS)
  - Use read replicas only when needed
  - Enable storage auto-scaling
  
- **Neo4j:** Self-hosted on Kubernetes (no managed service cost)
  - Use persistent volumes on cheaper storage tiers
  - Optimize query performance to reduce resource needs

**Storage:**

- **Hot Storage (S3 Standard):** Recent reports, architecture diagrams
- **Warm Storage (S3 Infrequent Access):** 30-90 day old reports (50% savings)
- **Cold Storage (S3 Glacier):** Long-term archives >90 days (80% savings)
- Lifecycle policies for automatic tiering

### AI API Costs

**LLM Usage Optimization:**

**Prompt Optimization:**
- Reduce token usage (concise prompts, remove unnecessary context)
- Use system message caching (supported by Anthropic Claude)
- Batch multiple analyses in single API call when possible

**Model Selection:**
- **GPT-4o-mini:** Simple architectures, cost $0.15/1M tokens (vs $5/1M for GPT-4o)
- **GPT-4o:** Complex architectures requiring deep analysis
- **Claude Opus 4:** Cross-validation for critical systems only
- Dynamic selection based on architecture complexity score

**Response Caching:**
- Cache LLM responses for identical inputs (40% cost reduction observed)
- Cache key: Hash of (architecture, framework, threat category)
- TTL: 30 days (threat patterns don't change frequently)

**Budget Controls:**
- Set monthly budget alerts ($1K, $5K, $10K thresholds)
- Rate limiting per user/organization
- Disable AI features if budget exceeded (fallback to rule-based)

**Cost Monitoring:**

Track per-request AI costs:
- Log token usage per analysis
- Calculate cost per threat model
- Monitor cost trends (weekly, monthly)
- Alert on cost anomalies (>2x average)

**Estimated Costs:**

- Simple architecture (20 components): $0.10-$0.50
- Complex architecture (100+ components): $1-$5
- Target: <$2 average per analysis

### Data Transfer Costs

**Minimize Cross-Region Transfer:**

- Keep data in same region as compute (co-locate databases with services)
- Use CDN for static assets (reduce origin requests)
- Compress API responses (gzip/brotli)
- Batch database queries (reduce query count)

**Egress Optimization:**

- Use CloudFlare or Cloudfront (cheaper egress than cloud providers)
- Cache aggressively (reduce origin traffic)
- Compress images and reports

---

## Future Enhancements

### Roadmap (6-12 Months)

**1. Advanced AI Capabilities**

- **Multi-Modal Analysis:** Process architecture diagrams (images) directly without text conversion
- **AI-Powered Remediation:** Automatically generate code/config patches for mitigations
- **Predictive Threat Modeling:** ML models predict threats based on technology stack alone
- **Natural Language Queries:** "Show me all SQL injection threats in payment services"

**2. Enhanced Collaboration**

- **Real-Time Collaboration:** Google Docs-style simultaneous editing
- **Threat Model Templates Marketplace:** Community-contributed templates
- **Security Champions Program:** Gamification, badges, leaderboards
- **Slack/Teams Bots:** Query threat models via chat interface

**3. Deeper Integrations**

- **Cloud Provider Native Integration:**
  - AWS: Ingest VPC Flow Logs, CloudTrail, Config
  - Azure: Azure Monitor, Defender integration
  - GCP: Security Command Center integration
- **SIEM Integration:** Splunk, QRadar, ArcSight
- **Ticketing Beyond Jira/GitHub:** ServiceNow, Linear, Asana
- **Code Repository Analysis:** Automatic architecture extraction from codebase

**4. Advanced Threat Intelligence**

- **Private Threat Intel Feeds:** Organization-specific threat data
- **Threat Actor Profiling:** Industry-specific threat actor campaigns
- **IoC Integration:** Indicators of Compromise correlation
- **Threat Hunting:** Proactive threat discovery based on emerging patterns

**5. Compliance Automation**

- **Automated Evidence Collection:** Screenshots, logs, configurations
- **Continuous Compliance Monitoring:** Real-time compliance posture tracking
- **Audit Preparation Workflows:** Generate complete audit packages
- **Custom Compliance Frameworks:** Support organization-specific requirements

**6. Enhanced Visualization**

- **3D Threat Graphs:** Interactive 3D visualization of attack paths
- **Attack Simulation:** Visual playback of attack scenarios
- **Risk Heat Maps:** Geographic and architecture-based risk visualization
- **Trend Analysis Dashboards:** Security posture over time

**7. Performance & Scale**

- **Graph Sharding:** Scale Neo4j beyond single cluster limits
- **Edge Computing:** Deploy threat analysis closer to users (reduced latency)
- **Streaming Analysis:** Real-time threat identification as architecture changes
- **GPU Acceleration:** Faster embedding generation and ML inference

### Research Areas

**1. Automated Mitigation Verification**

- Integrate with CI/CD to verify mitigations actually implemented
- Continuous validation of security controls
- Automated regression detection

**2. Threat Model Diff & Merge**

- Git-like branching and merging for threat models
- Conflict resolution for concurrent changes
- Automated merge of compatible changes

**3. Federated Threat Intelligence**

- Decentralized threat intelligence sharing
- Privacy-preserving threat pattern exchange
- Industry-specific threat communities

**4. Zero-Knowledge Threat Modeling**

- Analyze architectures without exposing sensitive details to AI APIs
- Homomorphic encryption for threat analysis
- On-premise AI model deployment option

---

## Appendix

### Glossary

**Architecture Model:** Unified internal representation of system architecture containing components, data flows, trust boundaries, and assets.

**Attack Surface:** The sum of all entry points where an attacker could interact with a system.

**Attack Tree:** Hierarchical diagram showing attack paths with AND/OR logic gates.

**Attack Vector:** Method or pathway used to exploit a vulnerability.

**CVSS:** Common Vulnerability Scoring System - standardized risk scoring method.

**CWE:** Common Weakness Enumeration - classification of software weaknesses.

**CVE:** Common Vulnerabilities and Exposures - publicly known security vulnerabilities.

**Data Flow:** Movement of data between system components across trust boundaries.

**Framework Engine:** Component supporting multiple threat modeling frameworks (STRIDE, PASTA, VAST).

**Impact Score:** Severity of consequences if a threat is realized (0-100).

**Likelihood Score:** Probability of threat exploitation (0-100).

**MITRE ATT&CK:** Knowledge base of adversary tactics, techniques, and procedures.

**PASTA:** Process for Attack Simulation and Threat Analysis framework.

**Risk Score:** Numerical value combining likelihood and impact (0-100).

**STRIDE:** Microsoft threat modeling framework (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).

**Threat Actor:** Entity capable of carrying out attacks (insider, cybercriminal, nation-state).

**Threat Graph:** Neo4j graph database storing threats, vulnerabilities, assets, and relationships.

**Trust Boundary:** Security perimeter where trust levels or privileges change.

**VAST:** Visual, Agile, and Simple Threat modeling framework.

### References

**Standards & Frameworks:**

- STRIDE: [Microsoft Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- PASTA: [Risk Centric Threat Modeling Methodology](https://versprite.com/blog/what-is-pasta-threat-modeling/)
- VAST: [ThreatModeler VAST](https://threatmodeler.com/threat-modeling-methodologies/)
- MITRE ATT&CK: [https://attack.mitre.org/](https://attack.mitre.org/)
- OWASP Top 10: [https://owasp.org/Top10/](https://owasp.org/Top10/)
- CWE Top 25: [https://cwe.mitre.org/top25/](https://cwe.mitre.org/top25/)
- CVSS: [https://www.first.org/cvss/](https://www.first.org/cvss/)

**Compliance Frameworks:**

- GDPR: [https://gdpr.eu/](https://gdpr.eu/)
- SOC 2: [AICPA Trust Services Criteria](https://us.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report)
- ISO 27001:2022: [https://www.iso.org/standard/27001](https://www.iso.org/standard/27001)
- HIPAA: [HHS Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- PCI-DSS v4.0: [https://www.pcisecuritystandards.org/](https://www.pcisecuritystandards.org/)

**Technology Documentation:**

- Neo4j: [https://neo4j.com/docs/](https://neo4j.com/docs/)
- LangChain: [https://python.langchain.com/](https://python.langchain.com/)
- Qdrant: [https://qdrant.tech/documentation/](https://qdrant.tech/documentation/)
- Kubernetes: [https://kubernetes.io/docs/](https://kubernetes.io/docs/)
- Istio: [https://istio.io/latest/docs/](https://istio.io/latest/docs/)

---

## Document Approval

**Prepared By:** AI Systems Architecture Team  
**Review Date:** June 24, 2026  
**Approval Status:** Pending Review

**Reviewers:**

- [ ] Security Architecture Team
- [ ] Platform Engineering Team  
- [ ] Compliance Officer
- [ ] Chief Technology Officer

**Next Steps:**

1. Review and approval by stakeholders
2. Creation of detailed architecture document
3. Creation of system diagrams (15 comprehensive diagrams)
4. Implementation planning and sprint breakdown
5. Proof-of-concept development

---

**Document Version:** 1.0  
**Last Updated:** June 24, 2026  
**Status:** Draft - Pending Review

