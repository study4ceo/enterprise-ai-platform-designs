# Coding Agent Modes and Skills

Complete guide to modes and skills in AI coding assistants (Claude Code, Cursor, GitHub Copilot, etc.)

## Part 1: Coding Agent Modes

### 1. Autocomplete Mode (Inline Suggestions)

**What it is:**
- Real-time code suggestions as you type
- Single line or small block completions
- Non-intrusive, ghost text

**When to use:**
- Writing repetitive code
- Implementing patterns you've started
- Boilerplate generation
- Fast coding flow

**Examples:**

```python
# You type:
def calculate_total_price(items):
    
# AI suggests:
    total = sum(item.price * item.quantity for item in items)
    return total
```

```javascript
// You type:
const fetchUser = async (userId) => {

// AI suggests:
    const response = await fetch(`/api/users/${userId}`);
    return await response.json();
```

**Trigger:** Automatic as you type

**Tools:**
- GitHub Copilot
- Cursor Tab
- Tabnine
- Codeium

**Best practices:**
- Accept (Tab) if correct
- Keep typing to ignore
- Use for patterns you've established in codebase

---

### 2. Chat Mode (Conversational)

**What it is:**
- Multi-turn conversation about code
- Ask questions, get explanations
- Iterative refinement

**When to use:**
- Need explanation of complex code
- Design discussions
- Learning new concepts
- Clarifying requirements

**Examples:**

```
You: How does this sorting algorithm work?
AI: This is a merge sort implementation...

You: Can you optimize it for small arrays?
AI: Yes, we can add a cutoff to insertion sort...

You: Show me the modified code
AI: [provides optimized version]
```

**Trigger:** Manual activation (Cmd+K, Ctrl+K, chat panel)

**Tools:**
- Cursor Chat
- GitHub Copilot Chat
- Claude Code (Windsurf)
- Codeium Chat

**Best practices:**
- Be specific in questions
- Provide context from codebase
- Iterate on solutions
- Ask "why" for learning

---

### 3. Command Mode (Inline Editing)

**What it is:**
- Select code → give instruction → AI edits
- Direct manipulation of selection
- Fast refactoring

**When to use:**
- Refactoring existing code
- Quick fixes
- Style changes
- Adding features to existing code

**Examples:**

```python
# Select this code:
def process_users(users):
    result = []
    for user in users:
        if user.active:
            result.append(user.name)
    return result

# Command: "Convert to list comprehension"
# AI changes to:
def process_users(users):
    return [user.name for user in users if user.active]
```

```javascript
// Select: 
function calculateTotal(items) {
    let total = 0;
    for (let i = 0; i < items.length; i++) {
        total += items[i].price;
    }
    return total;
}

// Command: "Use reduce"
// AI changes to:
function calculateTotal(items) {
    return items.reduce((total, item) => total + item.price, 0);
}
```

**Trigger:** Select code + Cmd+K (or Ctrl+K)

**Tools:**
- Cursor Cmd+K
- GitHub Copilot inline chat
- Continue.dev
- Windsurf inline edit

**Best practices:**
- Select minimal relevant code
- Clear, specific instructions
- Review changes before accepting

---

### 4. Composer Mode (Multi-File Editing)

**What it is:**
- Edit multiple files simultaneously
- Cross-file refactoring
- Feature implementation spanning files

**When to use:**
- Adding features across multiple files
- Large refactorings
- Architecture changes
- Creating new modules

**Examples:**

```
You: Add user authentication to this app

AI edits:
1. backend/auth.py - creates auth module
2. backend/routes.py - adds auth middleware
3. backend/models.py - adds User model
4. frontend/Login.tsx - creates login component
5. frontend/api.ts - adds auth API calls
```

**Trigger:** Composer panel (Cursor), multi-file mode

**Tools:**
- Cursor Composer (Cmd+I)
- Windsurf Cascade
- Aider (CLI)

**Best practices:**
- Clear description of feature
- Let AI determine which files to edit
- Review all changes before applying
- Use for coherent features, not scattered tasks

---

### 5. Agentic Mode (Autonomous)

**What it is:**
- AI works autonomously with minimal guidance
- Can read docs, run tests, debug
- Iterative improvement until task complete

**When to use:**
- Well-defined tasks
- Time-consuming implementations
- When you can step away
- Prototyping

**Examples:**

```
You: Build a REST API for blog posts with CRUD operations

AI autonomously:
1. Reads existing code patterns
2. Creates models/blog_post.py
3. Creates routes/blog.py
4. Writes tests
5. Runs tests
6. Fixes failing tests
7. Updates documentation
8. Reports completion
```

**Trigger:** Agent mode activation

**Tools:**
- Windsurf Cascade (Flows)
- Devin
- Cursor Agent mode
- GPT Engineer

**Best practices:**
- Clear acceptance criteria
- Let agent iterate
- Review final result
- Use for lower-risk tasks initially

---

### 6. Terminal Mode (Command Execution)

**What it is:**
- AI suggests and executes terminal commands
- Debugging via command output
- Build automation

**When to use:**
- Running tests
- Installing dependencies
- Git operations
- Build/deploy tasks

**Examples:**

```
You: Install the dependencies for this project

AI: I'll run:
npm install

[Executes command]
AI: Dependencies installed successfully. 15 packages added.
```

**Trigger:** Ask AI to run commands

**Tools:**
- Cursor (with terminal access)
- Windsurf
- Warp (AI terminal)

**Best practices:**
- Review dangerous commands before allowing
- Grant terminal access selectively
- Monitor command outputs

---

## Part 2: Skills in Coding Agents

### What are Skills?

**Skills** = Specialized capabilities or knowledge areas that enhance the agent's coding assistance.

Think of skills as **plugins** or **expertise modules** that extend basic code completion.

---

### Core Skills

#### 1. Code Completion Skill

**What it does:**
- Predicts next code tokens
- Suggests completions based on context
- Learns from your codebase patterns

**Sub-skills:**
- Line completion
- Function completion
- Class/interface completion
- Import statement completion

**Example:**
```python
# You type: def fetch_
# AI suggests: def fetch_user_by_id(user_id: int) -> User:
```

---

#### 2. Code Explanation Skill

**What it does:**
- Explains complex code in natural language
- Breaks down algorithms
- Documents code purpose

**Example:**
```python
# You ask: "What does this do?"
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# AI explains:
# "This implements the quicksort algorithm:
# 1. Selects middle element as pivot
# 2. Partitions array into less than, equal to, greater than pivot
# 3. Recursively sorts left and right partitions
# Time: O(n log n) average, O(n²) worst
# Space: O(log n) for recursion stack"
```

---

#### 3. Refactoring Skill

**What it does:**
- Improves code structure without changing behavior
- Applies design patterns
- Reduces complexity

**Sub-skills:**
- Extract method/function
- Rename variables
- Simplify conditionals
- Remove duplication
- Apply SOLID principles

**Example:**
```python
# Before:
def process_order(order):
    if order.status == 'pending':
        if order.total > 100:
            discount = order.total * 0.1
            order.total = order.total - discount
        charge_payment(order)
        send_confirmation(order)
        order.status = 'completed'

# Ask: "Refactor this for clarity"

# After:
def process_order(order):
    if not order.is_pending():
        return
    
    apply_discount_if_eligible(order)
    charge_payment(order)
    send_confirmation(order)
    order.mark_completed()

def apply_discount_if_eligible(order):
    if order.total > 100:
        order.apply_discount(0.1)
```

---

#### 4. Test Generation Skill

**What it does:**
- Generates unit tests
- Creates test cases
- Identifies edge cases

**Sub-skills:**
- Unit test generation
- Integration test generation
- Mock/stub creation
- Test data generation

**Example:**
```python
# For this function:
def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)

# AI generates:
def test_calculate_discount():
    # Happy path
    assert calculate_discount(100, 10) == 90
    assert calculate_discount(50, 20) == 40
    
    # Edge cases
    assert calculate_discount(100, 0) == 100  # No discount
    assert calculate_discount(100, 100) == 0  # Full discount
    
    # Error cases
    with pytest.raises(ValueError):
        calculate_discount(100, -10)  # Negative discount
    with pytest.raises(ValueError):
        calculate_discount(100, 101)  # > 100% discount
```

---

#### 5. Bug Detection Skill

**What it does:**
- Identifies potential bugs
- Spots anti-patterns
- Finds security vulnerabilities

**Sub-skills:**
- Null pointer detection
- Race condition detection
- Memory leak detection
- Security vulnerability scanning
- Logic error detection

**Example:**
```python
# Your code:
def get_user_email(user_id):
    user = db.query(User).filter_by(id=user_id).first()
    return user.email  # ⚠️ Bug!

# AI warns:
# "Potential NullPointerError: `user` could be None if not found.
# Suggested fix:"

def get_user_email(user_id):
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise UserNotFoundException(f"User {user_id} not found")
    return user.email
```

---

#### 6. Documentation Skill

**What it does:**
- Generates docstrings
- Creates API documentation
- Writes README files

**Sub-skills:**
- Function documentation
- Class documentation
- Module documentation
- API docs generation

**Example:**
```python
# Your code:
def fetch_user_orders(user_id, start_date=None, end_date=None, status=None):
    query = Order.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    if status:
        query = query.filter(Order.status == status)
    return query.all()

# AI generates:
def fetch_user_orders(user_id, start_date=None, end_date=None, status=None):
    """
    Fetch orders for a specific user with optional filters.
    
    Args:
        user_id (int): The ID of the user
        start_date (datetime, optional): Filter orders created after this date
        end_date (datetime, optional): Filter orders created before this date
        status (str, optional): Filter by order status ('pending', 'completed', 'cancelled')
    
    Returns:
        list[Order]: List of Order objects matching the filters
    
    Example:
        >>> fetch_user_orders(123, status='completed')
        [<Order id=1>, <Order id=2>]
    """
    # ... implementation
```

---

#### 7. Code Translation Skill

**What it does:**
- Converts code between languages
- Translates paradigms (OOP ↔ Functional)

**Example:**
```python
# Python code:
def filter_active_users(users):
    return [u for u in users if u.active]

# Ask: "Convert to JavaScript"
# AI generates:
const filterActiveUsers = (users) => {
    return users.filter(u => u.active);
};

// Or TypeScript:
const filterActiveUsers = (users: User[]): User[] => {
    return users.filter(u => u.active);
};
```

---

#### 8. Performance Optimization Skill

**What it does:**
- Identifies performance bottlenecks
- Suggests optimizations
- Improves algorithmic complexity

**Example:**
```python
# Your code:
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

# AI suggests:
# "This is O(n²). Here's an O(n) solution:"

def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
```

---

#### 9. Architecture Design Skill

**What it does:**
- Suggests design patterns
- Recommends architecture
- Provides structural guidance

**Example:**
```
You: "I need to process user uploads asynchronously"

AI suggests:
"Use the Producer-Consumer pattern with a message queue:

1. API receives upload → pushes to queue (Producer)
2. Worker processes from queue (Consumer)
3. Updates database when done

Recommended stack:
- Queue: Redis/RabbitMQ
- Workers: Celery (Python) or Bull (Node.js)
- Storage: S3/MinIO

Would you like me to implement this?"
```

---

#### 10. Debugging Skill

**What it does:**
- Analyzes error messages
- Suggests fixes
- Walks through debugging process

**Example:**
```
You: "I'm getting: AttributeError: 'NoneType' object has no attribute 'email'"

AI analyzes:
"This error means you're calling .email on a None object.

Looking at your code on line 45:
user = get_user(user_id)
print(user.email)  # ← Error here

The issue: get_user() returns None when user not found.

Fix options:
1. Add null check:
   if user:
       print(user.email)

2. Raise exception in get_user():
   if not user:
       raise UserNotFoundException()

3. Use default:
   email = user.email if user else 'unknown@example.com'

Which approach fits your use case?"
```

---

#### 11. API Integration Skill

**What it does:**
- Generates API client code
- Creates request/response handlers
- Handles authentication

**Example:**
```
You: "Integrate Stripe payment API"

AI generates:
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_payment_intent(amount: int, currency: str = 'usd'):
    """
    Create a Stripe payment intent.
    
    Args:
        amount: Amount in cents (e.g., 1000 = $10.00)
        currency: Currency code (default: usd)
    
    Returns:
        PaymentIntent object with client_secret
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True}
        )
        return intent
    except stripe.error.CardError as e:
        # Card declined
        raise PaymentError(f"Card declined: {e.user_message}")
    except stripe.error.StripeError as e:
        # Other Stripe errors
        raise PaymentError(f"Payment failed: {str(e)}")
```

---

#### 12. Database Query Skill

**What it does:**
- Generates SQL queries
- Creates ORM queries
- Optimizes queries

**Example:**
```
You: "Get users who made purchases in the last 30 days"

AI generates:

# SQL:
SELECT DISTINCT u.*
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at >= NOW() - INTERVAL 30 DAY
  AND o.status = 'completed';

# SQLAlchemy ORM:
from datetime import datetime, timedelta

thirty_days_ago = datetime.now() - timedelta(days=30)
users = db.session.query(User)\
    .join(Order)\
    .filter(Order.created_at >= thirty_days_ago)\
    .filter(Order.status == 'completed')\
    .distinct()\
    .all()

# With optimization:
# "Add index on orders.created_at and orders.user_id for better performance"
```

---

## Skill Comparison Across Tools

| Skill | GitHub Copilot | Cursor | Windsurf | Tabnine |
|-------|----------------|--------|----------|---------|
| Autocomplete | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |
| Chat | ★★★★ | ★★★★★ | ★★★★★ | ★★★ |
| Refactoring | ★★★ | ★★★★★ | ★★★★ | ★★ |
| Multi-file edit | ★★ | ★★★★★ | ★★★★★ | ★ |
| Test generation | ★★★★ | ★★★★ | ★★★★ | ★★ |
| Bug detection | ★★★ | ★★★★ | ★★★★ | ★★ |
| Documentation | ★★★★ | ★★★★ | ★★★★ | ★★★ |
| Terminal access | ★★ | ★★★★ | ★★★★★ | ★ |
| Autonomous mode | ★ | ★★★ | ★★★★★ | ★ |

---

## Mode Selection Guide

### Quick Tasks (< 5 min)
- **Use:** Autocomplete or Command mode
- **Why:** Fast, non-intrusive

### Code Review/Learning
- **Use:** Chat mode
- **Why:** Explanations and back-and-forth

### Refactoring
- **Use:** Command mode
- **Why:** Precise inline editing

### Feature Development
- **Use:** Composer mode
- **Why:** Multi-file coordination

### Complex Projects
- **Use:** Agentic mode
- **Why:** Autonomous work while you focus elsewhere

### Debugging
- **Use:** Chat + Terminal mode
- **Why:** Analyze errors, run tests

---

## Best Practices by Mode

### Autocomplete
✅ Let it complete patterns
✅ Train it with good examples
❌ Don't blindly accept all suggestions

### Chat
✅ Provide context from files
✅ Ask follow-up questions
❌ Don't assume it sees all code

### Command
✅ Select minimal relevant code
✅ Be specific in instructions
❌ Don't select entire files for small changes

### Composer
✅ Describe feature clearly
✅ Review all files changed
❌ Don't use for unrelated changes

### Agentic
✅ Clear acceptance criteria
✅ Monitor progress
❌ Don't use for critical production code initially

---

## Skill Development Tips

### For Users:
1. **Learn keyboard shortcuts** - Faster mode switching
2. **Provide good context** - Better AI suggestions
3. **Review suggestions** - Don't accept blindly
4. **Iterate** - Refine prompts if first try isn't perfect
5. **Combine modes** - Chat to plan, Command to execute

### For Teams:
1. **Share prompts** - Document what works
2. **Code review AI output** - Same standards as human code
3. **Track time saved** - Measure productivity gains
4. **Train on codebase** - Some tools learn from your code
5. **Set guidelines** - When to use which mode/skill

---

## Interview Questions & Answers

**Q: What's the difference between Copilot and Cursor?**

A: "GitHub Copilot focuses on autocomplete and chat. Cursor adds:
- Multi-file editing (Composer)
- Better codebase understanding
- More control over edits
- Built-in terminal integration

Copilot is simpler, Cursor is more powerful but steeper learning curve."

**Q: When would you use agentic mode vs command mode?**

A: "Command mode for:
- Quick refactoring
- Changes to specific selection
- When I know exactly what I want

Agentic mode for:
- Feature spanning multiple files
- When requirements are clear but implementation unclear
- Time-consuming boilerplate

Command is faster and more controlled. Agentic is for larger scopes."

**Q: How do AI coding skills improve productivity?**

A: "Skills reduce different friction points:
- Autocomplete: Typing speed
- Refactoring: Code quality
- Test generation: Test coverage
- Documentation: Communication
- Bug detection: Debugging time

Combined, these can save 30-40% of coding time for repetitive tasks, letting developers focus on design and complex logic."

---

## Tool-Specific Features

### Cursor
- **Cmd+K**: Inline command
- **Cmd+I**: Composer mode
- **@codebase**: Reference entire codebase
- **@docs**: Reference documentation

### GitHub Copilot
- **Tab**: Accept suggestion
- **Cmd+→**: Accept word
- **Alt+]**: Next suggestion
- **/explain**: Explain code
- **/fix**: Fix bugs

### Windsurf (Claude)
- **Cascade**: Autonomous multi-file edits
- **Flows**: Saved workflows
- **Terminal**: Full command execution
- **Context**: Automatic file context

### Continue.dev
- **Open source alternative**
- **Customizable models**
- **Local or cloud**
- **VS Code extension**

---

## Future Skills (Emerging)

1. **Code Security Auditing** - Identify vulnerabilities automatically
2. **Compliance Checking** - GDPR, accessibility, etc.
3. **Performance Profiling** - Identify bottlenecks during coding
4. **UI/UX Suggestions** - Design feedback for frontend
5. **Database Migration** - Auto-generate migrations
6. **Infrastructure as Code** - Generate Terraform, K8s configs
7. **Code Evolution** - Upgrade dependencies, migrate APIs

---

## Summary

**Modes** = How you interact with AI
**Skills** = What AI can help you with

**Master autocomplete** for daily coding → **Add command mode** for refactoring → **Use composer** for features → **Try agentic** for complex tasks

Start simple, gradually adopt advanced modes as you learn.
