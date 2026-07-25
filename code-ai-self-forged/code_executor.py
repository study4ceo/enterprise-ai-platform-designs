"""Code execution engine."""

import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from config import settings
from logger import get_logger
from code_validator import CodeValidator

logger = get_logger(__name__)


class ExecutionResult:
    """Result of code execution."""

    def __init__(
        self,
        success: bool,
        output: str = "",
        error: str = "",
        return_value: Optional[any] = None,
        execution_time: float = 0.0,
    ):
        self.success = success
        self.output = output
        self.error = error
        self.return_value = return_value
        self.execution_time = execution_time

    def __str__(self) -> str:
        if self.success:
            return f"✓ Success\nOutput: {self.output}"
        else:
            return f"✗ Failed\nError: {self.error}"


class CodeExecutor:
    """Executes Python code safely."""

    def __init__(self, validator: Optional[CodeValidator] = None):
        """Initialize executor.
        
        Args:
            validator: Code validator instance
        """
        self.validator = validator or CodeValidator()

    def execute(self, code: str) -> ExecutionResult:
        """Execute Python code.
        
        Args:
            code: Python code to execute
            
        Returns:
            ExecutionResult with output and status
        """
        import time

        start_time = time.time()

        # Extract code from markdown if present
        code = self.validator.extract_code_from_markdown(code)

        # Validate code
        is_valid, issues = self.validator.validate(code)
        if not is_valid:
            logger.error("Code validation failed", issues=issues)
            return ExecutionResult(
                success=False,
                error=f"Validation failed: {', '.join(issues)}",
                execution_time=time.time() - start_time,
            )

        # Execute in subprocess for safety
        try:
            result = self._execute_in_subprocess(code)
            execution_time = time.time() - start_time
            
            logger.info(
                "Code executed",
                success=result.success,
                execution_time=execution_time,
            )
            
            result.execution_time = execution_time
            return result

        except Exception as e:
            logger.error("Execution error", error=str(e))
            return ExecutionResult(
                success=False,
                error=f"Execution error: {str(e)}",
                execution_time=time.time() - start_time,
            )

    def _execute_in_subprocess(self, code: str) -> ExecutionResult:
        """Execute code in a subprocess.
        
        Args:
            code: Python code to execute
            
        Returns:
            ExecutionResult
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            dir=settings.workspace_dir,
        ) as f:
            f.write(code)
            temp_file = Path(f.name)

        try:
            # Execute with timeout
            result = subprocess.run(
                [sys.executable, str(temp_file)],
                capture_output=True,
                text=True,
                timeout=settings.execution_timeout,
                cwd=settings.workspace_dir,
            )

            if result.returncode == 0:
                return ExecutionResult(
                    success=True,
                    output=result.stdout,
                    error=result.stderr,
                )
            else:
                return ExecutionResult(
                    success=False,
                    output=result.stdout,
                    error=result.stderr or f"Exit code: {result.returncode}",
                )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Execution timeout after {settings.execution_timeout}s",
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Subprocess error: {str(e)}",
            )
        finally:
            # Clean up temp file
            try:
                temp_file.unlink()
            except Exception:
                pass
