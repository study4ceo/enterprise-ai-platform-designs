# Complete Setup Instructions

## 📋 Prerequisites

Make sure you have:
- **Node.js** 18+ installed ([Download](https://nodejs.org/))
- **Git** installed (optional, for cloning)
- **Code editor** (VS Code recommended)
- **Terminal/Command Prompt** access

Check versions:
```bash
node --version  # Should be 18+
npm --version   # Should be 9+
```

## 🚀 Quick Setup (5 Minutes)

### Step 1: Navigate to Project
```bash
cd D:\code_ai\code\project-designs\mcq-runner-ml-ai
```

### Step 2: Install Dependencies
```bash
cd frontend-node
npm install
```

This will install:
- React & Next.js (UI framework)
- Monaco Editor (code editor)
- TailwindCSS (styling)
- Other dependencies

**Expected time**: 2-3 minutes

### Step 3: Start Development Server
```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Step 4: Open in Browser
Open: `http://localhost:3000`

You should see the landing page with "Practice Mode" and "Test Mode" buttons.

### Step 5: Start Practicing!
Click **"Practice Mode"** and you're ready to go!

## 🔧 Detailed Setup

### Option 1: Frontend Only (Recommended for Quick Start)

This is sufficient for practice:

```bash
# From project root
cd frontend-node

# Install
npm install

# Run
npm run dev
```

**What you get:**
- ✅ Full test interface
- ✅ 4 practice scenarios
- ✅ Instant validation
- ✅ Progress tracking
- ✅ Everything needed for practice

### Option 2: Full Stack (Advanced)

For advanced features like server-side validation:

**Terminal 1 - Frontend:**
```bash
cd frontend-node
npm install
npm run dev
```

**Terminal 2 - Backend (Go):**
```bash
cd backend-go
go mod download
go run main.go
```

**Terminal 3 - Python Evaluator (Optional):**
```bash
cd evaluator-python
pip install -r requirements.txt
python main.py
```

### Option 3: Docker (Production-like)

```bash
# From project root
docker-compose up -d
```

Access at: `http://localhost:3000`

Stop with:
```bash
docker-compose down
```

## 📁 Project Structure Overview

```
mcq-runner-ml-ai/
├── frontend-node/              ← React app (START HERE)
│   ├── src/
│   │   ├── components/        ← UI components
│   │   └── pages/             ← Pages (index, practice, test)
│   ├── public/                ← Static files
│   ├── package.json           ← Dependencies
│   └── next.config.js         ← Next.js config
│
├── scenarios/                  ← Practice questions (JSON)
│   ├── easy/
│   ├── medium/
│   └── hard/
│
├── backend-go/                 ← Go API (optional)
│   └── main.go
│
└── evaluator-python/           ← Python validation (optional)
    └── main.py
```

## 🎯 What to Do After Setup

### 1. Test the Installation

Visit: `http://localhost:3000`

You should see:
- ✅ Landing page loads
- ✅ "Practice Mode" and "Test Mode" buttons visible
- ✅ No console errors (press F12 to check)

### 2. Try Your First Practice

1. Click **"Practice Mode"**
2. You'll see a scenario with:
   - User query at top
   - Tool list on left (click to expand)
   - Answer editor on right
3. Try answering!
4. Click **"Submit Answer"**
5. See instant feedback

### 3. Navigate Scenarios

Use the arrow buttons or:
- **Next Scenario**: Right arrow
- **Previous Scenario**: Left arrow

### 4. Review Your Progress

Check the top-right corner for:
- Questions completed
- Success rate
- Average time

## 🐛 Troubleshooting

### Issue: "Command not found: npm"

**Solution**: Install Node.js from [nodejs.org](https://nodejs.org/)

### Issue: "Port 3000 already in use"

**Solution**: Kill the process or use a different port:
```bash
PORT=3001 npm run dev
```

Then visit: `http://localhost:3001`

### Issue: "Module not found"

**Solution**: Delete and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Monaco Editor not loading

**Solution**: Clear browser cache and reload (Ctrl+Shift+R)

### Issue: Scenarios not loading

**Solution**: Check that `/scenarios` folder exists with JSON files

### Issue: JSON validation not working

**Solution**: Check browser console (F12) for errors

## 🔍 Verifying Installation

### Quick Health Check:

1. **Server Running?**
   ```
   Visit: http://localhost:3000
   Should load landing page
   ```

2. **Practice Mode Works?**
   ```
   Click "Practice Mode"
   Should see test interface
   ```

3. **Scenarios Load?**
   ```
   Should see scenario counter: "1 / 4"
   ```

4. **Editor Works?**
   ```
   Type in the answer box
   Should see syntax highlighting
   ```

5. **Validation Works?**
   ```
   Submit an answer
   Should see feedback
   ```

All ✅? **You're ready to practice!**

## 📝 Adding More Scenarios

Want to add your own practice questions?

### Create New Scenario:

1. Go to `scenarios/easy/` (or medium/hard)

2. Create new JSON file: `my-scenario.json`

3. Use this template:
```json
{
  "id": "custom_001",
  "title": "My Scenario",
  "difficulty": "easy",
  "category": "Custom",
  "timeLimit": 300,
  "points": 10,
  "query": "User query here",
  "tools": [
    {
      "name": "function_name",
      "description": "What it does",
      "parameters": {
        "type": "object",
        "properties": {
          "param1": {
            "type": "string",
            "description": "Parameter description"
          }
        },
        "required": ["param1"]
      }
    }
  ],
  "correct_answer": {
    "selected_function": "function_name",
    "arguments": {
      "param1": "value"
    }
  },
  "explanation": "Why this is correct"
}
```

4. Update `practice.jsx` to include your file

5. Restart dev server

## 🎨 Customization

### Change Theme Colors

Edit `frontend-node/tailwind.config.js`:
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#your-color',
        // Add custom colors
      }
    }
  }
}
```

### Change Time Limits

Edit scenario JSON files:
```json
"timeLimit": 300  // Change to desired seconds
```

### Disable Hints

Edit `TestInterface.jsx`:
```javascript
const [showHints, setShowHints] = useState(false); // Default to false
```

## 📊 Performance Optimization

### For Faster Loading:

1. **Production Build**:
```bash
npm run build
npm start
```

2. **Enable Caching**:
```javascript
// next.config.js
module.exports = {
  swcMinify: true,
  compress: true
}
```

## 🔐 Security Notes

### For Local Practice:
- No security concerns, it's all local

### For Deployment:
- Use HTTPS
- Add authentication
- Sanitize user inputs
- Rate limit API calls

## 📚 Additional Resources

### Documentation:
- `README.md` - Full project overview
- `QUICK_START.md` - Fast setup guide
- `CHEAT_SHEET.md` - Quick reference
- `PROJECT_SUMMARY.md` - What's been built

### External Links:
- [React Docs](https://react.dev/)
- [Next.js Docs](https://nextjs.org/docs)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)

## 🆘 Getting Help

### If You're Stuck:

1. **Check browser console** (F12 → Console tab)
2. **Check terminal output** (where you ran `npm run dev`)
3. **Read error messages carefully**
4. **Try restarting dev server**
5. **Clear browser cache**

### Common Error Messages:

```
Error: Cannot find module 'xyz'
Fix: npm install
```

```
Error: Port 3000 in use
Fix: Use different port or kill existing process
```

```
Error: Invalid JSON
Fix: Check for syntax errors in scenario files
```

## ✅ Final Checklist

Before starting practice:

- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install` completed)
- [ ] Dev server running (`npm run dev`)
- [ ] Browser shows landing page (http://localhost:3000)
- [ ] Practice mode accessible
- [ ] Scenarios loading correctly
- [ ] Answer editor working
- [ ] Validation providing feedback

All checked? **You're ready! Start practicing! 🚀**

## 🎯 Next Steps

1. **Complete Tutorial** (when available)
2. **Practice all Easy scenarios**
3. **Progress to Medium**
4. **Try Test Mode**
5. **Review mistakes**
6. **Take Turing test!**

## 💪 You're All Set!

Everything is configured and ready. Time to practice and ace that Turing test!

```bash
# Start practicing now:
cd frontend-node
npm run dev
# Visit http://localhost:3000
# Click "Practice Mode"
# Start with Easy scenarios
# Build your confidence
# You got this! 🚀
```

---

**Questions?** Check the other documentation files or review troubleshooting section.

**Happy practicing! 💪**
