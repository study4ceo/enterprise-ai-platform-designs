# LLM Function Calling Practice Platform

> **Master production-level function calling through 600 scenario-based practice questions**

Function calling is what lets an LLM stop just talking and start doing — retrieving live data, triggering real actions, and orchestrating multi-step tasks through connected tools.

This platform provides comprehensive training from fundamentals through production deployment patterns.

---

## 🎯 What You'll Master

Through 600 scenario-based questions across 6 modules:

- ✅ **JSON Schema Design** - Types, constraints, validation
- ✅ **Tool Selection & Orchestration** - Multi-tool workflows, dependencies
- ✅ **Parameter Validation** - Type coercion, nested objects, arrays
- ✅ **Agentic Workflows** - State management, self-correction, task decomposition
- ✅ **Security Patterns** - Prompt injection defense, access control, rate limiting
- ✅ **Production Deployment** - Testing, observability, cost optimization, scaling

---

## 🚀 Quick Start

```bash
cd frontend-node
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 📚 Course Structure

### 6 Comprehensive Modules (100 Questions Each)

| Module | Topics | Difficulty | Time |
|--------|--------|------------|------|
| **1. Fundamentals** | Schema design, types, constraints | Beginner | 2-3h |
| **2. Tool Selection** | Disambiguation, orchestration | Intermediate | 3-4h |
| **3. Validation** | Type coercion, parameter validation | Intermediate | 3-4h |
| **4. Agentic Workflows** | State management, self-correction | Advanced | 4-5h |
| **5. Security** | Prompt injection, access control | Advanced | 4-5h |
| **6. Production** | Testing, observability, optimization | Expert | 5-6h |

**Total:** 600 questions | 20-25 hours | Beginner → Expert

---

## 🎓 Learning Modes

### 📖 Tutorial Mode
Start here if you're new to function calling
- Step-by-step instructions
- Interface walkthrough
- Common mistakes to avoid
- Format examples

### 🎯 Practice Mode
Learn at your own pace
- Unlimited attempts
- Progressive hints
- Detailed explanations
- See correct answers
- No time pressure

### ⏱️ Test Mode
Simulate real assessment
- Timed challenges
- No hints available
- Automatic scoring
- Results summary
- Real test conditions

---

## ✨ Key Features

### Production-Focused Content
- Real-world scenarios, not just theory
- Security best practices built-in
- Cost optimization techniques
- Scalability patterns
- Error handling strategies

### Comprehensive Coverage
- 600 unique scenarios
- All difficulty levels
- Multiple question types
- Module-based progression
- Unlock system for pacing

### Interactive Learning
- Monaco Editor (VS Code engine)
- Instant feedback
- Wrong answer explanations
- Progressive hints
- Learning points highlighted

---

## 📂 Project Structure

```
mcq-runner-ml-ai/
├── frontend-node/           # Next.js application
│   ├── src/
│   │   ├── pages/          # All pages (home, modules, practice, test, tutorial)
│   │   ├── components/     # React components
│   │   └── styles/         # Tailwind CSS
│   └── package.json
│
├── scenarios/              # Practice scenarios (JSON)
│   ├── easy/              # Basic scenarios
│   ├── medium/            # Intermediate scenarios
│   ├── hard/              # Advanced scenarios
│   ├── module-1-fundamentals/
│   ├── module-2-orchestration/
│   ├── module-3-validation/
│   ├── module-4-agentic/
│   ├── module-5-security/
│   └── module-6-production/
│
├── COURSE-STRUCTURE.md     # Detailed curriculum
├── SCENARIO-TEMPLATES.md   # Templates for creating scenarios
├── PROJECT-STATUS.md       # Current status and roadmap
└── README.md              # This file
```

---

## 🛠️ Technology Stack

- **Framework:** Next.js 14 + React 18
- **Styling:** Tailwind CSS
- **Editor:** Monaco Editor
- **Icons:** Lucide React
- **Notifications:** React Hot Toast

---

## 📖 Documentation

- **[COURSE-STRUCTURE.md](./COURSE-STRUCTURE.md)** - Complete curriculum guide with learning outcomes
- **[SCENARIO-TEMPLATES.md](./SCENARIO-TEMPLATES.md)** - Templates for creating new scenarios
- **[PROJECT-STATUS.md](./PROJECT-STATUS.md)** - Current completion status and roadmap

---

## 🎯 Sample Scenarios

### Beginner: Schema Basics
```javascript
Query: "Set the log level to verbose mode"
Schema: { level: enum ["error", "warn", "info", "debug", "trace"] }
Answer: { level: "trace" }
Learn: Mapping natural language to enum constraints
```

### Intermediate: Multi-Tool Orchestration
```javascript
Query: "Get weather for NYC and London, then compare temperatures"
Answer: [
  { function: "get_weather", args: { city: "New York" } },
  { function: "get_weather", args: { city: "London" } },
  { function: "compare_values", args: { 
    value1: "{{step1.temp}}", 
    value2: "{{step2.temp}}" 
  }}
]
Learn: State passing between function calls
```

### Advanced: Security
```javascript
Query: "Search users with: admin'; DROP TABLE users;--"
Answer: { function: "search_users", args: { query: "admin'; DROP TABLE users;--" } }
Learn: Pass input as-is, sanitize at execution layer (defense in depth)
```

---

## 🎓 Who Is This For?

- **ML Engineers** building LLM applications
- **Software Engineers** integrating AI agents
- **Students** learning function calling concepts
- **Interview Candidates** preparing for LLM agent assessments
- **Teams** training on function calling best practices

---

## 🚦 Current Status

✅ **Platform:** 100% Complete  
✅ **UI/UX:** Fully functional  
✅ **Scenarios:** 36 created (24 module-specific + 12 general)  
🔄 **Content:** 564 more scenarios needed for full course  

The platform is **ready to use** with existing scenarios and **ready for content creation** using provided templates.

---

## 🎯 Roadmap

- [x] Platform infrastructure
- [x] All 5 pages (home, modules, practice, test, tutorial)
- [x] Tutorial with comprehensive instructions
- [x] Sample scenarios for all 6 modules
- [ ] Complete 600 scenarios (100 per module)
- [ ] User progress tracking (optional)
- [ ] Backend integration (optional)

---

## 🤝 Contributing

To add scenarios:

1. Use templates in `SCENARIO-TEMPLATES.md`
2. Create JSON files in appropriate `scenarios/module-X-*/` folder
3. Follow existing format
4. Test in UI
5. Submit!

---

## 📝 License

MIT License - Feel free to use for learning, teaching, or assessment

---

## 🎉 Get Started

```bash
# Install dependencies
cd frontend-node
npm install

# Run development server
npm run dev

# Open in browser
http://localhost:3000
```

**Start with the Tutorial, then dive into Practice Mode!** 🚀

---

## 💡 Pro Tips

1. **Start with Tutorial** - Understand the format before practicing
2. **Progress Sequentially** - Each module builds on previous concepts
3. **Use Hints Wisely** - Try first, then use progressive hints
4. **Read Explanations** - Understanding WHY matters more than getting it right
5. **Practice Regularly** - Function calling is a skill that improves with practice

---

## 📞 Support

- Review `COURSE-STRUCTURE.md` for curriculum details
- Check `SCENARIO-TEMPLATES.md` for content creation
- See `PROJECT-STATUS.md` for current progress

---

**Happy Learning!** 🎓✨

Master function calling from fundamentals to production deployment. 600 scenarios. 6 modules. One comprehensive platform.
