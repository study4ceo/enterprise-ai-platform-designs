"""Reasoning agent using LLM."""

from typing import List, Dict, Optional

from config import settings
from logger import get_logger
from code_executor import CodeExecutor, ExecutionResult

logger = get_logger(__name__)


class Message:
    """Conversation message."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}


class ReasoningAgent:
    """AI agent that reasons and writes code."""

    SYSTEM_PROMPT = """You are an autonomous AI agent that thinks and writes code.

Your capabilities:
- Analyze problems and break them down into steps
- Write Python code to solve problems
- Execute code and interpret results
- Learn from errors and iterate
- Explain your reasoning process

Guidelines:
- Think step-by-step before writing code
- Write clean, well-commented code
- Handle errors gracefully
- Always return code in markdown code blocks with ```python
- Explain what your code does
- If execution fails, analyze the error and try again

You have access to standard Python libraries. File operations are restricted in this environment.
"""

    def __init__(self, executor: Optional[CodeExecutor] = None):
        """Initialize reasoning agent.
        
        Args:
            executor: Code executor instance
        """
        # Initialize LLM client based on provider
        if settings.llm_provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model_name = settings.model_name
        elif settings.llm_provider == "groq":
            # Groq uses OpenAI-compatible API
            from openai import OpenAI
            self.client = OpenAI(
                base_url=settings.groq_base_url,
                api_key=settings.groq_api_key
            )
            self.model_name = settings.groq_model
        elif settings.llm_provider == "ollama":
            # Ollama uses OpenAI-compatible API
            from openai import OpenAI
            self.client = OpenAI(
                base_url=settings.ollama_base_url,
                api_key="not-needed"  # Ollama doesn't need API key
            )
            self.model_name = settings.ollama_model
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
        
        self.executor = executor or CodeExecutor()
        self.conversation: List[Message] = []
        
        logger.info("ReasoningAgent initialized", provider=settings.llm_provider, model=self.model_name)

    def think(self, user_input: str) -> str:
        """Process user input and generate response.
        
        Args:
            user_input: User's question or task
            
        Returns:
            Agent's response
        """
        logger.info("Agent thinking", input=user_input)

        # Add user message
        self.conversation.append(Message("user", user_input))

        # Get LLM response
        response = self._call_llm()
        
        # Add assistant message
        self.conversation.append(Message("assistant", response))

        logger.info("Agent responded", response_length=len(response))
        return response

    def execute_code(self, code: str) -> ExecutionResult:
        """Execute code and return result.
        
        Args:
            code: Python code to execute
            
        Returns:
            ExecutionResult
        """
        logger.info("Executing code")
        result = self.executor.execute(code)
        
        # Add execution result to conversation
        result_msg = f"Execution result:\n{result}"
        self.conversation.append(Message("user", result_msg))
        
        return result

    def solve(self, problem: str, max_iterations: int = 3) -> Dict:
        """Solve a problem autonomously.
        
        Args:
            problem: Problem description
            max_iterations: Maximum solution attempts
            
        Returns:
            Dict with solution details
        """
        logger.info("Starting autonomous solve", problem=problem)

        # Initial thinking
        response = self.think(problem)

        for iteration in range(max_iterations):
            logger.info("Iteration", number=iteration + 1)

            # Check if response contains code
            if "```python" in response or "```\n" in response:
                # Extract and execute code
                result = self.execute_code(response)

                if result.success:
                    logger.info("Solution successful")
                    return {
                        "success": True,
                        "iterations": iteration + 1,
                        "code": response,
                        "output": result.output,
                        "conversation": self.conversation,
                    }
                else:
                    # Failed, ask agent to fix
                    logger.warning("Execution failed, asking agent to fix")
                    response = self.think(
                        "The code failed. Please analyze the error and provide a corrected version."
                    )
            else:
                # No code yet, ask for implementation
                logger.info("No code found, requesting implementation")
                response = self.think(
                    "Please provide the Python code implementation for this solution."
                )

        logger.error("Max iterations reached without success")
        return {
            "success": False,
            "iterations": max_iterations,
            "message": "Could not solve problem within max iterations",
            "conversation": self.conversation,
        }

    def _call_llm(self) -> str:
        """Call LLM API.
        
        Returns:
            LLM response text
        """
        try:
            if settings.llm_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=settings.max_tokens,
                    temperature=settings.temperature,
                    system=self.SYSTEM_PROMPT,
                    messages=[msg.to_dict() for msg in self.conversation],
                )
                return response.content[0].text
            
            elif settings.llm_provider == "ollama":
                # Ollama uses OpenAI-compatible chat completion
                messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
                messages.extend([msg.to_dict() for msg in self.conversation])
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error("LLM API error", error=str(e))
            raise

    def reset(self):
        """Reset conversation history."""
        self.conversation = []
        logger.info("Conversation reset")
