# Getting Started with LLM Function Calling Practice Platform

## 🚀 Start Using in 3 Minutes

### Step 1: Install & Run
```bash
cd frontend-node
npm install
npm run dev
```

Open: http://localhost:3000

### Step 2: Take the Tutorial
- Click "Start with the Tutorial" on homepage
- Learn the interface and format
- See examples of correct answers
- Understand common mistakes

### Step 3: Start Practicing
- Go to Practice Mode
- Pick any scenario
- Try to solve it
- Use hints if needed
- Read explanations

**That's it! You're ready to master function calling.** 🎉

---

## 📚 Recommended Learning Path

### For Complete Beginners:
1. **Tutorial** (15 min) - `/tutorial`
2. **Module 1: Fundamentals** (2-3 hours)
   - Start with "Required vs Optional Fields"
   - Progress through enum, types, defaults
3. **Module 2: Tool Selection** (3-4 hours)
   - Learn tool disambiguation
   - Practice multi-tool workflows
4. **Continue through Modules 3-6** (20+ hours total)

### For Interview Prep:
1. **Tutorial** (quick review)
2. **Practice Mode** - Focus on:
   - Easy scenarios (build speed)
   - Medium scenarios (core patterns)
   - Hard scenarios (edge cases)
3. **Test Mode** - Simulate real conditions
   - Timed practice
   - No hints
   - Track your scores

### For Production Engineers:
1. **Skip to Advanced Modules:**
   - Module 4: Agentic Workflows
   - Module 5: Security
   - Module 6: Production Patterns
2. **Focus on:**
   - Error handling scenarios
   - Security best practices
   - Cost optimization
   - Observability patterns

---

## 🎯 Understanding the Interface

### Question Layout:

```
┌─────────────────────────────────────────┐
│  QUERY (What user wants)                │
├─────────────────────────────────────────┤
│  TOOLS (Available functions)            │
│  ▸ function_1 (click to expand)         │
│  ▸ function_2                            │
│  ▾ function_3 (expanded)                 │
│     {                                    │
│       "parameters": {...}                │
│     }                                    │
├─────────────────────────────────────────┤
│  YOUR ANSWER (JSON editor)              │
│  {                                       │
│    "selected_function": "...",           │
│    "arguments": {...}                    │
│  }                                       │
├─────────────────────────────────────────┤
│  [Submit] [Show Hint] [Reset]           │
└─────────────────────────────────────────┘
```

---

## ✅ How to Answer Questions

### Single Function Call:
```json
{
  "selected_function": "function_name",
  "arguments": {
    "param1": "value1",
    "param2": 123
  }
}
```

### Multiple Functions (Array):
```json
[
  {
    "selected_function": "first_function",
    "arguments": {...}
  },
  {
    "selected_function": "second_function",
    "arguments": {...}
  }
]
```

### No Function Needed:
```
N/A
```
(Just type the letters: N/A)

---

## 🎓 Core Concepts to Master

### 1. Reading JSON Schemas
```json
{
  "name": {
    "type": "string",           // Must be text
    "description": "User name"
  },
  "age": {
    "type": "integer",          // Must be whole number
    "minimum": 0,               // Can't be negative
    "maximum": 150
  },
  "email": {
    "type": ["string", "null"]  // Can be text OR null
  },
  "tags": {
    "type": "array",            // Must be list
    "items": {
      "type": "string"          // Each item is text
    }
  }
}
```

**Required Array:** Shows which fields MUST be provided
```json
{
  "required": ["name", "email"]  // age is optional
}
```

### 2. Type Conversions

User says → You write:
- "fifty" → `50` (integer, not string)
- "enable it" → `true` (boolean, not "enable")
- "tags: urgent, bug" → `["urgent", "bug"]` (array)
- "no email" → `null` (if schema allows null)
- "tomorrow at 2pm" → `"2024-03-16T14:00:00Z"` (ISO 8601)

### 3. Tool Selection Rules

1. **Most Specific Wins:**
   - get_order (single) vs get_order_history (multiple)
   - → If user wants history, use get_order_history

2. **Follow User Intent:**
   - User says "search" → use search function
   - User says "get my info" → use get function

3. **Multiple Actions:**
   - "Get profile AND disable notifications" → 2 functions
   - Return array: [{...}, {...}]

4. **No Function Needed:**
   - "Thanks!" → N/A
   - "That's helpful" → N/A
   - Just conversation, not a request

---

## 💡 Common Mistakes & How to Avoid

### ❌ Mistake 1: Wrong Types
```json
{
  "selected_function": "set_limit",
  "arguments": {
    "max_connections": "50"  // WRONG: String instead of number
  }
}
```

✅ **Correct:**
```json
{
  "arguments": {
    "max_connections": 50    // RIGHT: Actual number
  }
}
```

### ❌ Mistake 2: Missing Required Fields
```json
{
  "selected_function": "send_email",
  "arguments": {
    "to": "john@example.com"
    // WRONG: Missing required "subject" and "body"
  }
}
```

✅ **Correct:**
```json
{
  "arguments": {
    "to": "john@example.com",
    "subject": "Hello",
    "body": "Message content"
  }
}
```

### ❌ Mistake 3: Extra Fields
```json
{
  "selected_function": "get_weather",
  "arguments": {
    "location": "Boston"
  },
  "explanation": "This gets weather"  // WRONG: Extra field
}
```

✅ **Correct:**
```json
{
  "selected_function": "get_weather",
  "arguments": {
    "location": "Boston"
  }
}
```

### ❌ Mistake 4: Wrong Array Format
```json
{
  "arguments": {
    "tags": "urgent, bug"  // WRONG: String instead of array
  }
}
```

✅ **Correct:**
```json
{
  "arguments": {
    "tags": ["urgent", "bug"]  // RIGHT: Actual array
  }
}
```

---

## 🎯 Quick Reference Cheat Sheet

### JSON Types:
- `"string"` → `"text value"`
- `"integer"` → `42`
- `"number"` → `3.14`
- `"boolean"` → `true` or `false`
- `"array"` → `[item1, item2]`
- `"object"` → `{ key: value }`
- `"null"` → `null`

### Common Conversions:
| User Says | You Write |
|-----------|-----------|
| "yes" / "enable" | `true` |
| "no" / "disable" | `false` |
| "one hundred" | `100` |
| "items: a, b, c" | `["a", "b", "c"]` |
| "no value" | `null` (if allowed) |
| omitted | don't include (undefined) |

### When to Use N/A:
- Greetings ("Hi!", "Thank you")
- Statements ("I love this")
- Questions about capabilities ("Can you do X?")
- No action requested

---

## 📈 Tracking Your Progress

### In Practice Mode:
- ✅ Green = Correct answer
- ❌ Red = Incorrect, see what went wrong
- 💡 Yellow = Used hints

### Module Completion:
- Each module has 100 questions
- Unlock next module at 70% completion
- Track: questions attempted, success rate, time spent

### Skills to Monitor:
1. **Function Selection** - Choosing the right tool
2. **Parameter Extraction** - Getting values from query
3. **Type Accuracy** - Correct data types
4. **Schema Understanding** - Reading requirements
5. **Multi-tool Orchestration** - Complex workflows

---

## 🚀 Next Steps After Setup

### Today:
- [ ] Complete tutorial
- [ ] Solve 5 easy scenarios
- [ ] Read explanations carefully

### This Week:
- [ ] Complete Module 1 (Fundamentals)
- [ ] Start Module 2 (Tool Selection)
- [ ] Practice 30-60 minutes daily

### This Month:
- [ ] Complete Modules 1-3
- [ ] Start Test Mode practice
- [ ] Focus on weak areas

---

## 💬 Getting Help

### Resources:
1. **Tutorial Page** - Basic how-to
2. **COURSE-STRUCTURE.md** - Detailed curriculum
3. **Scenario Hints** - Progressive guidance
4. **Explanations** - Why answers are correct/wrong

### Common Questions:

**Q: How many scenarios should I do per day?**  
A: Start with 5-10. Quality > quantity. Understand each one fully.

**Q: Should I use hints?**  
A: Try without first. If stuck after 5 minutes, use progressive hints.

**Q: What if I keep getting a type of question wrong?**  
A: Review that module's section in COURSE-STRUCTURE.md, practice more similar scenarios.

**Q: How do I know I'm ready for Test Mode?**  
A: When you get 80%+ correct in Practice Mode without hints.

---

## 🎉 You're Ready!

Open http://localhost:3000 and start with the Tutorial.

**Remember:** Function calling is a skill. You'll improve with practice. Focus on understanding WHY answers are correct, not just getting them right.

**Good luck!** 🚀
