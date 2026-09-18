# Turing Function Calling - Quick Reference Cheat Sheet

## 🎯 Answer Format

### Single Function Call
```json
{
  "selected_function": "function_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Multiple Function Calls
```json
[
  {
    "selected_function": "function_1",
    "arguments": { ... }
  },
  {
    "selected_function": "function_2",
    "arguments": { ... }
  }
]
```

### No Function Needed
```
N/A
```

## 📋 Decision Tree

```
Read User Query
    ↓
Is user REQUESTING an action?
    ├─ YES → Look for matching function
    │         ↓
    │    Function exists?
    │    ├─ YES → Extract parameters → Build JSON
    │    └─ NO → Answer: N/A
    │
    └─ NO (just commenting/thanking) → Answer: N/A
```

## 🔍 Common Query Patterns

| User Says | They Want | Function Type |
|-----------|-----------|---------------|
| "What's the weather..." | Current weather | `get_weather` |
| "Weather forecast..." | Future weather | `get_forecast` |
| "Send email to..." | Send email | `send_email` |
| "Send quick message..." | Simple message | `send_quick_message` |
| "Get my profile..." | User info | `get_user_profile` |
| "Stop notifications..." | Disable alerts | `stop_notifications` |
| "Create task..." | New task | `create_task` |
| "Thanks!" / "Great!" | Nothing | `N/A` |

## 📦 Parameter Types

### String
```json
"param": "value"
```

### Integer/Number
```json
"count": 5
```

### Boolean
```json
"enabled": true
```

### Array
```json
"items": ["item1", "item2"]
```

### Object
```json
"config": {
  "key1": "value1",
  "key2": "value2"
}
```

### Enum (String with limited values)
```json
"unit": "celsius"  // Must be from: ["celsius", "fahrenheit"]
```

## ✅ Validation Checklist

Before submitting, check:

- [ ] Is JSON syntax valid?
- [ ] All required parameters included?
- [ ] Parameter types correct? (string vs number vs boolean)
- [ ] Enum values are from allowed list?
- [ ] Values extracted from user query (not made up)?
- [ ] No extra fields added?
- [ ] Function name spelled correctly?
- [ ] Using correct function (not a similar one)?

## ⚠️ Common Mistakes

### ❌ Extra Fields
```json
{
  "selected_function": "get_weather",
  "arguments": { "location": "Boston" },
  "reason": "User wants weather"  // ← REMOVE THIS
}
```

### ❌ Wrong Type
```json
{
  "selected_function": "create_task",
  "arguments": {
    "priority": "high"  // ← Should be integer, not string
  }
}
```

### ❌ Missing Required Param
```json
{
  "selected_function": "send_email",
  "arguments": {
    "to": "john@example.com"
    // Missing "subject" and "body"!
  }
}
```

### ❌ Made-Up Values
```json
// User said: "What's the weather?"
{
  "selected_function": "get_weather",
  "arguments": {
    "location": "New York"  // ← Where did "New York" come from?
  }
}
// Should be: N/A or ask for location
```

### ❌ Wrong Function
```json
// User: "What's the weather now?"
{
  "selected_function": "get_forecast"  // ← Wrong! This is for future
  // Should be: "get_weather"
}
```

## 🎯 Parameter Extraction Tips

### From Query → Parameter

```
Query: "What's the weather in Boston?"
        ↓
Extract: location = "Boston"

Query: "Send email to john@company.com about the meeting"
        ↓
Extract: to = "john@company.com"
         subject = "about the meeting" (or infer)
         body = "about the meeting"

Query: "Get 5 latest messages"
        ↓
Extract: limit = 5 (convert to integer!)

Query: "What's the temperature in Celsius in London?"
        ↓
Extract: location = "London"
         unit = "celsius"
```

## 🔢 JSON Schema Quick Reference

### Required vs Optional
```json
{
  "parameters": {
    "type": "object",
    "properties": {
      "required_param": { ... },
      "optional_param": { ... }
    },
    "required": ["required_param"]  // ← Only this is required!
  }
}
```

### Reading Schemas
```json
{
  "name": "send_email",
  "parameters": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",           // ← Must be string
        "description": "Email..."   // ← What it's for
      },
      "subject": {
        "type": "string"
      }
    },
    "required": ["to", "subject"]   // ← Both must be provided
  }
}
```

## 🚦 Quick Decision Guide

### When to use Single Function?
- User asks for ONE thing
- Example: "What's the weather?"

### When to use Multiple Functions?
- User asks for TWO+ things
- Example: "Get my profile AND stop notifications"

### When to use N/A?
- User is NOT requesting an action
- Just commenting, thanking, greeting
- No matching function available
- Example: "Thanks!" or "Hello!"

## 📝 Test Day Strategy

### Before Starting:
1. ✅ Read ALL instructions carefully
2. ✅ Take a deep breath
3. ✅ Have your cheat sheet ready

### For Each Question:
1. ✅ Read query carefully (what does user WANT?)
2. ✅ Scroll through ALL available tools
3. ✅ Expand relevant tool schemas
4. ✅ Identify the best match(es)
5. ✅ Extract parameters from query
6. ✅ Build JSON carefully
7. ✅ Validate before submitting

### Time Management:
- **Easy questions**: 2-3 minutes
- **Medium questions**: 4-5 minutes
- **Hard questions**: 6-8 minutes

### If Stuck:
1. Re-read the user query
2. What is the USER INTENT?
3. Which function best matches that intent?
4. What info did user provide?

## 🎓 Scoring Guide

| Component | Points | What's Checked |
|-----------|--------|----------------|
| Function Selection | 40 | Right function chosen? |
| Parameters | 40 | All required params with correct types? |
| JSON Syntax | 10 | Valid JSON format? |
| Following Rules | 10 | No extra fields? Proper structure? |

### Aim for:
- **90%+** on Easy
- **80%+** on Medium
- **70%+** on Hard

## 🔥 Pro Tips

1. **Always scroll to bottom of tool list** - Important tools might be last
2. **Click to expand schemas** - Don't guess from names
3. **Copy parameter names exactly** - Typos = 0 points
4. **Use double quotes** - JSON requires `"` not `'`
5. **Check "required" array** - Only include what's required
6. **Read descriptions** - They tell you when to use each function
7. **Multi-function = Array** - Use `[{...}, {...}]` format
8. **When in doubt, look at examples** - Pattern recognition helps

## 📊 Success Patterns

### Pattern 1: Direct Match
```
Query: "Get weather in Boston"
Tool: get_weather(location)
Answer: {"selected_function": "get_weather", "arguments": {"location": "Boston"}}
```

### Pattern 2: Parameter Inference
```
Query: "Email john@example.com that meeting moved to 3pm"
Tool: send_email(to, subject, body)
Answer: Extract all info from query
```

### Pattern 3: Multiple Actions
```
Query: "Get my profile and turn off alerts"
Tools: get_user_profile(), stop_alerts()
Answer: Array with both functions
```

### Pattern 4: No Action
```
Query: "This is awesome!"
Tools: [any]
Answer: N/A
```

## 🎯 Final Checklist

Before clicking Submit:

- [ ] JSON is valid (no syntax errors)
- [ ] Function name is correct
- [ ] All required parameters included
- [ ] Parameter types match schema
- [ ] Values from query (not invented)
- [ ] No extra fields added
- [ ] Multi-function = array format
- [ ] Single function = object format
- [ ] N/A for non-requests

## 💪 You Got This!

Remember:
- **Practice makes perfect**
- **Read carefully**
- **Trust your preparation**
- **Stay calm**
- **Double-check before submitting**

**Good luck! 🚀**

---

Print this sheet and keep it handy while practicing!
