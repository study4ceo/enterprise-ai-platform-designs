# Compliance Requirements

**Guide to regulatory compliance requirements and data governance mapping**

---

## Overview

This document covers major regulatory frameworks affecting data governance, their specific requirements, penalties, and how data handling architectures enable compliance through technical and organizational controls.

**Compliance Landscape:**
- Global regulations (GDPR)
- Regional regulations (CCPA, LGPD)
- Industry-specific (HIPAA, PCI-DSS, SOX)
- Sector regulations (BCBS 239, MiFID II, FINRA)

---

## 1. GDPR (General Data Protection Regulation)

### Overview
**Jurisdiction:** European Union  
**Effective Date:** May 25, 2018  
**Scope:** Processing of EU residents' personal data, regardless of company location  
**Penalties:** Up to €20M or 4% of annual global revenue (whichever is higher)

### Key Principles

**1. Lawfulness, Fairness, and Transparency**
- Legal basis for processing (consent, contract, legal obligation, vital interests, public task, legitimate interest)
- Clear privacy notices
- Transparent processing activities

**2. Purpose Limitation**
- Data collected for specified, explicit purposes
- No further processing incompatible with original purpose

**3. Data Minimization**
- Adequate, relevant, limited to necessary
- Avoid over-collection

**4. Accuracy**
- Keep data accurate and up-to-date
- Right to rectification

**5. Storage Limitation**
- Retain only as long as necessary
- Defined retention periods

**6. Integrity and Confidentiality**
- Appropriate security measures
- Protection against unauthorized processing

**7. Accountability**
- Demonstrate compliance
- Document processes and decisions

### Key Requirements

#### Article 25: Data Protection by Design and by Default
- Privacy built into systems from start
- Default settings maximize privacy
- Regular testing and evaluation

**Architecture Implications:**
- Encryption by default
- Pseudonymization where possible
- Minimal data collection in design
- Privacy-preserving analytics

#### Article 30: Records of Processing Activities
- Maintain register of processing activities
- Document purposes, categories, recipients
- Retention periods and security measures

**Architecture Implications:**
- Automated data catalog
- Processing activity tracking
- Metadata management

#### Article 32: Security of Processing
- Pseudonymization and encryption
- Confidentiality, integrity, availability
- Regular testing and evaluation
- Incident response procedures

**Technical Measures:**
```yaml
Encryption:
  At Rest: AES-256
  In Transit: TLS 1.3
  In Use: Homomorphic encryption (advanced)

Access Control:
  Authentication: MFA required
  Authorization: RBAC + ABAC
  Audit: All access logged

Monitoring:
  SIEM: Real-time threat detection
  Anomaly Detection: ML-based
  Incident Response: <72 hour notification
```

#### Article 33 & 34: Breach Notification
- Notify supervisory authority within 72 hours
- Notify affected individuals if high risk
- Document breaches and responses

**Architecture Implications:**
- Automated breach detection
- Incident workflow automation
- Forensic logging capabilities

#### Data Subject Rights (Articles 15-22)

**Right to Access (Article 15)**
- Provide copy of personal data
- Information about processing

**Right to Rectification (Article 16)**
- Correct inaccurate data

**Right to Erasure (Article 17) - "Right to be Forgotten"**
- Delete data when no longer necessary
- User requests deletion

**Right to Restrict Processing (Article 18)**
- Limit processing under certain conditions

**Right to Data Portability (Article 20)**
- Receive data in machine-readable format
- Transmit to another controller

**Right to Object (Article 21)**
- Object to processing for direct marketing
- Object to automated decision-making

**Architecture Implications:**
- Self-service data access portals
- Automated deletion workflows
- Data export APIs (JSON, CSV)
- Consent management platforms
- Workflow automation for DSR (Data Subject Requests)

### Compliance Checklist

✅ Legal basis documented for all processing  
✅ Privacy notices clear and accessible  
✅ Consent mechanisms (where applicable)  
✅ Data protection impact assessments (DPIA) for high-risk processing  
✅ Data processing agreements (DPA) with processors  
✅ Records of processing activities maintained  
✅ Technical and organizational measures implemented  
✅ Breach notification procedures in place  
✅ DSR workflows operational  
✅ Data Protection Officer (DPO) appointed (if required)  
✅ Cross-border transfer mechanisms (SCCs, BCRs, adequacy decisions)  

### Architecture Patterns for GDPR

**Data Residency & Localization:**
```
EU Data → EU Region Storage
  ├─ Encrypted at rest (AES-256)
  ├─ Access restricted to EU-based staff
  └─ Logs retained in EU
```

**Consent Management:**
```
User → Consent Capture → Consent Store
  ↓
Processing Systems ← Consent Check ← Consent Service
```

**Right to Erasure:**
```
Deletion Request → Workflow → Identify All Data
  ↓
Hard Delete + Backup Marking → Verification → Confirmation
```

---

## 2. CCPA / CPRA (California Privacy Rights Act)

### Overview
**Jurisdiction:** California, USA  
**CCPA Effective:** January 1, 2020  
**CPRA Effective:** January 1, 2023  
**Scope:** Businesses doing business in California meeting thresholds  
**Penalties:** $2,500 per violation ($7,500 intentional), Private right of action ($100-$750 per consumer per incident)

### Thresholds (Any One)
- Gross annual revenue > $25M
- Buy/sell/share personal info of 100K+ consumers/households
- Derive 50%+ of revenue from selling personal info

### Consumer Rights

**Right to Know**
- What personal info is collected
- Sources of collection
- Business/commercial purposes
- Categories of third parties shared with

**Right to Delete**
- Request deletion of personal info
- Exceptions for legal compliance, fraud, security

**Right to Opt-Out**
- Opt-out of sale/sharing of personal info
- "Do Not Sell My Personal Information" link required

**Right to Correct** (CPRA)
- Correct inaccurate personal info

**Right to Limit Use** (CPRA)
- Limit use of sensitive personal info

**Right to Non-Discrimination**
- No penalties for exercising rights

### Sensitive Personal Information (CPRA)
- SSN, driver's license, passport
- Account login + security/access codes
- Precise geolocation
- Racial/ethnic origin, religion, union membership
- Contents of mail, email, text (not public)
- Genetic data, biometric info
- Health info, sex life/orientation

### Business Obligations

**Transparency**
- Privacy policy disclosures (categories, purposes, retention)
- Notice at collection
- Cookie/tracking disclosures

**Opt-Out Mechanisms**
- "Do Not Sell" link on homepage
- Honor Global Privacy Control (GPC) signals (CPRA)
- Opt-out for sensitive personal info use

**Contracts**
- Service provider agreements
- Processor certification

**Security**
- Reasonable security measures
- Breach notification (California Civil Code 1798.82)

### Architecture Implications

**Consent & Preference Management:**
```yaml
Components:
  - Consent Banner: Cookie consent, opt-out
  - Preference Center: Granular controls
  - GPC Signal Handler: Automatic opt-out
  - Consent Database: Audit trail
```

**Data Mapping:**
```
Personal Info Categories → Processing Purposes → Third Parties
  ↓
Retention Periods → Deletion Workflows
```

**DSR Automation:**
- Know: Generate data report (JSON/PDF)
- Delete: Cascade deletion across systems
- Opt-Out: Suppression lists, marketing blocks
- Correct: Data quality workflows

---

## 3. HIPAA (Health Insurance Portability and Accountability Act)

### Overview
**Jurisdiction:** United States  
**Effective Date:** 1996 (Privacy Rule 2003, Security Rule 2005)  
**Scope:** Covered entities (healthcare providers, health plans, clearinghouses) and business associates  
**Penalties:** $100-$50,000 per violation (up to $1.5M per year), Criminal penalties up to 10 years prison

### Protected Health Information (PHI)

**18 HIPAA Identifiers:**
1. Names
2. Geographic subdivisions smaller than state
3. Dates (except year)
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. SSN
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers and serial numbers
13. Device identifiers and serial numbers
14. URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any other unique identifying number/code

### HIPAA Security Rule - Three Safeguards

#### 1. Administrative Safeguards

**Security Management Process**
- Risk analysis
- Risk management
- Sanction policy
- Information system activity review

**Assigned Security Responsibility**
- Security official designated

**Workforce Security**
- Authorization/supervision procedures
- Workforce clearance
- Termination procedures

**Information Access Management**
- Isolate healthcare clearinghouse functions
- Access authorization
- Access establishment/modification

**Security Awareness and Training**
- Security reminders
- Protection from malicious software
- Log-in monitoring
- Password management

**Security Incident Procedures**
- Response and reporting

**Contingency Plan**
- Data backup plan
- Disaster recovery plan
- Emergency mode operation plan
- Testing and revision procedures
- Applications and data criticality analysis

**Business Associate Contracts**
- Written contract or assurance

#### 2. Physical Safeguards

**Facility Access Controls**
- Contingency operations
- Facility security plan
- Access control and validation
- Maintenance records

**Workstation Use**
- Proper use policies

**Workstation Security**
- Physical safeguards (locks, positioning)

**Device and Media Controls**
- Disposal procedures
- Media re-use procedures
- Accountability
- Data backup and storage

#### 3. Technical Safeguards

**Access Control**
- Unique user identification (required)
- Emergency access procedure (required)
- Automatic logoff (addressable)
- Encryption and decryption (addressable)

**Audit Controls**
- Hardware, software, procedural mechanisms to record and examine activity

**Integrity**
- Mechanisms to ensure PHI not improperly altered/destroyed

**Person or Entity Authentication**
- Verify identity before granting access

**Transmission Security**
- Integrity controls (addressable)
- Encryption (addressable)

### Architecture Requirements

**Encryption Standards:**
```yaml
Data at Rest:
  Algorithm: AES-256
  Key Management: HSM or KMS
  
Data in Transit:
  Protocol: TLS 1.2+ (TLS 1.3 recommended)
  Certificate: 2048-bit RSA minimum
  
Backups:
  Encrypted: Required
  Offsite Storage: Encrypted transport
```

**Access Controls:**
```yaml
Authentication:
  MFA: Required for remote access
  Password: Complexity requirements
  Biometric: Optional additional factor

Authorization:
  Model: RBAC with least privilege
  Break-the-Glass: Emergency access with audit
  Session: Timeout after inactivity
```

**Audit Logging:**
```yaml
Log Events:
  - Login/logout attempts
  - PHI access (view, edit, delete)
  - Configuration changes
  - Audit log access
  
Retention: Minimum 6 years
Immutability: WORM storage
Monitoring: SIEM integration
```

**Disaster Recovery:**
```yaml
RTO: <24 hours for critical systems
RPO: <1 hour data loss maximum
Backup Frequency: Daily incremental, weekly full
Geographic: Secondary site 100+ miles away
Testing: Annual DR drills
```

### HIPAA Compliance Checklist

✅ Risk analysis conducted and documented  
✅ Security policies and procedures written  
✅ Security official designated  
✅ Workforce training completed and documented  
✅ Business associate agreements (BAA) in place  
✅ Access controls implemented (unique IDs, MFA)  
✅ Audit logging enabled and monitored  
✅ Encryption implemented (at rest and in transit)  
✅ Contingency and disaster recovery plans  
✅ Incident response procedures documented  
✅ Physical security controls for facilities  
✅ Device and media disposal procedures  

---

## 4. SOX (Sarbanes-Oxley Act)

### Overview
**Jurisdiction:** United States  
**Effective Date:** 2002  
**Scope:** Publicly traded companies and accounting firms  
**Penalties:** $5M fine, 20 years prison for executives

### Key Sections Impacting Data

**Section 302: Corporate Responsibility**
- CEO/CFO certify accuracy of financial statements
- Certify internal controls effective

**Section 404: Management Assessment of Internal Controls**
- Annual internal control report
- Auditor attestation on controls

**Section 409: Real-Time Disclosures**
- Rapid disclosure of material changes

**Section 802: Criminal Penalties for Document Destruction**
- Destruction, alteration, falsification of records
- Criminal penalties

### Data Governance Requirements

**Financial Data Integrity**
- Accurate financial records
- Audit trails for all transactions
- Change control for financial systems

**Internal Controls**
- IT general controls (ITGC)
- Application controls
- Access controls

**Audit Trail**
- Immutable logs
- Who, what, when, where
- 7-year retention

**Change Management**
- Documented procedures
- Approval workflows
- Segregation of duties

### Architecture Implications

**Immutable Audit Logs:**
```yaml
Storage:
  Type: Write-Once-Read-Many (WORM)
  Technology: S3 Object Lock, Azure Immutable Blob
  Retention: 7 years minimum
  
Log Contents:
  - User identity
  - Timestamp (UTC)
  - Action performed
  - Before/after values
  - IP address
  - Session ID
```

**Change Control:**
```yaml
Workflow:
  Request → Approval (Manager + IT) → Implementation
  ↓
  Testing → Verification → Documentation
  ↓
  Audit Trail → Compliance Review
```

**Segregation of Duties:**
```
Developer ≠ Production Access
Approver ≠ Implementer
Auditor ≠ System Administrator
```

**Database Change Tracking:**
```sql
-- Temporal tables (SQL Server)
CREATE TABLE FinancialTransactions
(
    TransactionID INT PRIMARY KEY,
    Amount DECIMAL(18,2),
    StartTime DATETIME2 GENERATED ALWAYS AS ROW START,
    EndTime DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (StartTime, EndTime)
)
WITH (SYSTEM_VERSIONING = ON);
```

---

## 5. PCI-DSS (Payment Card Industry Data Security Standard)

### Overview
**Jurisdiction:** Global (card brand requirement)  
**Current Version:** 4.0 (March 2022)  
**Scope:** Any organization storing, processing, or transmitting cardholder data  
**Penalties:** $5,000-$100,000 per month fines, loss of card processing rights

### 12 Requirements (6 Goals)

#### Goal 1: Build and Maintain Secure Network
**Requirement 1:** Install and maintain network security controls
- Firewalls, network segmentation

**Requirement 2:** Apply secure configurations
- Vendor defaults changed, hardening

#### Goal 2: Protect Cardholder Data
**Requirement 3:** Protect stored cardholder data
- Minimize storage, encrypt/mask, key management

**Requirement 4:** Protect cardholder data with strong cryptography
- TLS/VPN for transmission, end-to-end encryption

#### Goal 3: Maintain Vulnerability Management
**Requirement 5:** Protect systems from malware
- Anti-malware, detection mechanisms

**Requirement 6:** Develop secure systems and software
- Secure SDLC, patch management, change control

#### Goal 4: Implement Strong Access Control
**Requirement 7:** Restrict access by business need-to-know
- RBAC, least privilege

**Requirement 8:** Identify users and authenticate access
- Unique IDs, MFA, password standards

**Requirement 9:** Restrict physical access
- Facility access, visitor logs, device protection

#### Goal 5: Monitor and Test Networks
**Requirement 10:** Log and monitor all access
- Audit logs, log review, SIEM

**Requirement 11:** Test security systems and processes
- Vulnerability scans, penetration testing

#### Goal 6: Maintain Information Security Policy
**Requirement 12:** Support information security with policies
- Security policy, risk assessment, personnel awareness

### Cardholder Data Elements

**Primary Account Number (PAN)** - Most critical
- 13-19 digits
- Must be encrypted/tokenized if stored

**Sensitive Authentication Data (SAD)** - NEVER store after authorization
- Full magnetic stripe
- CAV2/CVC2/CVV2/CID
- PINs/PIN blocks

**Additional Cardholder Data** (can store if needed):
- Cardholder name
- Expiration date
- Service code

### Data Protection Methods

**Tokenization:**
```
Real PAN: 4532-1234-5678-9010
Token:    4532-XXXX-XXXX-8765 (format-preserving)

Mapping stored in secure vault, not in primary systems
```

**Encryption:**
```yaml
Standards:
  Symmetric: AES-256
  Asymmetric: RSA 2048-bit or ECC 256-bit
  
Key Management:
  Rotation: Annual minimum
  Storage: HSM or KMS
  Access: Split knowledge, dual control
```

**Masking:**
```
Display: 4532-****-****-9010 (show last 4)
Logs:    **** (fully redacted)
```

### Architecture Patterns

**Network Segmentation:**
```
DMZ (Public) → Firewall → Cardholder Data Environment (CDE)
  ↓
Internal Network (Non-CDE)
```

**Tokenization Architecture:**
```
Application → API Gateway → Tokenization Service
  ↓                           ↓
Non-CDE Database        Secure Vault (CDE)
(Tokens only)           (Real PANs encrypted)
```

**Logging & Monitoring:**
```yaml
Log Sources:
  - All access to cardholder data
  - Administrative actions
  - Authentication attempts
  - Audit log access
  
Centralization: SIEM required
Retention: 1 year online, 3 months immediately available
Review: Daily
```

---

## 6. BCBS 239 (Basel Committee Banking Supervision)

### Overview
**Jurisdiction:** Global banking (Basel Committee countries)  
**Effective Date:** January 2016  
**Scope:** Systemically important banks (SIBs)  
**Purpose:** Risk data aggregation and reporting

### 14 Principles (4 Groups)

#### Overarching Governance & Infrastructure (1-4)
1. Governance
2. Data architecture and IT infrastructure
3. Accuracy and integrity
4. Completeness

#### Risk Data Aggregation Capabilities (5-8)
5. Timeliness
6. Adaptability
7. Accuracy
8. Comprehensiveness

#### Risk Reporting Practices (9-11)
9. Clarity and usefulness
10. Frequency
11. Distribution

#### Review (12-14)
12. Remedial actions and supervisory measures
13. Home/host supervisory cooperation
14. Implementation

### Data Architecture Requirements

**Key Principles:**

**Principle 2: Data Architecture**
- Accurate and reliable risk data
- Flexible and adaptable
- Data lineage and traceability
- Automated data flows

**Principle 3: Accuracy and Integrity**
- Data reconciliation
- Controls and validations
- Minimize manual processes

**Principle 5: Timeliness**
- Generate reports within regulatory deadlines
- Intraday capability for critical reports

### Architecture Implications

**Data Lineage:**
```
Source Systems → Staging → Integration → Data Warehouse
  ↓                ↓           ↓            ↓
Lineage         Lineage    Lineage      Lineage
Metadata        Metadata   Metadata     Metadata
```

**Reconciliation Framework:**
```yaml
Controls:
  - Source to target record counts
  - Sum/balance checks
  - Referential integrity
  - Business rule validation
  - Manual override tracking
  
Frequency: Real-time or daily
Reporting: Exception-based
```

**Automation:**
```
Manual Processes → Risk Analysis → Automation Roadmap
  ↓
Automated Workflows → Validation → Monitoring
```

---

## 7. Industry-Specific Regulations

### Financial Services

**MiFID II (EU)**
- Markets in Financial Instruments Directive
- Transaction reporting (T+1)
- Best execution records
- Record retention (5-7 years)

**FINRA (US)**
- Electronic communications retention
- Supervision and review
- Books and records requirements

**GLBA (Gramm-Leach-Bliley Act, US)**
- Financial privacy notices
- Safeguards Rule (administrative, technical, physical)
- Pretexting protection

### Healthcare

**HITECH Act**
- Enhanced HIPAA enforcement
- Breach notification requirements
- EHR meaningful use incentives

**21 CFR Part 11 (FDA)**
- Electronic records and signatures
- Audit trails
- Validation
- Legacy system requirements

### Telecommunications

**TCPA (Telephone Consumer Protection Act)**
- Consent for marketing calls/texts
- Do Not Call registry
- ATDS restrictions

**COPPA (Children's Online Privacy Protection Act)**
- Parental consent for <13
- Data minimization
- Deletion rights

---

## 8. Compliance Mapping Framework

### Threat → Control → Requirement

**Example: Data Breach**
```yaml
Threat: Unauthorized data access
  ↓
Controls:
  - Encryption (AES-256)
  - Access control (MFA)
  - Monitoring (SIEM)
  ↓
Satisfies:
  - GDPR Article 32 (Security)
  - HIPAA Security Rule (Technical Safeguards)
  - PCI-DSS Requirement 3 & 8
  - SOX (Internal Controls)
```

### Control Matrix

| Control | GDPR | CCPA | HIPAA | SOX | PCI |
|---------|------|------|-------|-----|-----|
| Encryption at Rest | Art 32 | ✓ | Tech Safeguards | ✓ | Req 3 |
| Encryption in Transit | Art 32 | ✓ | Tech Safeguards | ✓ | Req 4 |
| Access Control (RBAC) | Art 32 | ✓ | Tech Safeguards | ✓ | Req 7 |
| MFA | Art 32 | - | Tech Safeguards | ✓ | Req 8 |
| Audit Logging | Art 30 | ✓ | Tech Safeguards | Sec 404 | Req 10 |
| Data Retention Policy | Art 5 | ✓ | Admin Safeguards | Sec 802 | Req 3 |
| Breach Notification | Art 33 | ✓ | Breach Rule | - | Req 12 |
| Data Deletion | Art 17 | CCPA | - | - | Req 3 |

---

## 9. Architecture Compliance Capabilities

### Encryption & Cryptography

**At Rest:**
- Database: TDE (Transparent Data Encryption)
- Files: Filesystem encryption (LUKS, BitLocker)
- Backups: Encrypted before offsite storage
- Cloud: Server-side encryption (SSE-KMS)

**In Transit:**
- TLS 1.3 for all APIs and services
- VPN for admin access
- Certificate management automation

**In Use (Advanced):**
- Homomorphic encryption
- Secure enclaves (Intel SGX, AWS Nitro)

### Access Control & Authentication

**Authentication:**
```yaml
Primary: SSO (SAML 2.0, OAuth 2.0)
MFA: TOTP, Push, Biometric
Passwordless: FIDO2, WebAuthn
```

**Authorization:**
```yaml
Model: RBAC + ABAC
Enforcement: Policy engine (OPA, Ranger)
Granularity: Row/column level
```

### Audit Logging & Monitoring

**Log Categories:**
- Access logs (who, what, when, where)
- Change logs (before/after values)
- Authentication logs (success/failure)
- Administrative actions
- Audit log access (who viewed logs)

**Centralization:**
```
Sources → Log Aggregator (Fluentd/Logstash)
  ↓
SIEM (Splunk/Elastic) → Alerting (PagerDuty)
  ↓
Long-term Storage (S3 Glacier) → 7 years retention
```

### Data Lineage & Traceability

**Automated Lineage Capture:**
- ETL metadata extraction
- Query log analysis
- API call tracking
- Schema change tracking

**Lineage Uses:**
- Impact analysis ("what breaks if I change this?")
- Root cause analysis ("where did bad data come from?")
- Compliance reporting (data provenance)

### Data Retention & Deletion

**Retention Policies:**
```yaml
Operational: 7 years (SOX)
PII: Duration + legal hold (GDPR)
Logs: 1-7 years (varies by regulation)
Backups: Policy-based (30d-7y)
```

**Deletion Methods:**
```yaml
Soft Delete: Mark as deleted, retain for recovery
Hard Delete: Overwrite with zeros/random data
Crypto-Shred: Delete encryption keys
Physical: Degauss, shred drives (NIST 800-88)
```

### Anonymization & Masking

**Techniques:**
- Suppression (redact fields)
- Generalization (age 35 → age 30-40)
- Noise addition (differential privacy)
- Tokenization (replace with tokens)
- Format-preserving encryption

---

## 10. Compliance Gap Analysis

### Assessment Process

```
Identify Requirements → Map to Controls → Assess Current State
  ↓
Gap Analysis → Prioritize Gaps → Remediation Plan
  ↓
Implement Controls → Validate → Continuous Monitoring
```

### Gap Analysis Template

| Requirement | Current State | Target State | Gap | Priority | Owner | Timeline |
|-------------|---------------|--------------|-----|----------|-------|----------|
| GDPR Art 32 - Encryption | TLS 1.2 | TLS 1.3 | Minor | Medium | InfoSec | Q2 |
| HIPAA - MFA | Password only | MFA required | Major | High | IT | Q1 |
| PCI Req 10 - Logging | Manual review | SIEM automated | Major | High | Security | Q1 |

### Remediation Prioritization

**Risk-Based:**
1. **Critical** - Regulatory violation likely, high fines
2. **High** - Significant compliance gap, medium fines
3. **Medium** - Minor gaps, attestation risk
4. **Low** - Best practice, no immediate risk

---

## Summary

**Key Takeaways:**

1. **No Single Regulation** - Most organizations face multiple regulations
2. **Overlapping Requirements** - Many controls satisfy multiple regulations
3. **Architecture Matters** - Technical controls enable compliance
4. **Automation Critical** - Manual processes don't scale
5. **Continuous Compliance** - Not point-in-time, ongoing monitoring

**Recommended Architecture Stack for Compliance:**
- **Encryption:** AES-256 (rest), TLS 1.3 (transit)
- **Access:** SSO + MFA + RBAC
- **Logging:** Centralized SIEM, 7-year retention
- **Privacy:** Consent management, DSR automation
- **Lineage:** Automated metadata capture
- **Monitoring:** Real-time anomaly detection

**Compliance is a Journey:**
- Start with risk assessment
- Prioritize by regulation and risk
- Implement controls incrementally
- Automate wherever possible
- Continuous monitoring and improvement

---

**Status:** Complete ✅

**Related:** [README](README.md) | [Data Governance Guide](data-governance-guide.md) | [Data Handling Architectures](data-handling-architectures.md)
