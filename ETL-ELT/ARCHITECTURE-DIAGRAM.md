# ETL/ELT Architecture Diagrams

## High-Level Architecture

```mermaid
graph LR
    subgraph Sources
        A[Databases]
        B[APIs]
        C[Streaming]
        D[Files/Logs]
    end
    
    subgraph Ingestion
        E[AWS Glue]
        F[Kinesis]
        G[DMS]
        H[Lambda]
    end
    
    subgraph Raw["Raw Storage (S3)"]
        I[Landing Zone]
    end
    
    subgraph Transform
        J[Glue ETL]
        K[EMR/Spark]
        L[Athena]
        M[Lambda + Bedrock]
    end
    
    subgraph Curated["Curated Layer"]
        N[Redshift]
        O[S3 Data Lake]
        P[Feature Store]
    end
    
    subgraph Consumption
        Q[QuickSight]
        R[SageMaker]
        S[Bedrock Apps]
        T[APIs]
    end
    
    A & B & C & D --> E & F & G & H
    E & F & G & H --> I
    I --> J & K & L & M
    J & K & L & M --> N & O & P
    N & O & P --> Q & R & S & T
```

## ML/LLM Pipeline

```mermaid
graph TB
    subgraph Data["Data Sources"]
        DS1[Structured Data]
        DS2[Unstructured Docs]
        DS3[Real-time Events]
    end
    
    subgraph Ingestion["Ingestion Layer"]
        ING1[Glue/DMS]
        ING2[Textract/S3]
        ING3[Kinesis]
    end
    
    subgraph Raw["Raw Storage"]
        RAW[S3 Landing Zone]
    end
    
    subgraph Processing["Processing & Enrichment"]
        P1[Glue ETL<br/>Feature Engineering]
        P2[Bedrock<br/>Text Processing]
        P3[Lambda<br/>Real-time Transform]
    end
    
    subgraph MLOps["ML/LLM Layer"]
        ML1[SageMaker<br/>Training]
        ML2[Feature Store]
        ML3[Bedrock<br/>LLM Inference]
        ML4[Model Registry]
    end
    
    subgraph Serving["Serving Layer"]
        S1[SageMaker Endpoints]
        S2[Lambda + Bedrock]
        S3[Batch Predictions]
    end
    
    subgraph Apps["Applications"]
        APP1[BI Dashboards]
        APP2[ML-Powered Apps]
        APP3[LLM Chatbots]
        APP4[Automated Workflows]
    end
    
    DS1 --> ING1
    DS2 --> ING2
    DS3 --> ING3
    ING1 & ING2 & ING3 --> RAW
    RAW --> P1 & P2 & P3
    P1 --> ML1 & ML2
    P2 --> ML3
    P3 --> ML2
    ML1 --> ML4
    ML4 --> S1
    ML2 --> S1 & S3
    ML3 --> S2
    S1 & S2 & S3 --> APP1 & APP2 & APP3 & APP4
```

## ETL vs ELT Pattern

```mermaid
graph LR
    subgraph ETL["ETL Pattern"]
        E1[Extract] --> T1[Transform<br/>Glue/EMR]
        T1 --> L1[Load<br/>Redshift]
        L1 --> U1[Use<br/>BI Tools]
    end
    
    subgraph ELT["ELT Pattern"]
        E2[Extract] --> L2[Load<br/>S3 Raw]
        L2 --> T2[Transform<br/>Athena/Redshift]
        T2 --> U2[Use<br/>ML/Analytics]
    end
    
    style ETL fill:#e1f5ff
    style ELT fill:#fff4e1
```

## Data Flow with LLM Integration

```mermaid
sequenceDiagram
    participant S as Data Source
    participant I as Ingestion
    participant R as S3 Raw
    participant T as Transform
    participant B as Bedrock LLM
    participant C as Curated Layer
    participant A as Application
    
    S->>I: Extract Data
    I->>R: Store Raw
    R->>T: Load for Processing
    T->>B: Enrich with LLM
    B-->>T: Enhanced Data
    T->>C: Store Curated
    C->>A: Serve Data/Features
    A->>B: Real-time Inference
    B-->>A: Predictions/Insights
```

## Component Interaction

```mermaid
graph TD
    subgraph Input["Data Input"]
        I1[Batch Sources]
        I2[Streaming Sources]
        I3[API Sources]
    end
    
    subgraph Processing["Processing Layer"]
        P1{ETL or ELT?}
        P2[Glue ETL Jobs]
        P3[Load to S3]
        P4[Athena Queries]
        P5[Redshift Views]
    end
    
    subgraph ML["ML/LLM Layer"]
        M1[Feature Engineering]
        M2[SageMaker Training]
        M3[Bedrock LLM]
        M4[Model Deployment]
    end
    
    subgraph Output["Output Layer"]
        O1[Data Warehouse]
        O2[Data Lake]
        O3[Feature Store]
        O4[API Endpoints]
    end
    
    I1 & I2 & I3 --> P1
    P1 -->|ETL| P2
    P1 -->|ELT| P3
    P2 --> O1
    P3 --> P4 & P5
    P4 & P5 --> O2
    O1 & O2 --> M1
    M1 --> M2 & M3
    M2 --> M4
    M4 --> O3
    M3 --> O4
    O3 & O4 --> Output
```

## AWS Service Architecture

```mermaid
graph TB
    subgraph VPC["AWS VPC"]
        subgraph Compute["Compute"]
            Lambda[Lambda Functions]
            Glue[Glue Jobs]
            EMR[EMR Clusters]
        end
        
        subgraph Storage["Storage"]
            S3[S3 Buckets]
            RDS[RDS/Aurora]
            Redshift[Redshift]
        end
        
        subgraph ML["ML Services"]
            SM[SageMaker]
            BR[Bedrock]
            FS[Feature Store]
        end
        
        subgraph Orchestration["Orchestration"]
            SF[Step Functions]
            EB[EventBridge]
            MWAA[Airflow/MWAA]
        end
        
        subgraph Monitoring["Monitoring"]
            CW[CloudWatch]
            XR[X-Ray]
        end
    end
    
    subgraph External["External"]
        Sources[Data Sources]
        Users[End Users/Apps]
    end
    
    Sources --> Lambda & Glue
    Lambda & Glue --> S3
    S3 --> EMR & Redshift
    S3 --> SM & BR
    SM --> FS
    FS --> Users
    BR --> Users
    SF --> Lambda & Glue & EMR
    EB --> SF
    CW & XR -.-> Compute & ML
    
    style ML fill:#ff9
    style Compute fill:#9f9
    style Storage fill:#99f
```
