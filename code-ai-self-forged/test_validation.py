"""Test data validation problems with the AI agent."""

from reasoning_agent import ReasoningAgent
from logger import setup_logging, get_logger
from rich.console import Console
from rich.panel import Panel

setup_logging()
logger = get_logger(__name__)
console = Console()


def test_email_validator():
    """Test email validation."""
    console.print("\n[bold cyan]TEST 1: Email Validator[/bold cyan]\n")
    
    problem = """
Validate these email addresses and provide:
1. Basic format validation (regex)
2. Identify valid vs invalid emails
3. Categorize by domain type (free email like gmail/yahoo, corporate, custom)
4. Flag suspicious patterns
5. Generate validation report

Email addresses:
john.doe@company.com
jane_smith@gmail.com
invalid.email@
bob@test
alice.brown@corporate-site.co.uk
charlie@yahoo.com
admin@
test@domain..com
user123@outlook.com
support@my-company.io

Provide detailed validation results for each email.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Email Validation Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_credit_card_validator():
    """Test credit card validation with Luhn algorithm."""
    console.print("\n[bold cyan]TEST 2: Credit Card Validator (Luhn Algorithm)[/bold cyan]\n")
    
    problem = """
Validate credit card numbers using the Luhn algorithm:
1. Validate each number with Luhn algorithm
2. Identify card type (Visa starts with 4, Mastercard starts with 51-55, Amex starts with 34/37)
3. Mask all but last 4 digits
4. Report valid/invalid with reasoning

Credit card numbers:
4532015112830366
5425233430109903
374245455400126
6011000990139424
4532015112830367
5425233430109904
123456789012345
4111111111111111
5105105105105100

Provide validation results with card type identification.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Credit Card Validation Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_password_strength():
    """Test password strength checker."""
    console.print("\n[bold cyan]TEST 3: Password Strength Checker[/bold cyan]\n")
    
    problem = """
Evaluate password strength and provide feedback:
1. Check length (min 8 characters)
2. Check complexity (uppercase, lowercase, numbers, special chars)
3. Detect common patterns (123, abc, qwerty, password, admin)
4. Calculate strength score (0-100)
5. Provide specific improvement suggestions

Passwords to check:
Password123
Str0ng!P@ssw0rd2026
12345678
qwerty
MyP@ssw0rd
admin123
Secure#Pass99
abc123ABC
ThisIsAVeryLongButWeakPassword
P@55w0rd!

Rate each password and provide recommendations.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Password Strength Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Failed[/red]\n\n{result.get('message', 'Unknown error')}",
            title="Failed",
            border_style="red",
        ))
    
    return result["success"]


def test_phone_number_validator():
    """Test phone number validation."""
    console.print("\n[bold cyan]TEST 4: Phone Number Validator[/bold cyan]\n")
    
    problem = """
Validate and format phone numbers:
1. Identify valid vs invalid numbers
2. Standardize to format: (XXX) XXX-XXXX for US numbers
3. Handle different input formats
4. Extract country codes if present
5. Report validation results

Phone numbers:
555-1234-5678
(555) 123-4567
5551234567
+1 555 987 6543
123-456-7890
555.123.4567
+44 20 7946 0958
555-12-345
(555)1234567
+1-555-234-5678

Format valid US numbers and flag invalid ones.
"""
    
    agent = ReasoningAgent()
    result = agent.solve(problem, max_iterations=3)
    
    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"{result['output']}",
            title="Phone Validation Result",
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
    """Run all validation tests."""
    console.print("[bold yellow]═" * 40)
    console.print("DATA VALIDATION TEST SUITE")
    console.print("Testing Code-AI-Self-Forged")
    console.print("═" * 40 + "[/bold yellow]\n")
    
    results = []
    
    # Run tests
    results.append(("Email Validator", test_email_validator()))
    results.append(("Credit Card Validator", test_credit_card_validator()))
    results.append(("Password Strength", test_password_strength()))
    results.append(("Phone Number Validator", test_phone_number_validator()))
    
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
