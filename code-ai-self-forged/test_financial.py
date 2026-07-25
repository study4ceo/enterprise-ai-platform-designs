"""Test financial calculation problems with the AI agent."""

from reasoning_agent import ReasoningAgent
from logger import setup_logging, get_logger
from rich.console import Console
from rich.panel import Panel

setup_logging()
logger = get_logger(__name__)
console = Console()


def test_financial_report():
    """Test financial report generation."""
    console.print("\n[bold cyan]TEST 1: Financial Report Generator[/bold cyan]\n")
    
    problem = """
Generate a financial report for a business with:
1. Net profit/loss calculation
2. Profit margin percentage
3. Top 3 expense categories
4. Expense breakdown (% of total expenses)
5. Financial health assessment

Financial data:
Income:
- Sales revenue: $125,000
- Service revenue: $45,000
- Consulting fees: $28,000

Expenses:
- Salaries: $85,000
- Rent: $18,000
- Marketing: $22,000
- Utilities: $6,000
- Insurance: $8,000
- Office supplies: $3,500
- Software subscriptions: $4,200

Provide a comprehensive financial report with insights.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Financial Report Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_compound_interest():
    """Test compound interest calculator."""
    console.print("\n[bold cyan]TEST 2: Compound Interest Calculator[/bold cyan]\n")
    
    problem = """
Calculate investment growth with compound interest:
1. Calculate future value after each year
2. Show year-by-year breakdown
3. Calculate total interest earned
4. Compare different compounding frequencies (annually, quarterly, monthly, daily)

Investment parameters:
- Principal amount: $50,000
- Annual interest rate: 6.5%
- Time period: 10 years
- Compounding: monthly

Show detailed calculations and comparison table.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Compound Interest Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_portfolio_rebalancing():
    """Test portfolio rebalancing calculator."""
    console.print("\n[bold cyan]TEST 3: Portfolio Rebalancing[/bold cyan]\n")
    
    problem = """
Calculate trades needed to rebalance an investment portfolio:
1. Calculate current allocation percentages
2. Determine target allocation percentages
3. Identify which assets to buy/sell
4. Calculate exact dollar amounts for rebalancing
5. Show before/after comparison

Current portfolio (total value: $100,000):
- Stocks: $55,000
- Bonds: $25,000
- Real Estate: $15,000
- Cash: $5,000

Target allocation:
- Stocks: 50%
- Bonds: 30%
- Real Estate: 15%
- Cash: 5%

Show rebalancing trades and final allocation.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Portfolio Rebalancing Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_loan_amortization():
    """Test loan amortization calculator."""
    console.print("\n[bold cyan]TEST 4: Loan Amortization Schedule[/bold cyan]\n")
    
    problem = """
Calculate loan amortization schedule:
1. Monthly payment amount
2. First 12 months payment breakdown (principal vs interest)
3. Total interest paid over loan term
4. Total amount paid
5. Payoff date

Loan parameters:
- Loan amount: $250,000
- Annual interest rate: 4.5%
- Loan term: 30 years
- Payment frequency: Monthly

Show the amortization schedule for the first year and summary statistics.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Loan Amortization Result",
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
    """Run all financial calculation tests."""
    console.print("[bold yellow]═" * 40)
    console.print("FINANCIAL CALCULATIONS TEST SUITE")
    console.print("Testing Code-AI-Self-Forged")
    console.print("═" * 40 + "[/bold yellow]\n")
    
    results = []
    
    # Run tests
    results.append(("Financial Report", test_financial_report()))
    results.append(("Compound Interest", test_compound_interest()))
    results.append(("Portfolio Rebalancing", test_portfolio_rebalancing()))
    results.append(("Loan Amortization", test_loan_amortization()))
    
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
