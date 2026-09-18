# Quick Start Guide - Turing Function Calling Practice

Get up and running in 5 minutes!

## 🚀 Installation

### Option 1: Quick Start (Frontend Only)

```bash
cd frontend-node
npm install
npm run dev
```

Access at: `http://localhost:3000`

### Option 2: Full Stack (with Backend)

```bash
# Terminal 1: Frontend
cd frontend-node
npm install
npm run dev

# Terminal 2: Backend (Go)
cd backend-go
go run main.go
```

## 📝 Your First Practice Session

1. **Open the app** at `http://localhost:3000`

2. **Click "Practice Mode"** (green button)

3. **You'll see a test interface with:**
   - User Query at the top
   - List of available tools (click to expand)
   - Answer input area on the right

4. **How to answer:**

   **Example 1: Single Function**
   ```json
   {
     "selected_function": "get_weather",
     "arguments": {
       "location": "Boston"
     }
   }
   ```

   **Example 2: No Function Needed**
   ```
   N/A
   ```

   **Example 3: Multiple Functions**
   ```json
   [
     {
       "selected_function": "get_user_profile",
       "arguments": {}
     },
     {
       "selected_function": "stop_user_watch",
       "arguments": {}
     }
   ]
   ```

5. **Click Submit** and get instant feedback!

## 🎯 Practice Strategy

### Week 1: Foundations
- **Day 1-2**: Do all "Easy" scenarios
- **Day 3-4**: Practice "Medium" scenarios
- **Day 5**: Review mistakes, redo failed ones

### Week 2: Mastery
- **Day 1-3**: Tackle "Hard" scenarios
- **Day 4**: Take timed tests
- **Day 5**: Final review

### Test Day
- Do 5-10 warm-up questions
- Take a timed practice test
- Review your most common mistakes
- **You're ready!**

## 🎓 Key Learning Points

### 1. Read ALL Tools Before Answering
❌ **Don't**: Pick the first tool that seems right
✅ **Do**: Scroll through entire list, some tools are at the bottom

### 2. Extract Parameters from Query
```
Query: "What's the weather in Boston?"
         ↓
{
  "selected_function": "get_weather",
  "arguments": {
    "location": "Boston"  ← extracted from query
  }
}
```

### 3. Know When to Say N/A
```
Query: "Thanks for your help!"
       ↓
Answer: N/A  ← no action requested
```

### 4. Multi-Function Calls
```
Query: "Get my profile and stop notifications"
       ↓ TWO requests ↓
[
  { "selected_function": "get_user_profile", ... },
  { "selected_function": "stop_notifications", ... }
]
```

### 5. Required vs Optional Parameters
```json
{
  "name": "send_email",
  "parameters": {
    "properties": {
      "to": { ... },      // required if in "required" array
      "cc": { ... }       // optional if NOT in "required" array
    },
    "required": ["to"]    ← Only "to" is required!
  }
}
```

## ⚠️ Common Mistakes

### Mistake 1: Extra Fields
❌ **Wrong:**
```json
{
  "selected_function": "get_weather",
  "arguments": { "location": "Boston" },
  "explanation": "This gets the weather"  ← Remove this!
}
```

✅ **Correct:**
```json
{
  "selected_function": "get_weather",
  "arguments": { "location": "Boston" }
}
```

### Mistake 2: Missing Required Parameters
❌ **Wrong:**
```json
{
  "selected_function": "send_email",
  "arguments": {
    "to": "john@example.com"
    // Missing "subject" and "body" if required!
  }
}
```

✅ **Correct:** Check the schema's "required" array!

### Mistake 3: Wrong Tool Selection
❌ **Wrong:**
```
Query: "What's the weather?"
Tool: get_forecast ← This is for future weather
```

✅ **Correct:**
```
Query: "What's the weather?"
Tool: get_weather ← This is for current weather
```

### Mistake 4: Calling Function When Not Needed
❌ **Wrong:**
```
Query: "I love this app!"
Answer: { "selected_function": "send_feedback", ... }
```

✅ **Correct:**
```
Query: "I love this app!"
Answer: N/A  ← Just a comment, no action needed
```

## 📊 Scoring Breakdown

Your answer is graded on:

1. **Function Selection** (40 points)
   - Did you pick the right function?

2. **Parameter Correctness** (40 points)
   - All required params included?
   - Correct types (string, integer, array)?
   - Values extracted correctly from query?

3. **JSON Validity** (10 points)
   - Valid JSON syntax?
   - Proper structure?

4. **Following Instructions** (10 points)
   - No extra fields when not asked?
   - "N/A" when appropriate?

**Total: 100 points per question**

## 🎮 Interface Navigation

### Keyboard Shortcuts (coming soon)
- `Ctrl/Cmd + Enter` - Submit answer
- `Ctrl/Cmd + F` - Format JSON
- `Esc` - Clear answer

### Mouse Interactions
- **Click tool names** to expand/collapse schemas
- **Scroll** through long tool lists
- **Drag** to resize editor panels

## 💡 Pro Tips

1. **Always expand tools** - Don't assume from the name
2. **Copy-paste carefully** - Watch for typos in parameter names
3. **Use the format button** - Makes JSON easier to read
4. **Read error messages** - They tell you exactly what's wrong
5. **Practice daily** - Even 15 minutes helps
6. **Review explanations** - Understand the WHY, not just the answer

## 🆘 Troubleshooting

### "Invalid JSON" Error
- Check for missing commas
- Ensure quotes around strings
- Use double quotes, not single quotes
- Check brackets match: `{}`  `[]`

### "Missing Required Parameter"
- Expand the tool schema
- Look at the "required" array
- Add all listed parameters

### "Wrong Function Selected"
- Re-read the user query
- What is the user ACTUALLY asking for?
- Scroll through ALL tools before deciding

## 📚 Additional Resources

- **Tutorial Mode**: Step-by-step guide (coming soon)
- **Video Walkthroughs**: Watch examples (coming soon)
- **Cheat Sheet**: Quick reference guide (in `/docs`)

## 🎯 Ready to Start?

```bash
cd frontend-node
npm run dev
```

Open `http://localhost:3000` and click **"Practice Mode"**

**Good luck! You've got this! 💪🚀**

---

Questions? Issues? Check the main README.md or open an issue.
