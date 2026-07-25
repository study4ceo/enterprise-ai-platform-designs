"""Run all test suites for Code-AI-Self-Forged."""

import sys
from rich.console import Console
from rich.panel import Panel

console = Console()


def run_test_suite(module_name: str, suite_name: str):
    """Import and run a test suite."""
    try:
        module = __import__(module_name)
        console.print(f"\n[bold blue]Running {suite_name}...[/bold blue]")
        module.main()
        return True
    except Exception as e:
        console.print(f"[red]Error running {suite_name}: {str(e)}[/red]")
        return False


def main():
    """Run all test suites."""
    console.print("[bold yellow]" + "═" * 60)
    console.print("CODE-AI-SELF-FORGED - COMPREHENSIVE TEST SUITE")
    console.print("Testing Production-Ready Problem Solving")
    console.print("═" * 60 + "[/bold yellow]\n")
    
    test_suites = [
        ("test_time_series", "Time Series Analysis"),
        ("test_data_analysis", "Data Analysis & Processing"),
        ("test_validation", "Data Validation"),
        ("test_financial", "Financial Calculations"),
        ("test_algorithms", "Algorithms & Optimization"),
        ("test_business_logic", "Business Logic"),
    ]
    
    results = []
    
    for module_name, suite_name in test_suites:
        success = run_test_suite(module_name, suite_name)
        results.append((suite_name, success))
    
    # Final summary
    console.print("\n\n[bold yellow]" + "═" * 60)
    console.print("OVERALL TEST SUMMARY")
    console.print("═" * 60 + "[/bold yellow]\n")
    
    passed_suites = sum(1 for _, success in results if success)
    total_suites = len(results)
    
    for suite_name, success in results:
        status = "[green]✓ PASSED[/green]" if success else "[red]✗ FAILED[/red]"
        console.print(f"{suite_name}: {status}")
    
    console.print(f"\n[bold]Test Suites: {passed_suites}/{total_suites} passed[/bold]")
    
    if passed_suites == total_suites:
        console.print(Panel(
            "[bold green]🎉 ALL TEST SUITES PASSED! 🎉[/bold green]\n\n"
            "Code-AI-Self-Forged successfully solved production-ready problems across:\n"
            "• Time Series Analysis\n"
            "• Data Analysis & Processing\n"
            "• Data Validation\n"
            "• Financial Calculations\n"
            "• Algorithms & Optimization\n"
            "• Business Logic\n\n"
            "The agent is ready for real-world autonomous problem solving!",
            title="Success",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[bold yellow]⚠️  {total_suites - passed_suites} test suite(s) failed[/bold yellow]\n\n"
            "Review logs above for details on failed tests.",
            title="Partial Success",
            border_style="yellow",
        ))


if __name__ == "__main__":
    main()
