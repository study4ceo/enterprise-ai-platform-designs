# Real-World Production Problems for Code-AI-Self-Forged

## Data Analysis & Processing

### 1. Log Analysis for Error Detection
**Problem:** Parse application logs and identify error patterns
```
Given a list of log entries, find all errors, group by error type, 
count occurrences, and report the top 5 most frequent errors with timestamps.
```
**Input:**
```python
logs = [
    "2026-07-25 10:15:23 INFO User logged in",
    "2026-07-25 10:16:45 ERROR Database connection failed",
    "2026-07-25 10:17:12 ERROR Database connection failed",
    "2026-07-25 10:18:33 WARNING High memory usage",
    "2026-07-25 10:19:01 ERROR API timeout - endpoint /users",
    "2026-07-25 10:20:15 ERROR Database connection failed",
]
```

### 2. Sales Data Aggregation
**Problem:** Calculate business metrics from transaction data
```
Given sales transactions, calculate:
- Total revenue per product category
- Top 3 best-selling products
- Average transaction value
- Revenue growth rate (if historical data provided)
```
**Input:**
```python
transactions = [
    {"date": "2026-07-01", "product": "Laptop", "category": "Electronics", "amount": 1200, "quantity": 1},
    {"date": "2026-07-02", "product": "Mouse", "category": "Electronics", "amount": 25, "quantity": 2},
    {"date": "2026-07-03", "product": "Desk", "category": "Furniture", "amount": 450, "quantity": 1},
    # ... more transactions
]
```

### 3. CSV Data Transformation
**Problem:** Clean and transform messy CSV-like data
```
Given a list of dictionaries with inconsistent fields and formats:
- Standardize date formats (YYYY-MM-DD)
- Remove duplicates based on ID
- Fill missing values with sensible defaults
- Export to clean JSON format
```

## API & Integration

### 4. REST API Health Checker
**Problem:** Monitor multiple API endpoints and report status
```
Check the health of multiple API endpoints:
- Send GET requests to each endpoint
- Record response time
- Check status code (200 = healthy)
- Generate a health report with alerts for failing endpoints
```
**Input:**
```python
endpoints = [
    "https://api.example.com/health",
    "https://api.example.com/users",
    "https://api.example.com/orders",
]
```

### 5. Webhook Payload Parser
**Problem:** Parse and validate incoming webhook payloads
```
Given a webhook payload (JSON), extract key information:
- Validate required fields exist
- Parse nested data structures
- Transform to internal data model
- Log any validation errors
```

## Mathematical & Financial

### 6. Financial Report Generator
**Problem:** Calculate financial metrics from income/expense data
```
Given monthly income and expenses:
- Calculate net profit/loss
- Compute profit margin percentage
- Identify highest expense categories
- Generate a summary report
```
**Input:**
```python
data = {
    "income": {"sales": 50000, "services": 20000},
    "expenses": {"salaries": 30000, "rent": 5000, "marketing": 8000, "utilities": 2000}
}
```

### 7. Compound Interest Calculator
**Problem:** Calculate investment growth over time
```
Given principal amount, interest rate, time period, and compounding frequency:
- Calculate future value
- Show year-by-year breakdown
- Calculate total interest earned
- Compare different compounding frequencies
```

### 8. Portfolio Rebalancing
**Problem:** Calculate trades needed to rebalance investment portfolio
```
Given current portfolio allocation and target allocation:
- Calculate percentage differences
- Determine which assets to buy/sell
- Calculate exact amounts for rebalancing
- Show before/after comparison
```

## Text Processing

### 9. Email Subject Line Analyzer
**Problem:** Analyze email subject lines for spam indicators
```
Given a list of email subjects:
- Detect spam patterns (ALL CAPS, excessive !!!, money keywords)
- Calculate spam score (0-100)
- Categorize as spam/not spam
- Provide reasoning for classification
```

### 10. Text Statistics Generator
**Problem:** Analyze text and generate comprehensive statistics
```
Given a text document:
- Count words, sentences, paragraphs
- Calculate average word/sentence length
- Find most common words (excluding stop words)
- Calculate readability score (Flesch-Kincaid)
- Identify longest sentence
```

## Algorithm & Optimization

### 11. Meeting Room Scheduler
**Problem:** Find optimal meeting room allocation
```
Given a list of meeting requests with start/end times:
- Determine minimum rooms needed
- Assign meetings to rooms avoiding conflicts
- Show schedule for each room
- Identify any conflicts
```
**Input:**
```python
meetings = [
    {"id": 1, "start": "09:00", "end": "10:00", "title": "Stand-up"},
    {"id": 2, "start": "09:30", "end": "11:00", "title": "Design Review"},
    {"id": 3, "start": "10:30", "end": "11:30", "title": "Client Call"},
]
```

### 12. Task Priority Optimizer
**Problem:** Optimize task execution order based on priority and dependencies
```
Given tasks with priority, estimated time, and dependencies:
- Sort by optimal execution order
- Calculate total completion time
- Identify critical path
- Highlight tasks that can run in parallel
```

### 13. Inventory Reorder Calculator
**Problem:** Calculate when to reorder inventory items
```
Given current stock, daily usage rate, lead time, and safety stock:
- Calculate reorder point
- Determine optimal reorder quantity
- Predict stockout date if no reorder
- Generate reorder alerts
```

## Data Validation & Quality

### 14. Email Validator
**Problem:** Validate email addresses against multiple rules
```
Given a list of email addresses:
- Check basic format (regex)
- Validate domain structure
- Flag suspicious patterns
- Categorize by domain type (corporate, free, custom)
```

### 15. Credit Card Number Validator
**Problem:** Validate credit card numbers using Luhn algorithm
```
Given credit card numbers:
- Validate using Luhn algorithm
- Identify card type (Visa, Mastercard, Amex)
- Mask all but last 4 digits
- Report valid/invalid with reasoning
```

### 16. Password Strength Checker
**Problem:** Evaluate password strength and provide feedback
```
Given passwords:
- Check length, complexity requirements
- Detect common patterns (123, abc, qwerty)
- Calculate entropy score
- Provide specific improvement suggestions
```

## Time Series & Trends

### 17. Moving Average Calculator
**Problem:** Calculate moving averages for trend analysis
```
Given time series data (daily sales, stock prices, etc.):
- Calculate 7-day and 30-day moving averages
- Identify trend direction (up/down/flat)
- Detect crossover points
- Generate buy/sell signals
```

### 18. Anomaly Detector
**Problem:** Identify outliers in numeric data
```
Given a series of measurements:
- Calculate mean and standard deviation
- Identify outliers (> 2 standard deviations)
- Flag suspicious data points
- Provide statistical summary
```

### 19. Seasonal Pattern Detector
**Problem:** Identify seasonal patterns in data
```
Given monthly data over multiple years:
- Calculate monthly averages
- Identify peak and low months
- Calculate seasonality index
- Predict next period based on pattern
```

## System & Operations

### 20. Disk Space Usage Analyzer
**Problem:** Analyze disk usage patterns and recommend cleanup
```
Given directory sizes:
- Sort by largest to smallest
- Calculate percentage of total
- Identify growth rate if historical data available
- Flag candidates for cleanup (temp files, old logs)
```

### 21. Database Query Optimizer
**Problem:** Analyze SQL queries for performance issues
```
Given SQL queries:
- Identify missing indexes
- Detect N+1 query patterns
- Check for SELECT * usage
- Suggest optimizations
```

### 22. Configuration Validator
**Problem:** Validate application configuration files
```
Given a config dictionary:
- Check required fields are present
- Validate data types
- Check ranges for numeric values
- Ensure no conflicting settings
- Generate validation report
```

## Business Logic

### 23. Shipping Cost Calculator
**Problem:** Calculate shipping costs based on multiple factors
```
Given weight, dimensions, destination, shipping speed:
- Calculate base shipping cost
- Apply distance-based multipliers
- Add surcharges (oversized, fragile, express)
- Compare carrier options
- Recommend cheapest/fastest option
```

### 24. Discount Calculator
**Problem:** Apply complex discount rules to cart
```
Given cart items and discount rules:
- Apply percentage discounts
- Handle buy-X-get-Y-free offers
- Apply tiered discounts (spend $100 get 10% off)
- Stack applicable discounts
- Calculate final price and savings
```

### 25. Employee Leave Balance Calculator
**Problem:** Calculate employee leave balances and entitlements
```
Given employee start date, leave taken, and leave policy:
- Calculate accrued leave days
- Subtract used leave
- Account for carryover rules
- Predict when employee reaches full balance
- Flag negative balances
```

## Testing These Problems

Run any problem with:
```bash
python main.py "Calculate compound interest for $10000 principal, 5% annual rate, 10 years, compounded monthly"
```

Or in interactive mode:
```bash
python main.py
You: Parse these logs and find the top 3 errors: [logs data here]
```

The agent will autonomously write code, execute it, and provide results!
