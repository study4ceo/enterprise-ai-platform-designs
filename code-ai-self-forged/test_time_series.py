"""Test time series problems with the AI agent."""

from reasoning_agent import ReasoningAgent
from logger import setup_logging, get_logger
from rich.console import Console
from rich.panel import Panel

setup_logging()
logger = get_logger(__name__)
console = Console()


def test_moving_averages():
    """Test moving average calculation."""
    console.print("\n[bold cyan]TEST 1: Moving Averages[/bold cyan]\n")
    
    problem = """
Given this daily sales data (in USD), calculate:
1. 7-day moving average
2. 30-day moving average  
3. Identify the trend direction (up/down/flat)
4. Detect any crossover points between the two averages

Sales data (60 days):
[120, 135, 142, 128, 155, 148, 162, 158, 145, 172, 168, 175, 182, 178, 185,
 192, 188, 195, 202, 198, 205, 212, 208, 215, 222, 218, 225, 232, 228, 235,
 242, 238, 245, 252, 248, 255, 262, 258, 265, 272, 268, 275, 282, 278, 285,
 292, 288, 295, 302, 298, 305, 312, 308, 315, 322, 318, 325, 332, 328, 335]

Show the last 10 days with their 7-day and 30-day moving averages.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Moving Averages Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_anomaly_detection():
    """Test anomaly detection."""
    console.print("\n[bold cyan]TEST 2: Anomaly Detection[/bold cyan]\n")
    
    problem = """
Given this server response time data (in milliseconds), identify anomalies:
1. Calculate mean and standard deviation
2. Identify outliers (values > 2 standard deviations from mean)
3. Flag suspicious data points with their indices
4. Provide statistical summary (min, max, mean, median, std)

Response times (50 measurements):
[45, 52, 48, 51, 49, 47, 53, 50, 46, 51,
 48, 52, 49, 47, 250, 51, 50, 48, 52, 49,
 47, 51, 50, 48, 320, 52, 49, 47, 51, 50,
 48, 52, 49, 47, 51, 50, 48, 52, 49, 47,
 51, 50, 180, 52, 49, 47, 51, 50, 48, 52]

Highlight the anomalies and explain why they're concerning.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Anomaly Detection Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_seasonal_patterns():
    """Test seasonal pattern detection."""
    console.print("\n[bold cyan]TEST 3: Seasonal Pattern Detection[/bold cyan]\n")
    
    problem = """
Given monthly sales data over 3 years, identify seasonal patterns:
1. Calculate average sales for each month across all years
2. Identify peak months and low months
3. Calculate seasonality index for each month (month_avg / overall_avg * 100)
4. Predict next 3 months based on seasonal pattern

Monthly sales data (36 months - 3 years):
Year 1: [85, 78, 92, 105, 118, 142, 165, 158, 128, 95, 88, 165]
Year 2: [90, 82, 98, 112, 125, 148, 172, 165, 135, 102, 95, 172]
Year 3: [95, 88, 105, 118, 132, 155, 178, 172, 142, 108, 102, 178]

Show:
- Monthly averages across years
- Peak season months
- Low season months  
- Seasonality indices
- Predictions for next Jan, Feb, Mar
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Seasonal Pattern Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_combined_analysis():
    """Test combined time series analysis."""
    console.print("\n[bold cyan]TEST 4: Combined Time Series Analysis[/bold cyan]\n")
    
    problem = """
Given daily website traffic data for 90 days, perform comprehensive analysis:
1. Calculate 7-day and 30-day moving averages
2. Detect anomalies (outliers > 2 std deviations)
3. Identify weekly patterns (which days have highest/lowest traffic)
4. Calculate week-over-week growth rate
5. Provide actionable insights

Daily visitors (90 days):
[1250, 1180, 1220, 1280, 1350, 1420, 1380, 1290, 1210, 1240,
 1300, 1370, 1440, 1400, 1310, 1230, 1260, 1320, 1390, 1460,
 1420, 1330, 1250, 1280, 1340, 1410, 1480, 1440, 1350, 1270,
 1300, 1360, 1430, 1500, 1460, 1370, 1290, 1320, 1380, 1450,
 2100, 1480, 1390, 1310, 1340, 1400, 1470, 1540, 1500, 1410,
 1330, 1360, 1420, 1490, 1560, 1520, 1430, 1350, 1380, 1440,
 1510, 1580, 1540, 1450, 1370, 1400, 1460, 1530, 1600, 1560,
 1470, 1390, 1420, 1480, 1550, 1620, 1580, 1490, 1410, 1440,
 1500, 1570, 1640, 1600, 1510, 1430, 1460, 1520, 1590, 1660]

Provide a complete time series analysis report.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Combined Analysis Result",
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
    """Run all time series tests."""
    console.print("[bold yellow]═" * 40)
    console.print("TIME SERIES ANALYSIS TEST SUITE")
    console.print("Testing Code-AI-Self-Forged")
    console.print("═" * 40 + "[/bold yellow]\n")
    
    results = []
    
    # Run tests
    results.append(("Moving Averages", test_moving_averages()))
    results.append(("Anomaly Detection", test_anomaly_detection()))
    results.append(("Seasonal Patterns", test_seasonal_patterns()))
    results.append(("Combined Analysis", test_combined_analysis()))
    
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
        console.print("\n[bold green]🎉 All tests passed! Agent is production-ready for time series analysis.[/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠️  {total - passed} test(s) failed. Review logs for details.[/bold yellow]")


if __name__ == "__main__":
    main()
