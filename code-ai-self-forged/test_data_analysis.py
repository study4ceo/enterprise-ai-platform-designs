"""Test data analysis problems with the AI agent."""

from reasoning_agent import ReasoningAgent
from logger import setup_logging, get_logger
from rich.console import Console
from rich.panel import Panel

setup_logging()
logger = get_logger(__name__)
console = Console()


def test_log_analysis():
    """Test log parsing and error detection."""
    console.print("\n[bold cyan]TEST 1: Log Analysis for Error Detection[/bold cyan]\n")
    
    problem = """
Parse these application logs and provide:
1. All errors grouped by error type
2. Count of occurrences for each error type
3. Top 3 most frequent errors with first and last occurrence timestamps
4. Total error rate (errors per hour)

Logs:
2026-07-25 08:15:23 INFO User logged in: user123
2026-07-25 08:16:45 ERROR Database connection failed: timeout after 30s
2026-07-25 08:17:12 ERROR Database connection failed: timeout after 30s
2026-07-25 08:18:33 WARNING High memory usage: 85%
2026-07-25 08:19:01 ERROR API timeout - endpoint /users - 504 Gateway Timeout
2026-07-25 08:20:15 ERROR Database connection failed: timeout after 30s
2026-07-25 08:21:42 INFO Request processed successfully
2026-07-25 08:22:18 ERROR Authentication failed: invalid token
2026-07-25 08:23:55 ERROR API timeout - endpoint /orders - 504 Gateway Timeout
2026-07-25 08:24:31 ERROR Authentication failed: invalid token
2026-07-25 08:25:47 ERROR Database connection failed: timeout after 30s
2026-07-25 08:26:12 INFO Cache cleared
2026-07-25 08:27:38 ERROR Authentication failed: invalid token
2026-07-25 08:28:51 ERROR File not found: /data/users.csv
2026-07-25 08:29:24 ERROR API timeout - endpoint /users - 504 Gateway Timeout
2026-07-25 09:15:18 ERROR Database connection failed: timeout after 30s

Generate a detailed error analysis report.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Log Analysis Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_sales_aggregation():
    """Test sales data aggregation."""
    console.print("\n[bold cyan]TEST 2: Sales Data Aggregation[/bold cyan]\n")
    
    problem = """
Analyze these sales transactions and calculate:
1. Total revenue per product category
2. Top 3 best-selling products by revenue
3. Top 3 best-selling products by quantity
4. Average transaction value
5. Category performance (% of total revenue)

Transactions:
{"date": "2026-07-01", "product": "Laptop Pro", "category": "Electronics", "amount": 1200, "quantity": 1}
{"date": "2026-07-01", "product": "Wireless Mouse", "category": "Electronics", "amount": 25, "quantity": 2}
{"date": "2026-07-02", "product": "Office Desk", "category": "Furniture", "amount": 450, "quantity": 1}
{"date": "2026-07-02", "product": "Ergonomic Chair", "category": "Furniture", "amount": 350, "quantity": 1}
{"date": "2026-07-03", "product": "USB Cable", "category": "Electronics", "amount": 15, "quantity": 5}
{"date": "2026-07-03", "product": "Monitor 27inch", "category": "Electronics", "amount": 400, "quantity": 2}
{"date": "2026-07-04", "product": "Desk Lamp", "category": "Furniture", "amount": 45, "quantity": 3}
{"date": "2026-07-04", "product": "Laptop Pro", "category": "Electronics", "amount": 1200, "quantity": 2}
{"date": "2026-07-05", "product": "Keyboard", "category": "Electronics", "amount": 80, "quantity": 3}
{"date": "2026-07-05", "product": "Office Desk", "category": "Furniture", "amount": 450, "quantity": 2}
{"date": "2026-07-06", "product": "Wireless Mouse", "category": "Electronics", "amount": 25, "quantity": 4}
{"date": "2026-07-06", "product": "Ergonomic Chair", "category": "Furniture", "amount": 350, "quantity": 2}

Generate a comprehensive sales analysis report.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Sales Aggregation Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_csv_transformation():
    """Test CSV data cleaning and transformation."""
    console.print("\n[bold cyan]TEST 3: CSV Data Transformation[/bold cyan]\n")
    
    problem = """
Clean and transform this messy user data:
1. Standardize date formats to YYYY-MM-DD
2. Remove duplicate users based on email
3. Fill missing phone numbers with "N/A"
4. Normalize names to Title Case
5. Report data quality metrics (duplicates found, missing values filled)

User data (list of dicts):
{"id": 1, "name": "john doe", "email": "john@email.com", "signup_date": "07/15/2026", "phone": "555-1234"}
{"id": 2, "name": "JANE SMITH", "email": "jane@email.com", "signup_date": "2026-07-16", "phone": ""}
{"id": 3, "name": "bob wilson", "email": "bob@email.com", "signup_date": "07-17-2026", "phone": "555-5678"}
{"id": 4, "name": "alice brown", "email": "john@email.com", "signup_date": "07/18/2026", "phone": "555-9012"}
{"id": 5, "name": "CHARLIE davis", "email": "charlie@email.com", "signup_date": "2026/07/19", "phone": ""}
{"id": 6, "name": "eve taylor", "email": "eve@email.com", "signup_date": "07-20-2026", "phone": "555-3456"}

Show the cleaned data and a data quality summary.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="CSV Transformation Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def main():
    """Run all data analysis tests."""
    console.print("[bold yellow]═" * 40)
    console.print("DATA ANALYSIS TEST SUITE")
    console.print("Testing Code-AI-Self-Forged")
    console.print("═" * 40 + "[/bold yellow]\n")
    
    results = []
    
    # Run tests
    results.append(("Log Analysis", test_log_analysis()))
    results.append(("Sales Aggregation", test_sales_aggregation()))
    results.append(("CSV Transformation", test_csv_transformation()))
    
    # Summary
    console.print("\n[bold yellow]═" * 40)
    console.print("TEST SUMMARY")
    console.print("═" * 40 + "[/bold yellow]\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[green]✓ PASSED[/green]" if success else "[red]✗ FAILED[/red]"
        console.print(f"{test_name}: {status}")
    
    console.print(f"\n[bold]Total: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("\n[bold green]🎉 All tests passed![/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠️  {total - passed} test(s) failed.[/bold yellow]")


if __name__ == "__main__":
    main()
