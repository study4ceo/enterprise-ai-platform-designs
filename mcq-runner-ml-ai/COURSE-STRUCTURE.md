# LLM Function Calling Practice Platform - Course Structure

## Overview

A production-level training platform for mastering LLM function calling. 600 scenario-based practice questions across 6 comprehensive modules covering fundamentals through deployment patterns.

## Course Philosophy

**Function calling is what lets an LLM stop just talking and start doing** — retrieving live data, triggering real actions, and orchestrating multi-step tasks through connected tools.

This course goes beyond basic tutorials to build **working, production-level understanding** of what it takes to design, orchestrate, secure, and ship reliable function-calling systems.

---

## 6 Course Modules (100 Questions Each)

### Module 1: Function Calling Fundamentals & Schema Design
**100 Questions | Beginner | 2-3 Hours**

Master the foundation of function calling through JSON schema design and parameter handling.

**Topics Covered:**
- Understanding JSON schema structure
- Parameter types: string, number, boolean, array, object
- Naming conventions and best practices
- Required vs optional fields
- Default values and validation rules
- Schema documentation practices
- Enum constraints and valid values
- Pattern matching and format validation

**Learning Outcomes:**
- Read and interpret JSON schemas correctly
- Extract parameters from natural language queries
- Understand type systems and constraints
- Know when to use defaults vs explicit values
- Validate parameter formats and boundaries

**Sample Questions:**
- Required vs optional field identification
- Default value handling
- Enum constraint mapping
- Type conversion (text → numbers, enable → boolean)
- Pattern validation (regex constraints)

---

### Module 2: Tool Selection & Multi-Tool Orchestration
**100 Questions | Intermediate | 3-4 Hours**

Learn to choose the right tools and orchestrate multiple functions to accomplish complex goals.

**Topics Covered:**
- Tool selection strategy
- Function disambiguation techniques
- Routing architecture patterns
- Multi-tool orchestration
- Combining results across tools
- Tool dependencies and sequencing
- Parallel vs sequential execution
- Result aggregation patterns

**Learning Outcomes:**
- Choose between similar functions correctly
- Identify when multiple tools are needed
- Understand dependency chains
- Combine results from multiple sources
- Optimize execution order (parallel/sequential)

**Sample Questions:**
- Disambiguating get_order vs get_order_history
- Multi-step workflows requiring 2-5 tools
- Determining execution dependencies
- Combining weather data from multiple cities
- Choosing specific over generic functions

---

### Module 3: Structured Output & Parameter Validation
**100 Questions | Intermediate | 3-4 Hours**

Master output validation, type checking, and handling malformed responses.

**Topics Covered:**
- Output structure validation
- Type checking and coercion
- Handling malformed outputs
- Constrained generation techniques
- Output parsing strategies
- Graceful degradation patterns
- Array validation (minItems, maxItems, patterns)
- Nested object validation

**Learning Outcomes:**
- Validate types before function execution
- Handle type coercion correctly
- Recognize and fix malformed parameters
- Apply array and object constraints
- Implement fallback strategies

**Sample Questions:**
- Converting 'fifty' (text) → 50 (integer)
- Array item validation with patterns
- Handling null vs undefined vs empty string
- Nested object structure validation
- Min/max constraint enforcement

---

### Module 4: Agentic Workflows & Tool Chaining
**100 Questions | Advanced | 4-5 Hours**

Build multi-step workflows with state management, self-correction, and failure handling.

**Topics Covered:**
- State management patterns
- Task decomposition strategies
- Tool chaining architectures
- Self-correction mechanisms
- Multi-step failure handling
- Workflow orchestration patterns
- Dependency graphs
- Rollback and compensation logic

**Learning Outcomes:**
- Decompose complex goals into steps
- Manage state across function calls
- Implement self-correction on failures
- Handle partial completion scenarios
- Design resilient workflows

**Sample Questions:**
- Booking flow: search → select → book → confirm
- Self-correction when API returns "try nearby dates"
- Task decomposition: plan team offsite (venue, invites, catering)
- State passing: {{step1.payment_method_id}} to step 2
- Recovery strategies for different failure types

---

### Module 5: Error Handling, Reliability & Security
**100 Questions | Advanced | 4-5 Hours**

Production security patterns including prompt injection defense, access control, and input sanitization.

**Topics Covered:**
- Retry strategies and exponential backoff
- Timeout handling and circuit breakers
- Prompt injection attack patterns
- Input sanitization techniques
- Access control for tool execution
- Audit logging and monitoring
- SQL injection prevention
- Defense in depth architecture

**Learning Outcomes:**
- Recognize and defend against prompt injection
- Implement proper access control
- Handle input sanitization correctly
- Design retry logic with backoff
- Understand security layers

**Sample Questions:**
- Defending against "IGNORE PREVIOUS INSTRUCTIONS" attacks
- SQL injection: when to sanitize, where to sanitize
- Access control: role-based vs resource-based
- Handling "Robert'; DROP TABLE users;--" input
- Circuit breaker patterns for failing endpoints

---

### Module 6: Production Patterns
**100 Questions | Expert | 5-6 Hours**

Testing, observability, API design, deployment, and cost management at scale.

**Topics Covered:**
- Testing strategies for function calling
- Golden dataset evaluation
- Observability and monitoring
- API design best practices
- Deployment patterns
- Cost optimization techniques
- Scaling considerations
- Token usage optimization

**Learning Outcomes:**
- Design comprehensive test suites
- Implement observability dashboards
- Optimize token costs (caching, dynamic selection)
- Debug production failures efficiently
- Scale to millions of queries

**Sample Questions:**
- Golden dataset vs E2E testing approaches
- Per-function success rate monitoring
- Token cost optimization (90% reduction strategies)
- Debugging "sometimes doesn't work" issues
- Prompt caching + dynamic tool selection

---

## Question Format

Each question includes:

- **Query:** Natural language user request
- **Tools:** Available functions with JSON schemas
- **Correct Answer:** Expected function call(s) with parameters
- **Explanation:** Detailed reasoning for the answer
- **Learning Points:** Key takeaways
- **Hints:** Progressive guidance
- **Tags:** Category labels for filtering

### Question Types:

1. **Single Function Selection** - Choose and call one function
2. **Multi-Step Workflows** - Array of function calls
3. **No Function Needed** - Recognize conversational queries
4. **Multiple Choice** - Conceptual questions with options
5. **Debugging** - Fix incorrect function calls

---

## Difficulty Progression

- **Beginner (Modules 1):** Basic schema reading, simple function calls
- **Intermediate (Modules 2-3):** Multi-tool, validation, complex parameters
- **Advanced (Modules 4-5):** Agentic workflows, security, error handling
- **Expert (Module 6):** Production patterns, optimization, scaling

---

## Learning Path

### Recommended Sequence:

1. **Start with Tutorial** (`/tutorial`) - Understand the interface and format
2. **Module 1** - Build foundation in schema design
3. **Module 2** - Learn tool selection and orchestration
4. **Module 3** - Master parameter validation
5. **Module 4** - Build complex agentic workflows
6. **Module 5** - Implement security best practices
7. **Module 6** - Optimize for production deployment

### Unlocking Modules:

- Modules 1-3: Unlocked by default
- Modules 4-6: Unlock after achieving 70%+ on previous module

---

## Practice Modes

### Practice Mode
- Unlimited attempts
- Hints available
- Detailed explanations
- No time pressure
- See correct answers immediately

### Test Mode
- Timed challenges (5-8 minutes per question)
- No hints
- Automatic scoring
- Simulates real assessment conditions
- Results shown at end

---

## Key Concepts by Module

| Module | Core Concepts | Production Skills |
|--------|---------------|-------------------|
| 1 | Schema design, types, constraints | API design, documentation |
| 2 | Tool selection, orchestration | System architecture, routing |
| 3 | Validation, type coercion | Error handling, robustness |
| 4 | State management, workflows | Reliability, resilience |
| 5 | Security, access control | Production security, defense |
| 6 | Testing, observability, cost | Scalability, optimization |

---

## Assessment Criteria

Questions test:
- ✅ **Correctness:** Right function, right parameters
- ✅ **Completeness:** All required steps included
- ✅ **Type Accuracy:** Proper type conversion
- ✅ **Security Awareness:** Safe handling of inputs
- ✅ **Efficiency:** Optimal execution strategy

---

## Getting Started

```bash
cd frontend-node
npm install
npm run dev
```

Open http://localhost:3000

1. Start with the **Tutorial** to understand the format
2. Browse **Modules** to see the full curriculum
3. Begin **Practice Mode** for hands-on learning
4. Try **Test Mode** when you're confident

---

## Technology Stack

- **Frontend:** React + Next.js
- **Editor:** Monaco Editor (VS Code editor component)
- **Styling:** Tailwind CSS
- **Notifications:** react-hot-toast
- **Icons:** lucide-react

---

## Course Outcomes

After completing all 600 questions, you will:

✅ Design clean, maintainable function schemas  
✅ Orchestrate complex multi-step workflows  
✅ Validate and sanitize inputs properly  
✅ Build resilient agentic systems  
✅ Implement production security patterns  
✅ Optimize costs and scale to millions of queries  
✅ Debug production issues efficiently  
✅ Deploy reliable function-calling systems  

---

## Next Steps

This platform provides the **practice and assessment**. For building real systems:

1. Choose your LLM provider (OpenAI, Anthropic, etc.)
2. Design your function toolkit
3. Implement execution layer with proper validation
4. Add observability and monitoring
5. Deploy with security best practices
6. Iterate based on production metrics

**Remember:** Function calling is a skill that improves with practice. Work through scenarios systematically, understand your mistakes, and build intuition for production patterns.

Good luck! 🚀
