# Technology Stack

**Comprehensive catalog of data governance and management technologies**

---

## Overview

This document catalogs modern technologies, tools, and platforms for implementing data governance, quality, security, lineage, privacy, and observability across enterprise data ecosystems.

**Tool Selection Criteria:**
- **Capabilities** - Features and functionality
- **Integration** - Ecosystem compatibility
- **Scalability** - Performance at enterprise scale
- **Vendor** - Company stability and support
- **Cost** - Licensing and TCO
- **Cloud Support** - AWS, Azure, GCP compatibility

---

## 1. Data Catalogs

### Overview
Data catalogs provide searchable inventories of data assets with automated metadata discovery, business glossary, and data lineage.

### Enterprise Solutions

#### Collibra Data Intelligence Platform
- **Type:** Enterprise data catalog and governance platform
- **Key Features:**
  - Business glossary and data dictionary
  - Workflow automation for data governance
  - Data lineage visualization
  - Policy management
  - Data quality integration
- **Integration:** Broad connectors (200+)
- **Deployment:** Cloud (SaaS) or On-premises
- **Best For:** Large enterprises with complex governance needs
- **Pricing:** Quote-based ($$$$)

#### Alation Data Catalog
- **Type:** Collaborative data catalog with behavioral intelligence
- **Key Features:**
  - Machine learning-driven metadata enrichment
  - Query-based lineage from SQL logs
  - Behavioral analytics (popular datasets, experts)
  - Built-in collaboration (comments, questions)
  - Stewardship workflows
- **Integration:** 100+ data sources
- **Deployment:** Cloud or On-premises
- **Best For:** Data-driven organizations prioritizing collaboration
- **Pricing:** Quote-based ($$$$)

#### Informatica Enterprise Data Catalog
- **Type:** AI-powered metadata management and catalog
- **Key Features:**
  - Claire AI engine for automated classification
  - Deep column-level lineage
  - Enterprise-scale metadata management
  - Integration with Informatica suite
  - Sensitive data discovery
- **Integration:** Tight Informatica ecosystem integration
- **Deployment:** Cloud, Hybrid, On-premises
- **Best For:** Informatica customers, regulated industries
- **Pricing:** Quote-based ($$$$)

### Open Source / Cloud-Native

#### Apache Atlas
- **Type:** Open-source metadata management for Hadoop ecosystem
- **Key Features:**
  - Metadata repository
  - Classification engine
  - REST API
  - Tight Hadoop integration
- **Integration:** Hadoop, Hive, Spark, Kafka
- **Deployment:** Self-hosted
- **Best For:** Hadoop-centric environments, budget-conscious
- **Pricing:** Free (Open Source)

#### AWS Glue Data Catalog
- **Type:** Fully managed metadata repository for AWS
- **Key Features:**
  - Automatic schema discovery
  - ETL job integration
  - Serverless architecture
  - Athena, Redshift, EMR integration
- **Integration:** AWS services (native)
- **Deployment:** AWS Cloud only
- **Best For:** AWS-native data lakes
- **Pricing:** Pay-per-use ($)

#### Azure Purview (Microsoft Purview)
- **Type:** Unified data governance service for Azure and beyond
- **Key Features:**
  - Automated data discovery and classification
  - Sensitive data scanning
  - Data lineage visualization
  - Integration with Microsoft 365
  - Multi-cloud support (AWS, GCP)
- **Integration:** Azure, Microsoft 365, SAP, Oracle
- **Deployment:** Azure Cloud
- **Best For:** Microsoft-centric enterprises, multi-cloud
- **Pricing:** Pay-per-use ($$)

#### DataHub (LinkedIn)
- **Type:** Open-source metadata platform
- **Key Features:**
  - Modern UI with search and discovery
  - Real-time metadata updates
  - Extensible plugin architecture
  - REST and GraphQL APIs
- **Integration:** Kafka, Snowflake, BigQuery, Postgres
- **Deployment:** Self-hosted or Managed (Acryl Data)
- **Best For:** Modern data stacks, developer-friendly
- **Pricing:** Free (Open Source), Managed ($$$)

---

## 2. Data Quality Tools

### Enterprise Solutions

#### Informatica Data Quality
- **Type:** Comprehensive data quality and MDM platform
- **Key Features:**
  - Data profiling and cleansing
  - Real-time and batch quality checks
  - Address verification and standardization
  - Duplicate detection and matching
  - Pre-built quality rules library
- **Integration:** Broad enterprise system support
- **Deployment:** Cloud, Hybrid, On-premises
- **Best For:** Enterprise data quality at scale
- **Pricing:** Quote-based ($$$$)

#### Talend Data Quality
- **Type:** Open-source and commercial data quality platform
- **Key Features:**
  - Visual quality rule design
  - Pattern-based profiling
  - Match and merge capabilities
  - Real-time quality monitoring
- **Integration:** Wide connector library
- **Deployment:** Cloud or On-premises
- **Best For:** Mid-market to enterprise
- **Pricing:** Open Source (free), Enterprise ($$$)

#### Ataccama ONE
- **Type:** AI-powered data quality and governance platform
- **Key Features:**
  - Machine learning-driven quality rules
  - Real-time data quality
  - Master data management
  - Self-service data preparation
- **Integration:** Broad enterprise connectivity
- **Deployment:** Cloud or On-premises
- **Best For:** Complex quality requirements, MDM
- **Pricing:** Quote-based ($$$$)

### Open Source / Developer Tools

#### Great Expectations
- **Type:** Open-source data validation framework (Python)
- **Key Features:**
  - Expectation-based validation (assertions)
  - Data documentation generation
  - Profiling and exploration
  - Integration with data pipelines
  - Version control for data tests
- **Integration:** Pandas, Spark, SQL databases
- **Deployment:** Embedded in pipelines
- **Best For:** Data engineers, DataOps workflows
- **Pricing:** Free (Open Source), Cloud ($)

#### Deequ (Amazon)
- **Type:** Data quality library for Apache Spark (Scala)
- **Key Features:**
  - Unit tests for data
  - Constraint verification
  - Metrics computation
  - Anomaly detection
- **Integration:** Spark, AWS Glue
- **Deployment:** Embedded in Spark jobs
- **Best For:** Spark-based data pipelines
- **Pricing:** Free (Open Source)

#### Soda Core
- **Type:** Open-source data quality testing framework
- **Key Features:**
  - YAML-based quality checks
  - CLI and programmatic API
  - Anomaly detection
  - Integration with orchestration tools
- **Integration:** Snowflake, BigQuery, Postgres, Spark
- **Deployment:** Embedded in workflows
- **Best For:** Modern data stacks, DataOps
- **Pricing:** Free (Open Source), Cloud ($$)

---

## 3. Master Data Management (MDM)

### Enterprise Solutions

#### Informatica MDM
- **Type:** Multi-domain MDM platform (customer, product, supplier)
- **Key Features:**
  - 360-degree entity views
  - Hierarchy management
  - Match and merge engine
  - Data stewardship workbench
  - Real-time and batch processing
- **Deployment:** Cloud, Hybrid, On-premises
- **Best For:** Large enterprises, multiple domains
- **Pricing:** Quote-based ($$$$)

#### SAP Master Data Governance
- **Type:** SAP-native MDM solution
- **Key Features:**
  - Tight SAP S/4HANA integration
  - Central governance workflows
  - Mass data processing
  - Consolidation and synchronization
- **Deployment:** SAP Cloud or On-premises
- **Best For:** SAP customers
- **Pricing:** SAP licensing ($$$$)

#### Profisee
- **Type:** Cloud-native multi-domain MDM
- **Key Features:**
  - Fast deployment (weeks)
  - Stewardship portal
  - Survivorship rules
  - Hierarchies and relationships
- **Deployment:** Microsoft Azure
- **Best For:** Mid-market, quick MDM implementation
- **Pricing:** Subscription-based ($$$)

#### Semarchy xDM
- **Type:** Smart MDM platform with data unification
- **Key Features:**
  - Model-driven architecture
  - Agile MDM approach
  - Continuous data quality
  - Built-in stewardship
- **Deployment:** Cloud or On-premises
- **Best For:** Agile MDM, quick time-to-value
- **Pricing:** Subscription-based ($$$)

---

## 4. Data Lineage Tools

### Specialized Lineage Solutions

#### Manta
- **Type:** End-to-end automated data lineage
- **Key Features:**
  - Code-level lineage extraction
  - Column-level lineage
  - Impact analysis
  - Support for 20+ technologies
  - Scanner-based automation
- **Integration:** ETL tools, databases, BI platforms
- **Deployment:** On-premises or Private Cloud
- **Best For:** Complex enterprise environments
- **Pricing:** Quote-based ($$$$)

#### Octopai
- **Type:** Automated metadata discovery and lineage
- **Key Features:**
  - Cross-platform lineage
  - BI report lineage
  - Automated discovery
  - Collaboration features
- **Integration:** BI tools, ETL, databases
- **Deployment:** SaaS
- **Best For:** BI-heavy organizations
- **Pricing:** Subscription-based ($$$)

#### MANTA by Collibra (acquired)
- **Type:** Automated lineage for Collibra users
- **Integration:** Native Collibra integration
- **Best For:** Collibra customers

---

## 5. Access Governance & Identity Management

### Enterprise Solutions

#### Okta Identity Cloud
- **Type:** Identity and access management platform
- **Key Features:**
  - Single Sign-On (SSO)
  - Multi-Factor Authentication (MFA)
  - Lifecycle management
  - API access management
  - Universal Directory
- **Integration:** 7,000+ pre-built integrations
- **Deployment:** Cloud (SaaS)
- **Best For:** Cloud-first enterprises
- **Pricing:** Per user ($$$)

#### SailPoint IdentityIQ
- **Type:** Enterprise identity governance platform
- **Key Features:**
  - Access certification campaigns
  - Provisioning and de-provisioning
  - Role-based access control (RBAC)
  - Compliance reporting
  - Privileged access management
- **Integration:** Enterprise applications (ERP, CRM, HR)
- **Deployment:** Cloud or On-premises
- **Best For:** Large enterprises, compliance-heavy
- **Pricing:** Quote-based ($$$$)

#### Saviynt
- **Type:** Cloud-native identity governance
- **Key Features:**
  - IGA (Identity Governance & Administration)
  - Privileged access management
  - Third-party risk management
  - Data access governance
- **Integration:** Cloud and on-prem applications
- **Deployment:** Cloud
- **Best For:** Cloud transformation, data access control
- **Pricing:** Subscription-based ($$$)

#### Azure Active Directory (Entra ID)
- **Type:** Microsoft's cloud-based identity service
- **Key Features:**
  - SSO and MFA
  - Conditional access policies
  - B2B and B2C identity
  - Integration with Microsoft 365
- **Integration:** Microsoft ecosystem, SAML/OAuth apps
- **Deployment:** Azure Cloud
- **Best For:** Microsoft-centric environments
- **Pricing:** Per user ($ - $$$)

---

## 6. Data Masking & Anonymization

### Enterprise Solutions

#### Delphix
- **Type:** Data masking and test data management platform
- **Key Features:**
  - Irreversible masking algorithms
  - Format-preserving encryption
  - Referential integrity preservation
  - Virtual data copies
  - Compliance automation
- **Deployment:** Appliance or Cloud
- **Best For:** DevOps, non-production environments
- **Pricing:** Quote-based ($$$$)

#### IRI FieldShield
- **Type:** Data masking and privacy protection
- **Key Features:**
  - Static and dynamic masking
  - Tokenization
  - Format-preserving encryption
  - GDPR compliance features
- **Deployment:** On-premises
- **Best For:** Cost-effective masking
- **Pricing:** Perpetual license ($$$)

#### K2View
- **Type:** Micro-database and masking platform
- **Key Features:**
  - Entity-centric data virtualization
  - Real-time masking
  - Synthetic data generation
  - GDPR compliance
- **Deployment:** Cloud or On-premises
- **Best For:** Real-time data access with masking
- **Pricing:** Quote-based ($$$$)

### Open Source

#### ARX Data Anonymization Tool
- **Type:** Open-source anonymization framework
- **Key Features:**
  - K-anonymity, L-diversity
  - Differential privacy
  - Risk analysis
  - GUI and Java API
- **Best For:** Research, small-scale anonymization
- **Pricing:** Free (Open Source)

---

## 7. Privacy Management Platforms

### Enterprise Solutions

#### OneTrust
- **Type:** Comprehensive privacy and GRC platform
- **Key Features:**
  - Consent management
  - Data subject rights (DSR) automation
  - Privacy impact assessments (PIA)
  - Cookie compliance
  - Third-party risk management
  - 100+ privacy regulations coverage
- **Integration:** 500+ integrations
- **Deployment:** Cloud (SaaS)
- **Best For:** Enterprises with global privacy needs
- **Pricing:** Quote-based ($$$$)

#### TrustArc
- **Type:** Privacy management and compliance platform
- **Key Features:**
  - Privacy assessments
  - Consent management
  - Data inventory and mapping
  - Regulatory intelligence
  - Cookie and advertising compliance
- **Integration:** Marketing and analytics tools
- **Deployment:** Cloud (SaaS)
- **Best For:** Marketing-heavy organizations
- **Pricing:** Subscription-based ($$$)

#### BigID
- **Type:** Data discovery and privacy intelligence
- **Key Features:**
  - Automated PII/PHI discovery
  - Data classification
  - DSR workflow automation
  - Residency and localization
  - Privacy-by-design APIs
- **Integration:** Cloud and on-prem data stores
- **Deployment:** SaaS or Private Cloud
- **Best For:** Data discovery, complex environments
- **Pricing:** Subscription-based ($$$)

#### Securiti.ai
- **Type:** Privacy and data governance automation
- **Key Features:**
  - AI-driven data discovery
  - Consent orchestration
  - DSR automation
  - Privacy engineering platform
- **Integration:** Cloud-native integrations
- **Deployment:** Cloud
- **Best For:** Modern cloud environments
- **Pricing:** Subscription-based ($$$)

---

## 8. Policy Enforcement & Access Control

### Enterprise Solutions

#### Apache Ranger
- **Type:** Open-source centralized policy framework
- **Key Features:**
  - Fine-grained access control
  - Dynamic data masking
  - Row/column-level security
  - Audit logging
  - Hadoop ecosystem focus
- **Integration:** HDFS, Hive, HBase, Kafka, Atlas
- **Deployment:** Self-hosted
- **Best For:** Hadoop/big data environments
- **Pricing:** Free (Open Source)

#### Open Policy Agent (OPA)
- **Type:** Open-source policy engine
- **Key Features:**
  - Policy-as-code (Rego language)
  - Decentralized policy enforcement
  - Cloud-native (Kubernetes, Envoy)
  - Context-aware decisions
- **Integration:** Kubernetes, microservices, APIs
- **Deployment:** Embedded or sidecar
- **Best For:** Cloud-native, microservices
- **Pricing:** Free (Open Source)

#### Immuta
- **Type:** Cloud-native data access control platform
- **Key Features:**
  - Automated policy enforcement
  - Attribute-based access control (ABAC)
  - Dynamic masking and anonymization
  - Purpose-based access
  - Multi-cloud support
- **Integration:** Snowflake, Databricks, Redshift, S3
- **Deployment:** Cloud or On-premises
- **Best For:** Cloud data platforms, self-service analytics
- **Pricing:** Subscription-based ($$$)

#### Privacera
- **Type:** Multi-cloud data governance and security
- **Key Features:**
  - Unified policy management
  - Fine-grained access control
  - Data masking and encryption
  - Cross-cloud governance
  - Built on Apache Ranger
- **Integration:** AWS, Azure, GCP, Databricks, Snowflake
- **Deployment:** SaaS or Self-managed
- **Best For:** Multi-cloud data environments
- **Pricing:** Subscription-based ($$$)

---

## 9. Data Observability & Monitoring

### Emerging Category - Data Reliability

#### Monte Carlo Data
- **Type:** End-to-end data observability platform
- **Key Features:**
  - Automated anomaly detection
  - Data downtime alerts
  - Lineage and impact analysis
  - Field-level monitoring
  - ML-powered anomaly detection
- **Integration:** 40+ data tools (warehouses, lakes, BI)
- **Deployment:** Cloud (SaaS)
- **Best For:** Modern data stacks, proactive monitoring
- **Pricing:** Subscription-based ($$$)

#### Datafold
- **Type:** Data diff and quality monitoring
- **Key Features:**
  - Cross-database diffing
  - CI/CD for data
  - Column-level lineage
  - Pre-deployment testing
- **Integration:** Snowflake, BigQuery, Databricks, Redshift
- **Deployment:** Cloud (SaaS)
- **Best For:** DataOps, deployment validation
- **Pricing:** Subscription-based ($$)

#### Bigeye
- **Type:** Data quality and observability platform
- **Key Features:**
  - Automated monitoring
  - Anomaly detection
  - Data lineage
  - Custom metrics
  - Slack/email alerts
- **Integration:** Major data warehouses and lakes
- **Deployment:** Cloud (SaaS)
- **Best For:** Fast-moving data teams
- **Pricing:** Subscription-based ($$$)

#### Databand
- **Type:** Data pipeline observability
- **Key Features:**
  - Pipeline monitoring
  - Data quality checks
  - Cost tracking
  - Failed run analysis
  - Integration with Airflow
- **Integration:** Airflow, Databricks, Snowflake, Spark
- **Deployment:** Cloud or On-premises
- **Best For:** Airflow users, pipeline-heavy
- **Pricing:** Subscription-based ($$)

---

## 10. Additional Tool Categories

### Data Integration & ETL

**Commercial:**
- Informatica PowerCenter / IICS
- Talend Data Integration
- Matillion (cloud ETL)
- Fivetran (automated connectors)

**Open Source:**
- Apache NiFi
- Apache Airflow (orchestration)
- Airbyte (open-source Fivetran)

### Data Warehouses / Lakes

**Cloud Data Warehouses:**
- Snowflake
- Google BigQuery
- Amazon Redshift
- Azure Synapse Analytics

**Data Lakehouses:**
- Databricks (Delta Lake)
- AWS Lake Formation
- Dremio

### Metadata Management

**Specialized:**
- Atlan (collaborative metadata)
- Select Star (automated docs)
- Metaphor (ML-driven catalog)

---

## Tool Comparison Matrix

| Category | Open Source Option | Mid-Market | Enterprise Leader |
|----------|-------------------|------------|-------------------|
| **Data Catalog** | Apache Atlas, DataHub | Alation | Collibra |
| **Data Quality** | Great Expectations | Talend DQ | Informatica DQ |
| **MDM** | - | Profisee | Informatica MDM |
| **Lineage** | - | Octopai | Manta |
| **IAM** | Keycloak | Okta | SailPoint |
| **Masking** | ARX | IRI FieldShield | Delphix |
| **Privacy** | - | BigID | OneTrust |
| **Policy** | OPA, Ranger | Immuta | Privacera |
| **Observability** | - | Datafold | Monte Carlo |

---

## Selection Framework

### Evaluation Criteria

**1. Functional Requirements**
- Core capabilities match needs
- Integration with existing stack
- Scalability to target data volumes

**2. Non-Functional Requirements**
- Performance (query speed, processing throughput)
- Availability and reliability
- Security and compliance certifications

**3. Total Cost of Ownership**
- Licensing costs
- Implementation services
- Training and onboarding
- Ongoing maintenance

**4. Vendor Considerations**
- Financial stability
- Roadmap alignment
- Support quality
- Community/ecosystem

**5. Technical Fit**
- Cloud vs. on-premises
- API and integration options
- Customization flexibility
- DevOps friendliness

### Decision Process

```
Requirements Gathering → Tool Shortlist → POC/Trial
     ↓
Vendor Demos → Technical Evaluation → Cost Analysis
     ↓
Reference Checks → Final Selection → Procurement
```

---

## Emerging Technologies

### AI-Powered Tools
- **Active metadata** with ML enrichment
- **Autonomous data quality** with self-healing
- **Predictive lineage** anticipating impacts

### Cloud-Native Architectures
- **Serverless catalogs** (AWS Glue, Azure Purview)
- **SaaS-first** governance platforms
- **Multi-cloud** governance (Privacera, Immuta)

### DataOps Integration
- **Policy-as-code** in Git (OPA)
- **Quality gates** in CI/CD (Great Expectations)
- **Automated testing** for data pipelines

---

## Summary

**Key Takeaways:**

1. **No Single Tool Solves Everything** - Expect 5-10 tools in governance stack
2. **Integration is Critical** - APIs and connectors matter
3. **Cloud-Native Trend** - SaaS adoption accelerating
4. **Open Source Growing** - Viable for many use cases
5. **Specialization Increasing** - Purpose-built tools outperform suites

**Typical Enterprise Stack:**
- Data Catalog: Collibra or Alation
- Data Quality: Informatica DQ or Great Expectations
- Lineage: Manta or Octopai
- IAM: Okta or Azure AD
- Privacy: OneTrust or BigID
- Observability: Monte Carlo or Datafold

---

**Status:** Complete ✅

**Related:** [README](README.md) | [Data Governance Guide](data-governance-guide.md) | [Data Handling Architectures](data-handling-architectures.md)
