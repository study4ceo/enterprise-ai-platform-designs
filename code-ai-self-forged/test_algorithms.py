"""Test algorithm and optimization problems with the AI agent."""

from reasoning_agent import ReasoningAgent
from logger import setup_logging, get_logger
from rich.console import Console
from rich.panel import Panel

setup_logging()
logger = get_logger(__name__)
console = Console()


def test_meeting_scheduler():
    """Test meeting room scheduler."""
    console.print("\n[bold cyan]TEST 1: Meeting Room Scheduler[/bold cyan]\n")
    
    problem = """
Optimize meeting room allocation:
1. Determine minimum rooms needed
2. Assign meetings to rooms avoiding conflicts
3. Show schedule for each room
4. Identify any time conflicts

Meetings:
{"id": 1, "title": "Stand-up", "start": "09:00", "end": "09:30"}
{"id": 2, "title": "Design Review", "start": "09:15", "end": "10:30"}
{"id": 3, "title": "Client Call", "start": "10:00", "end": "11:00"}
{"id": 4, "title": "Team Sync", "start": "11:00", "end": "12:00"}
{"id": 5, "title": "Planning", "start": "09:30", "end": "10:30"}
{"id": 6, "title": "1-on-1", "start": "14:00", "end": "15:00"}
{"id": 7, "title": "Demo", "start": "14:30", "end": "15:30"}
{"id": 8, "title": "Retrospective", "start": "15:00", "end": "16:00"}

Provide optimal room allocation and schedules.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Meeting Scheduler Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]



def test_task_optimizer():
    """Test task priority optimizer."""
    console.print("\n[bold cyan]TEST 2: Task Priority Optimizer[/bold cyan]\n")
    
    problem = """
Optimize task execution order:
1. Sort tasks by optimal execution order considering dependencies
2. Calculate total completion time
3. Identify critical path
4. Highlight tasks that can run in parallel

Tasks:
{"id": 1, "name": "Setup Database", "priority": 9, "time_hours": 2, "depends_on": []}
{"id": 2, "name": "Create API", "priority": 8, "time_hours": 4, "depends_on": [1]}
{"id": 3, "name": "Build Frontend", "priority": 7, "time_hours": 6, "depends_on": [2]}
{"id": 4, "name": "Write Tests", "priority": 6, "time_hours": 3, "depends_on": [2]}
{"id": 5, "name": "Deploy", "priority": 10, "time_hours": 1, "depends_on": [3, 4]}
{"id": 6, "name": "Documentation", "priority": 5, "time_hours": 2, "depends_on": []}

Show execution order, critical path, and parallel opportunities.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Task Optimizer Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_inventory_calculator():
    """Test inventory reorder calculator."""
    console.print("\n[bold cyan]TEST 3: Inventory Reorder Calculator[/bold cyan]\n")
    
    problem = """
Calculate inventory reorder points:
1. Calculate reorder point for each product
2. Determine optimal reorder quantity (EOQ formula if possible)
3. Predict stockout date if no reorder
4. Generate reorder alerts

Inventory data:
{"product": "Widget A", "current_stock": 150, "daily_usage": 25, "lead_time_days": 5, "safety_stock": 50}
{"product": "Widget B", "current_stock": 80, "daily_usage": 15, "lead_time_days": 7, "safety_stock": 30}
{"product": "Widget C", "current_stock": 200, "daily_usage": 10, "lead_time_days": 3, "safety_stock": 40}
{"product": "Widget D", "current_stock": 45, "daily_usage": 20, "lead_time_days": 4, "safety_stock": 25}

Generate reorder recommendations with urgency levels.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Inventory Calculator Result",
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
    """Run all algorithm tests."""
    console.print("[bold yellow]═" * 40)
    console.print("ALGORITHMS & OPTIMIZATION TEST SUITE")
    console.print("Testing Code-AI-Self-Forged")
    console.print("═" * 40 + "[/bold yellow]\n")
    
    results = []
    
    # Run tests
    results.append(("Meeting Scheduler", test_meeting_scheduler()))
    results.append(("Task Optimizer", test_task_optimizer()))
    results.append(("Inventory Calculator", test_inventory_calculator()))
    
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
