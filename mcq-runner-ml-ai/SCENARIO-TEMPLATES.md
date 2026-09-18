# Scenario Creation Templates

This guide helps create the remaining ~580 scenarios to reach 100 per module.

---

## Module 1: Fundamentals (Need 97 more)

### Template Categories:

#### 1. Basic Type Conversion (15 scenarios)
```json
{
  "query": "Set [parameter] to [text_value]",
  "focus": "Convert text to correct type",
  "examples": [
    "Set max users to one hundred → 100 (integer)",
    "Set auto-save to yes → true (boolean)",
    "Set timeout to 30 seconds → 30 (number)",
    "Set mode to active → 'active' (string)",
    "Set priority to top → 'high' (enum mapping)"
  ]
}
```

#### 2. Required vs Optional (15 scenarios)
```json
{
  "focus": "Identify what must be provided vs what can be omitted",
  "variations": [
    "Only required fields provided",
    "Required + some optional",
    "Distinguish similar required/optional fields",
    "Multiple optional with defaults"
  ]
}
```

#### 3. Enum Mapping (15 scenarios)
```json
{
  "focus": "Map natural language to enum values",
  "examples": [
    "verbose → trace",
    "quiet → error",
    "low priority → 'low'",
    "biggest size → 'xl'",
    "fastest speed → 'max'"
  ]
}
```

#### 4. Array Basics (15 scenarios)
```json
{
  "focus": "Construct simple arrays",
  "examples": [
    "Single item array",
    "Multiple items",
    "Empty array vs omitted",
    "Extracting items from prose"
  ]
}
```

#### 5. Object Basics (15 scenarios)
```json
{
  "focus": "Simple nested objects",
  "examples": [
    "address: { street, city, zip }",
    "config: { enabled, value }",
    "metadata: { key, value pairs }"
  ]
}
```

#### 6. Patterns & Formats (12 scenarios)
```json
{
  "focus": "String format validation",
  "examples": [
    "Email format",
    "Phone format",
    "Date format (ISO 8601)",
    "URL format",
    "UUID format"
  ]
}
```

#### 7. Default Values (10 scenarios)
```json
{
  "focus": "When to use defaults vs explicit values",
  "examples": [
    "All defaults",
    "Some defaults",
    "Override defaults"
  ]
}
```

---

## Module 2: Tool Selection (Need 95 more)

### Template Categories:

#### 1. Similar Functions (20 scenarios)
```json
{
  "focus": "Choose between 3-5 similar functions",
  "patterns": [
    "get_item vs get_items vs search_items",
    "create vs create_bulk vs clone",
    "update vs patch vs replace",
    "delete vs archive vs trash"
  ]
}
```

#### 2. Sequential Multi-Tool (20 scenarios)
```json
{
  "focus": "2-4 step workflows with dependencies",
  "patterns": [
    "search → select → execute",
    "get → process → update",
    "validate → transform → save"
  ]
}
```

#### 3. Parallel Multi-Tool (15 scenarios)
```json
{
  "focus": "Independent operations that can run together",
  "examples": [
    "Get weather for 3 cities",
    "Check status of multiple services",
    "Fetch data from multiple sources"
  ]
}
```

#### 4. Disambiguation (20 scenarios)
```json
{
  "focus": "Ambiguous queries requiring context understanding",
  "examples": [
    "'delete old files' → define 'old'",
    "'notify team' → which team?",
    "'update settings' → which settings?"
  ]
}
```

#### 5. Result Aggregation (10 scenarios)
```json
{
  "focus": "Combine outputs from multiple tools",
  "patterns": [
    "Gather → Compare",
    "Fetch multiple → Merge",
    "Query many → Summarize"
  ]
}
```

#### 6. Tool Chaining (10 scenarios)
```json
{
  "focus": "Output of tool N feeds into tool N+1",
  "examples": [
    "get_user_id → get_user_data → get_user_orders",
    "search_product → get_price → calculate_discount"
  ]
}
```

---

## Module 3: Validation (Need 95 more)

### Template Categories:

#### 1. Type Coercion (20 scenarios)
```json
{
  "focus": "Converting between types correctly",
  "examples": [
    "Numbers: 'fifty' → 50, '3.14' → 3.14",
    "Booleans: 'yes'/'no', 'on'/'off', 'enabled'/'disabled'",
    "Arrays: single item → array",
    "Objects: flat params → nested object"
  ]
}
```

#### 2. Array Validation (20 scenarios)
```json
{
  "focus": "Array constraints and item validation",
  "examples": [
    "minItems/maxItems enforcement",
    "Item pattern matching",
    "Unique items requirement",
    "Array of objects validation"
  ]
}
```

#### 3. Nested Objects (20 scenarios)
```json
{
  "focus": "Multi-level object structures",
  "examples": [
    "2-level nesting",
    "3-level nesting",
    "Arrays of objects",
    "Objects with array properties"
  ]
}
```

#### 4. Format Validation (15 scenarios)
```json
{
  "focus": "String format constraints",
  "examples": [
    "Email validation",
    "Date/time parsing",
    "Phone number formats",
    "URL validation",
    "Custom regex patterns"
  ]
}
```

#### 5. Boundary Validation (10 scenarios)
```json
{
  "focus": "Min/max constraints",
  "examples": [
    "Number ranges (min: 1, max: 100)",
    "String length (minLength, maxLength)",
    "Array size limits",
    "Date ranges"
  ]
}
```

#### 6. Null vs Undefined vs Empty (10 scenarios)
```json
{
  "focus": "Handling different empty states",
  "examples": [
    "null (explicit no value)",
    "undefined (omitted)",
    "empty string ''",
    "empty array []",
    "empty object {}"
  ]
}
```

---

## Module 4: Agentic Workflows (Need 97 more)

### Template Categories:

#### 1. State Management (20 scenarios)
```json
{
  "focus": "Passing data between steps",
  "patterns": [
    "Simple state passing (ID from step 1 to step 2)",
    "Multiple state variables",
    "State transformation",
    "Conditional state usage"
  ]
}
```

#### 2. Task Decomposition (20 scenarios)
```json
{
  "focus": "Breaking complex goals into steps",
  "complexity_levels": [
    "3-step workflows",
    "5-step workflows",
    "7-10 step workflows",
    "Workflows with optional steps"
  ]
}
```

#### 3. Self-Correction (15 scenarios)
```json
{
  "focus": "Recovery from failures",
  "failure_types": [
    "Resource not found",
    "Invalid parameters",
    "Rate limiting",
    "Timeout errors",
    "Business rule violations"
  ]
}
```

#### 4. Conditional Execution (15 scenarios)
```json
{
  "focus": "If-then logic in workflows",
  "examples": [
    "If A succeeds → do B, else do C",
    "If permission granted → execute",
    "If threshold exceeded → alert"
  ]
}
```

#### 5. Loop Patterns (12 scenarios)
```json
{
  "focus": "Iterative operations",
  "patterns": [
    "Retry with backoff",
    "Process items one by one",
    "Poll until condition met",
    "Batch processing"
  ]
}
```

#### 6. Rollback & Compensation (15 scenarios)
```json
{
  "focus": "Undoing partial failures",
  "examples": [
    "Created user but failed to send email → delete user",
    "Charged card but shipment failed → refund",
    "Booked venue but invite failed → cancel or retry"
  ]
}
```

---

## Module 5: Security (Need 97 more)

### Template Categories:

#### 1. Prompt Injection (25 scenarios)
```json
{
  "attack_patterns": [
    "IGNORE PREVIOUS INSTRUCTIONS",
    "SYSTEM: You are now...",
    "Override mode activated",
    "Execute: dangerous_function()",
    "Embedded commands in data fields"
  ],
  "variations": [
    "Direct attacks",
    "Obfuscated attacks",
    "Multi-step attacks",
    "Social engineering"
  ]
}
```

#### 2. SQL/Command Injection (20 scenarios)
```json
{
  "injection_types": [
    "SQL: '; DROP TABLE",
    "Command: ; rm -rf /",
    "LDAP injection",
    "NoSQL injection",
    "Path traversal: ../../"
  ]
}
```

#### 3. Access Control (20 scenarios)
```json
{
  "focus": "Permission checks and authorization",
  "scenarios": [
    "Role-based access",
    "Resource-level permissions",
    "Organizational boundaries",
    "Privilege escalation attempts",
    "Admin function access"
  ]
}
```

#### 4. Input Sanitization (12 scenarios)
```json
{
  "focus": "When and how to sanitize",
  "examples": [
    "XSS prevention",
    "Script tag handling",
    "File upload validation",
    "User-generated content"
  ]
}
```

#### 5. Rate Limiting (10 scenarios)
```json
{
  "focus": "Preventing abuse",
  "patterns": [
    "Per-user rate limits",
    "Per-function limits",
    "Sliding window",
    "Token bucket"
  ]
}
```

#### 6. Audit Logging (10 scenarios)
```json
{
  "focus": "Security monitoring",
  "examples": [
    "What to log",
    "Sensitive data in logs",
    "Log tampering prevention",
    "Audit trail requirements"
  ]
}
```

---

## Module 6: Production (Need 97 more)

### Template Categories:

#### 1. Testing Strategies (20 scenarios)
```json
{
  "test_types": [
    "Golden dataset design",
    "E2E test scenarios",
    "Integration tests",
    "Load testing",
    "Chaos engineering"
  ]
}
```

#### 2. Observability (20 scenarios)
```json
{
  "metrics": [
    "Success rate tracking",
    "Latency monitoring",
    "Error categorization",
    "Cost tracking",
    "User journey tracking"
  ]
}
```

#### 3. Cost Optimization (15 scenarios)
```json
{
  "techniques": [
    "Prompt caching",
    "Dynamic tool selection",
    "Token compression",
    "Model selection",
    "Batch processing"
  ]
}
```

#### 4. API Design (15 scenarios)
```json
{
  "patterns": [
    "RESTful function APIs",
    "Versioning strategies",
    "Error response formats",
    "Pagination",
    "Filtering and search"
  ]
}
```

#### 5. Deployment (12 scenarios)
```json
{
  "topics": [
    "Blue-green deployment",
    "Canary releases",
    "Feature flags",
    "A/B testing",
    "Rollback strategies"
  ]
}
```

#### 6. Scaling (15 scenarios)
```json
{
  "challenges": [
    "Horizontal scaling",
    "Caching strategies",
    "Database optimization",
    "Async processing",
    "Load balancing"
  ]
}
```

---

## Scenario Difficulty Guidelines

### Easy (Modules 1-2):
- Single concept focus
- 1-2 tools maximum
- Clear right/wrong answer
- Time: 3-4 minutes

### Medium (Modules 2-4):
- 2-3 concepts combined
- 2-4 tools
- Some ambiguity
- Time: 5-6 minutes

### Hard (Modules 4-6):
- Multiple concepts
- Complex workflows
- Requires analysis
- Time: 7-10 minutes

---

## Question Quality Checklist

- [ ] Clear query without ambiguity
- [ ] Realistic scenario
- [ ] One clear correct answer
- [ ] Detailed explanation included
- [ ] Learning points identified
- [ ] Wrong answer examples (with why they're wrong)
- [ ] Progressive hints
- [ ] Tags for categorization
- [ ] Time estimate appropriate
- [ ] Difficulty level accurate

---

## Batch Creation Strategy

**Week 1-2:** Module 1 completion (100 total)
**Week 3-4:** Module 2 completion (100 total)
**Week 5-6:** Module 3 completion (100 total)
**Week 7-8:** Module 4 completion (100 total)
**Week 9-10:** Module 5 completion (100 total)
**Week 11-12:** Module 6 completion (100 total)

Target: ~8-10 scenarios per day = 600 scenarios in 60-75 days

---

## Scenario Naming Convention

```
module-{N}-{category}/{topic}-{number}.json

Examples:
module-1-fundamentals/type-conversion-001.json
module-2-orchestration/multi-tool-003.json
module-5-security/prompt-injection-015.json
```

---

## Next Steps

1. Review existing 20 scenarios as examples
2. Start with Module 1 (easiest to create)
3. Create in batches of 10
4. Test each batch in the UI
5. Iterate based on difficulty and clarity
6. Move to next module once current reaches 100

The platform is ready - now it's time to fill it with world-class content! 🚀
