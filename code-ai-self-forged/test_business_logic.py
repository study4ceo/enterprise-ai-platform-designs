"""Test business logic problems with the AI agent."""

from reasoning_agent import ReasoningAgent
from logger import setup_logging, get_logger
from rich.console import Console
from rich.panel import Panel

setup_logging()
logger = get_logger(__name__)
console = Console()


def test_shipping_calculator():
    """Test shipping cost calculator."""
    console.print("\n[bold cyan]TEST 1: Shipping Cost Calculator[/bold cyan]\n")
    
    problem = """
Calculate shipping costs with multiple factors:
1. Base cost by weight
2. Distance multiplier (zones: local 1.0x, regional 1.5x, national 2.0x, international 3.0x)
3. Surcharges: oversized (+$25), fragile (+$15), express (+50%)
4. Compare Standard vs Express options
5. Recommend cheapest and fastest option

Shipment details:
- Weight: 15 lbs
- Dimensions: 24" x 18" x 12" (oversized if any dimension > 20")
- Destination zone: Regional
- Fragile: Yes
- Base rate: $0.50 per lb

Calculate costs for both Standard and Express shipping and provide recommendations.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Shipping Calculator Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]



def test_discount_calculator():
    """Test discount calculator with complex rules."""
    console.print("\n[bold cyan]TEST 2: Discount Calculator[/bold cyan]\n")
    
    problem = """
Apply complex discount rules to a shopping cart:
1. Apply percentage discounts per category
2. Handle buy-2-get-1-free offers
3. Apply tiered discounts: spend $100+ get 10% off, $200+ get 15% off, $300+ get 20% off
4. Stack applicable discounts correctly
5. Calculate final price and total savings

Cart items:
{"product": "Laptop", "category": "Electronics", "price": 1200, "quantity": 1}
{"product": "Mouse", "category": "Electronics", "price": 25, "quantity": 3}
{"product": "Desk", "category": "Furniture", "price": 450, "quantity": 1}
{"product": "Chair", "category": "Furniture", "price": 350, "quantity": 1}

Discount rules:
- Electronics: 5% off
- Buy-2-get-1-free on Mouse
- Tiered discount based on total

Show itemized discounts and final total.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Discount Calculator Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_leave_balance():
    """Test employee leave balance calculator."""
    console.print("\n[bold cyan]TEST 3: Employee Leave Balance Calculator[/bold cyan]\n")
    
    problem = """
Calculate employee leave balances:
1. Calculate accrued leave days based on tenure
2. Subtract used leave
3. Account for carryover rules (max 5 days from previous year)
4. Predict when employee reaches full balance
5. Flag negative balances

Employee data:
{"name": "John", "start_date": "2024-01-15", "accrual_rate": 1.5, "used_days": 8, "carryover": 3}
{"name": "Jane", "start_date": "2023-06-01", "accrual_rate": 2.0, "used_days": 18, "carryover": 5}
{"name": "Bob", "start_date": "2025-03-20", "accrual_rate": 1.25, "used_days": 12, "carryover": 0}

Current date: 2026-07-25
Accrual: days_per_month based on accrual_rate

Show leave balances and alerts.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Leave Balance Result",
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
    """Run all business logic tests."""
    console.print("[bold yellow]═" * 40)
    console.print("BUSINESS LOGIC TEST SUITE")
    console.print("Testing Code-AI-Self-Forged")
    console.print("═" * 40 + "[/bold yellow]\n")
    
    results = []
    
    # Run tests
    results.append(("Shipping Calculator", test_shipping_calculator()))
    results.append(("Discount Calculator", test_discount_calculator()))
    results.append(("Leave Balance", test_leave_balance()))
    
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
