"""Main entry point for Code-AI-Self-Forged."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from logger import setup_logging, get_logger
from reasoning_agent import ReasoningAgent

setup_logging()
logger = get_logger(__name__)
console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║   CODE-AI-SELF-FORGED                     ║
    ║   Autonomous AI Agent                     ║
    ║   Think • Write • Execute                 ║
    ╚═══════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def interactive_mode():
    """Run in interactive mode."""
    print_banner()
    console.print("\n[yellow]Interactive Mode[/yellow]")
    console.print("Ask me to solve problems and I'll write and execute code.\n")
    console.print("Commands:")
    console.print("  - Type your problem or question")
    console.print("  - 'reset' - Clear conversation")
    console.print("  - 'exit' or 'quit' - Exit\n")

    agent = ReasoningAgent()

    while True:
        try:
            # Get user input
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["exit", "quit"]:
                console.print("\n[yellow]Goodbye![/yellow]")
                break

            if user_input.lower() == "reset":
                agent.reset()
                console.print("[yellow]Conversation reset[/yellow]\n")
                continue

            # Process input
            console.print("\n[bold cyan]Agent:[/bold cyan]")
            
            # Ask if autonomous solve or just chat
            if "solve" in user_input.lower() or "write code" in user_input.lower():
                # Autonomous solve
                result = agent.solve(user_input)
                
                if result["success"]:
                    console.print(Panel(
                        f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
                        f"Output:\n{result['output']}",
                        title="Success",
                        border_style="green",
                    ))
                else:
                    console.print(Panel(
                        f"[red]✗ Could not solve[/red]\n\n{result['message']}",
                        title="Failed",
                        border_style="red",
                    ))
            else:
                # Just chat
                response = agent.think(user_input)
                console.print(Markdown(response))

            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]\n")
        except Exception as e:
            logger.error("Error in interactive mode", error=str(e))
            console.print(f"\n[red]Error: {str(e)}[/red]\n")


def solve_problem(problem: str):
    """Solve a single problem and exit.
    
    Args:
        problem: Problem description
    """
    print_banner()
    console.print(f"\n[yellow]Problem:[/yellow] {problem}\n")

    agent = ReasoningAgent()
    result = agent.solve(problem)

    if result["success"]:
        console.print(Panel(
            f"[green]✓ Solved in {result['iterations']} iteration(s)[/green]\n\n"
            f"Output:\n{result['output']}",
            title="Success",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]✗ Could not solve[/red]\n\n{result['message']}",
            title="Failed",
            border_style="red",
        ))


def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Command line mode
        problem = " ".join(sys.argv[1:])
        solve_problem(problem)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
